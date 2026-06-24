"""① 리서치 단계 — Jina Reader/Search(키 없이)로 주제 관련 자료를 모은다."""
import httpx

from config import Config


def research(topic: str, max_chars: int = 6000) -> str:
    """주제를 Jina 검색에 던져 상위 결과 본문을 모아 하나의 자료 텍스트로 반환.

    Jina s.jina.ai 는 검색 결과를 LLM-friendly 한 본문 형태로 돌려준다.
    키 없이 호출 가능하며, 실패하면 빈 문자열을 돌려 파이프라인은 계속 진행한다.
    """
    url = Config.JINA_SEARCH + topic
    headers = {
        "Accept": "text/plain",
        "X-Respond-With": "no-content",  # 메타 위주로 가볍게, 너무 큰 응답 방지
    }
    try:
        with httpx.Client(timeout=60, follow_redirects=True) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            text = resp.text.strip()
    except Exception as exc:  # 네트워크/타임아웃 시 리서치 없이 진행
        print(f"  ⚠ 리서치 실패(무시하고 진행): {exc}")
        return ""

    if len(text) > max_chars:
        text = text[:max_chars] + "\n…(이하 생략)"
    return text


def read_url(url: str, max_chars: int = 8000) -> str:
    """특정 URL의 본문을 Jina Reader로 마크다운 추출."""
    try:
        with httpx.Client(timeout=60, follow_redirects=True) as client:
            resp = client.get(Config.JINA_READER + url, timeout=60)
            resp.raise_for_status()
            text = resp.text.strip()
    except Exception as exc:
        print(f"  ⚠ URL 읽기 실패: {exc}")
        return ""
    return text[:max_chars]
