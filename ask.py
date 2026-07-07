#!/usr/bin/env python3
"""ChatAnywhere 원샷 질문 CLI — 터미널에서 한 번에 묻고 답 받기.

사용법:
    pip install openai
    export OPENAI_API_KEY="발급받은_KEY"

    python ask.py "질문"                          # 바로 질문
    cat 파일.txt | python ask.py "요약해줘"        # 파일 내용을 붙여서 질문
    git diff | python ask.py -p 커밋              # diff로 커밋 메시지 생성
    python ask.py -p 번역 "Hello, world"          # 프리셋 사용

프리셋 목록: python ask.py --list-presets
"""

import argparse
import datetime
import json
import os
import sys

try:
    from openai import OpenAI
except ImportError:
    sys.exit("openai 패키지가 필요합니다. 먼저 실행하세요:  pip install openai")

DEFAULT_BASE_URL = "https://api.chatanywhere.org/v1"
DEFAULT_MODEL = "gpt-4o-mini"
USAGE_FILE = os.path.join(os.path.expanduser("~"), ".chatanywhere", "usage.json")

# 프리셋: 자주 쓰는 작업을 시스템 프롬프트로 미리 정의
PRESETS = {
    "번역": {
        "aliases": ["tr", "translate"],
        "system": (
            "너는 전문 번역가다. 입력이 한국어면 자연스러운 영어로, "
            "다른 언어면 자연스러운 한국어로 번역해라. "
            "직역보다 의미가 통하는 자연스러운 문장을 우선하고, 번역 결과만 출력해라."
        ),
        "desc": "한국어↔영어 자동 번역",
    },
    "요약": {
        "aliases": ["sum", "summary"],
        "system": (
            "다음 내용의 핵심을 한국어로 요약해라. "
            "중요한 순서대로 불릿 목록으로 정리하고, 요약 결과만 출력해라."
        ),
        "desc": "핵심만 불릿으로 요약",
    },
    "교정": {
        "aliases": ["fix", "proofread"],
        "system": (
            "다음 글의 맞춤법, 문법, 어색한 표현을 교정해라. "
            "먼저 교정된 전체 글을 출력하고, 마지막에 '--- 바뀐 부분 ---' 아래에 "
            "주요 수정 사항을 간단히 정리해라."
        ),
        "desc": "맞춤법·문법·표현 교정",
    },
    "영작": {
        "aliases": ["en", "english"],
        "system": (
            "요청받은 내용을 자연스럽고 정중한 영어 문장으로 작성해라. "
            "이메일이면 제목(Subject)도 함께 제안해라. 영어 결과만 출력해라."
        ),
        "desc": "자연스러운 영어 문장/이메일 작성",
    },
    "설명": {
        "aliases": ["explain"],
        "system": (
            "다음 개념이나 코드를 처음 배우는 사람도 이해할 수 있게 "
            "한국어로 차근차근 설명해라. 필요하면 간단한 예시를 들어라."
        ),
        "desc": "개념/코드를 쉽게 설명",
    },
    "커밋": {
        "aliases": ["commit"],
        "system": (
            "다음 git diff를 보고 좋은 커밋 메시지를 작성해라. "
            "형식: 첫 줄은 50자 이내의 요약, 한 줄 비우고, 필요하면 본문에 이유를 서술. "
            "커밋 메시지만 출력해라."
        ),
        "desc": "git diff로 커밋 메시지 생성",
    },
}


def resolve_preset(name):
    """프리셋 이름 또는 별칭으로 프리셋을 찾는다."""
    if name in PRESETS:
        return PRESETS[name]
    for preset in PRESETS.values():
        if name in preset["aliases"]:
            return preset
    return None


