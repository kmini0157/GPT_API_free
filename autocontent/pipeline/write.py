"""② 작성 단계 — 무료 LLM(OpenAI 호환)으로 글·요약·이미지 프롬프트를 생성한다."""
import json

import httpx

from config import Config


def _chat(messages, temperature=0.7, max_tokens=2000) -> str:
    """OpenAI 호환 /chat/completions 호출. 무료 chatanywhere 엔드포인트 대상."""
    Config.require_llm()
    url = f"{Config.OPENAI_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {Config.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": Config.WRITER_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    with httpx.Client(timeout=120) as client:
        resp = client.post(url, headers=headers, json=payload)
        if resp.status_code != 200:
            raise SystemExit(f"LLM 호출 실패 [{resp.status_code}]: {resp.text[:300]}")
        data = resp.json()
    return data["choices"][0]["message"]["content"].strip()


def write_article(topic: str, research_text: str) -> dict:
    """주제 + 리서치 자료로 글 한 편을 만든다.

    반환: {title, body_md, summary, narration, image_prompt, tags}
    JSON 으로 받아 후속 단계(이미지·음성)가 바로 쓸 수 있게 한다.
    """
    lang = Config.OUTPUT_LANG
    sys = (
        f"너는 {lang}로 글을 쓰는 숙련된 콘텐츠 에디터다. "
        "정확하고, 군더더기 없으며, 사람이 끝까지 읽게 만드는 글을 쓴다."
    )
    research_block = research_text if research_text else "(리서치 자료 없음 — 일반 지식으로 작성)"
    user = f"""아래 주제로 블로그/뉴스레터용 글을 한 편 작성해줘.

주제: {topic}

참고 자료:
\"\"\"
{research_block}
\"\"\"

다음 JSON 형식으로만 답해(코드블록 없이 순수 JSON):
{{
  "title": "눈길을 끄는 제목",
  "body_md": "마크다운 본문. 소제목(##)으로 구조화, 800~1200자 분량",
  "summary": "3줄 요약",
  "narration": "음성으로 읽을 60~90초 분량의 자연스러운 내레이션 스크립트(마크다운 기호 없이)",
  "image_prompt": "썸네일 생성용 영어 이미지 프롬프트(구체적 장면 묘사)",
  "tags": ["태그", "3~5개"]
}}"""
    raw = _chat([{"role": "system", "content": sys}, {"role": "user", "content": user}])
    return _parse_json(raw, topic)


def _parse_json(raw: str, topic: str) -> dict:
    """LLM이 코드펜스를 둘러도 견고하게 JSON 추출."""
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip().strip("`").strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # 최후의 보루: 본문만이라도 살린다
        data = {
            "title": topic,
            "body_md": raw,
            "summary": "",
            "narration": raw[:600],
            "image_prompt": f"editorial illustration about {topic}, clean, modern",
            "tags": [topic],
        }
    data.setdefault("title", topic)
    data.setdefault("tags", [topic])
    return data
