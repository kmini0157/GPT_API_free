#!/usr/bin/env python3
"""ChatAnywhere API 대화형 채팅 CLI.

사용법:
    pip install openai
    export OPENAI_API_KEY="발급받은_KEY"    (Windows PowerShell: $env:OPENAI_API_KEY="...")
    python chat.py

옵션:
    python chat.py --model gpt-5-mini
    python chat.py --system "당신은 친절한 코딩 튜터입니다."
    python chat.py --base-url https://api.chatanywhere.tech/v1

채팅 중 명령어:
    /new            대화 기록 초기화
    /model 모델명    사용 모델 변경
    /help           도움말
    /exit           종료
"""

import argparse
import os
import sys

try:
    from openai import OpenAI
except ImportError:
    sys.exit("openai 패키지가 필요합니다. 먼저 실행하세요:  pip install openai")

DEFAULT_BASE_URL = "https://api.chatanywhere.org/v1"
DEFAULT_MODEL = "gpt-4o-mini"

HELP_TEXT = """\
명령어:
  /new            대화 기록 초기화 (새 대화 시작)
  /model 모델명    사용 모델 변경 (예: /model deepseek-r1)
  /help           이 도움말 표시
  /exit           종료

무료 Key 하루 한도 참고:
  200회  gpt-4o-mini, gpt-4.1-mini, gpt-4.1-nano, gpt-5-mini, gpt-5-nano, gpt-3.5-turbo
   30회  deepseek-r1, deepseek-v3, deepseek-v3-2-exp
    5회  gpt-5, gpt-4o, gpt-4.1
"""


def parse_args():
    parser = argparse.ArgumentParser(
        description="ChatAnywhere API 대화형 채팅 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=HELP_TEXT,
    )
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
        "--model",
        default=os.environ.get("CHATANYWHERE_MODEL", DEFAULT_MODEL),
        help=f"사용할 모델 (기본값: {DEFAULT_MODEL})",
    )
    parser.add_argument("--system", default=None, help="시스템 프롬프트")
    return parser.parse_args()


def chat_stream(client, model, messages):
    """스트리밍으로 응답을 출력하고 전체 응답 텍스트를 반환한다."""
    stream = client.chat.completions.create(model=model, messages=messages, stream=True)
    parts = []
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            text = chunk.choices[0].delta.content
            parts.append(text)
            print(text, end="", flush=True)
    print()
    return "".join(parts)


def main():
    args = parse_args()

    if not args.api_key:
        sys.exit(
            "API Key가 없습니다.\n"
            "  1) https://api.chatanywhere.tech/v1/oauth/free/render 에서 무료 Key를 발급받고\n"
            "  2) 환경변수로 설정하세요:  export OPENAI_API_KEY=\"발급받은_KEY\"\n"
            "     (또는  python chat.py --api-key 발급받은_KEY)"
        )

    client = OpenAI(api_key=args.api_key, base_url=args.base_url)
    model = args.model
    system_prompt = args.system
    messages = [{"role": "system", "content": system_prompt}] if system_prompt else []

    print(f"모델: {model} | 엔드포인트: {args.base_url}")
    print("대화를 시작하세요. 명령어는 /help, 종료는 /exit\n")

    while True:
        try:
            user_input = input("나> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n종료합니다.")
            break

        if not user_input:
            continue

        if user_input in ("/exit", "/quit"):
            print("종료합니다.")
            break
        if user_input == "/help":
            print(HELP_TEXT)
            continue
        if user_input == "/new":
            messages = [{"role": "system", "content": system_prompt}] if system_prompt else []
            print("대화 기록을 초기화했습니다.\n")
            continue
        if user_input.startswith("/model"):
            new_model = user_input[len("/model"):].strip()
            if new_model:
                model = new_model
                print(f"모델을 변경했습니다: {model}\n")
            else:
                print(f"현재 모델: {model}  (변경: /model 모델명)\n")
            continue

        messages.append({"role": "user", "content": user_input})
        print(f"\n{model}> ", end="", flush=True)
        try:
            reply = chat_stream(client, model, messages)
        except KeyboardInterrupt:
            # 응답 중 Ctrl+C → 해당 질문을 기록에서 제거하고 계속
            messages.pop()
            print("\n(응답을 중단했습니다)\n")
            continue
        except Exception as e:
            messages.pop()
            print(f"\n[오류] {e}")
            print("한도 초과(429)라면 /model 로 다른 모델로 바꾸거나 내일 다시 시도하세요.")
            print("서비스 상태 확인: https://status.chatanywhere.tech/\n")
            continue

        messages.append({"role": "assistant", "content": reply})
        print()


if __name__ == "__main__":
    main()