def record_usage(model):
    """오늘 사용 횟수를 ~/.chatanywhere/usage.json 에 기록한다 (usage.py에서 조회)."""
    try:
        os.makedirs(os.path.dirname(USAGE_FILE), exist_ok=True)
        data = {}
        if os.path.exists(USAGE_FILE):
            with open(USAGE_FILE, encoding="utf-8") as f:
                data = json.load(f)
        today = datetime.date.today().isoformat()
        day = data.setdefault(today, {})
        day[model] = day.get(model, 0) + 1
        for old_date in sorted(data)[:-30]:  # 최근 30일만 보관
            del data[old_date]
        with open(USAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception:
        pass  # 사용량 기록 실패가 본 기능을 막으면 안 됨


def parse_args():
    preset_lines = "\n".join(
        f"  {name:<4} ({', '.join(p['aliases'])}) — {p['desc']}" for name, p in PRESETS.items()
    )
    parser = argparse.ArgumentParser(
        description="ChatAnywhere 원샷 질문 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""프리셋:
{preset_lines}

예시:
  python ask.py "파이썬에서 리스트 뒤집는 법"
  cat 기사.txt | python ask.py -p 요약
  git diff | python ask.py -p 커밋
  python ask.py -p 영작 "다음 주 회의를 금요일로 옮기자는 메일"
""",
    )
    parser.add_argument("question", nargs="*", help="질문 (생략하면 파이프 입력만 사용)")
    parser.add_argument(
        "--api-key",
        default=os.environ.get("CHATANYWHERE_API_KEY") or os.environ.get("OPENAI_API_KEY"),
        help="API Key (기본값: CHATANYWHERE_API_KEY 또는 OPENAI_API_KEY 환경변수)",
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("CHATANYWHERE_BASE_URL", DEFAULT_BASE_URL),
        help=f"API 엔드포인트 (기본값: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "-m", "--model",
        default=os.environ.get("CHATANYWHERE_MODEL", DEFAULT_MODEL),
        help=f"사용할 모델 (기본값: {DEFAULT_MODEL})",
    )
    parser.add_argument("-p", "--preset", default=None, help="프리셋 이름 (예: 번역, 요약, 커밋)")
    parser.add_argument("-s", "--system", default=None, help="시스템 프롬프트 직접 지정 (프리셋보다 우선)")
    parser.add_argument("--no-stream", action="store_true", help="스트리밍 없이 한 번에 출력")
    parser.add_argument("--list-presets", action="store_true", help="프리셋 목록 출력")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.list_presets:
        for name, p in PRESETS.items():
            print(f"{name} ({', '.join(p['aliases'])}) — {p['desc']}")
        return

    system_prompt = args.system
    if args.preset:
        preset = resolve_preset(args.preset)
        if preset is None:
            sys.exit(f"알 수 없는 프리셋: {args.preset}  (목록: python ask.py --list-presets)")
        if system_prompt is None:
            system_prompt = preset["system"]

    question = " ".join(args.question).strip()
    piped = ""
    if not sys.stdin.isatty():
        piped = sys.stdin.read().strip()

    if not question and not piped:
        sys.exit('질문이 없습니다.  예: python ask.py "질문"  또는  cat 파일 | python ask.py "요약해줘"')

    if question and piped:
        user_content = f"{question}\n\n---\n\n{piped}"
    else:
        user_content = question or piped

    if not args.api_key:
        sys.exit(
            "API Key가 없습니다.\n"
            "  1) https://api.chatanywhere.tech/v1/oauth/free/render 에서 무료 Key를 발급받고\n"
            "  2) 환경변수로 설정하세요:  export OPENAI_API_KEY=\"발급받은_KEY\""
        )

    client = OpenAI(api_key=args.api_key, base_url=args.base_url)
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_content})

    try:
        if args.no_stream:
            resp = client.chat.completions.create(model=args.model, messages=messages)
            print(resp.choices[0].message.content)
        else:
            stream = client.chat.completions.create(model=args.model, messages=messages, stream=True)
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    print(chunk.choices[0].delta.content, end="", flush=True)
            print()
    except KeyboardInterrupt:
        print("\n(중단했습니다)", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"[오류] {e}", file=sys.stderr)
        print(
            "한도 초과(429)라면 -m 으로 다른 모델을 쓰거나 내일 다시 시도하세요.\n"
            "서비스 상태 확인: https://status.chatanywhere.tech/",
            file=sys.stderr,
        )
        sys.exit(1)

    record_usage(args.model)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        # 출력 파이프가 먼저 닫힌 경우 (예: ... | head) — 정상 종료 처리
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(0)
