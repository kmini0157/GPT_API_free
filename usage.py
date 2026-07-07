#!/usr/bin/env python3
"""ChatAnywhere 사용량 확인 CLI — 오늘 몇 회 썼는지, 무료 한도가 얼마나 남았는지.

사용법:
    python usage.py            # 오늘 사용량 + 남은 한도 추정 (로컬 기록 기준)
    python usage.py --week     # 최근 7일 사용량
    python usage.py --remote   # 서버에서 잔액·최근 24시간 사용량 조회 (전체 앱 사용분 포함)
    python usage.py --check    # API Key가 살아있는지 확인 (모델 목록 조회)

기본 표시는 chat.py / ask.py 가 ~/.chatanywhere/usage.json 에 기록한 로컬 카운트입니다.
브라우저 확장 등 다른 앱에서 쓴 횟수까지 보려면 --remote 를 쓰세요
(공식 잔액 조회 페이지 https://api.chatanywhere.tech/ 와 같은 API를 호출합니다).
"""

import argparse
import datetime
import json
import os
import sys
import urllib.error
import urllib.request

USAGE_FILE = os.path.join(os.path.expanduser("~"), ".chatanywhere", "usage.json")
DEFAULT_BASE_URL = "https://api.chatanywhere.org/v1"

# 무료 Key 하루 한도 (모델별) — 출처: README.ko.md
FREE_LIMITS = [
    (200, ["gpt-4o-mini", "gpt-4.1-mini", "gpt-4.1-nano", "gpt-5-mini", "gpt-5-nano", "gpt-3.5-turbo"]),
    (30, ["deepseek-r1", "deepseek-v3", "deepseek-v3-2-exp"]),
    (5, ["gpt-5", "gpt-4o", "gpt-4.1"]),
]


def limit_for(model):
    for limit, models in FREE_LIMITS:
        if model in models:
            return limit
    return None


def load_usage():
    try:
        with open(USAGE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def show_today(data):
    today = datetime.date.today().isoformat()
    counts = data.get(today, {})
    print(f"■ 오늘({today}) 사용량 — 이 컴퓨터의 chat.py/ask.py 기준\n")
    if not counts:
        print("  기록 없음\n")
    else:
        total = 0
        for model, count in sorted(counts.items(), key=lambda x: -x[1]):
            limit = limit_for(model)
            remain = f"(무료 한도 {limit}회 중 약 {max(limit - count, 0)}회 남음)" if limit else ""
            print(f"  {model:<20} {count:>4}회  {remain}")
            total += count
        print(f"  {'합계':<20} {total:>4}회  (무료 Key 전체 한도: 200회/일)\n")
    print("무료 Key 하루 한도:")
    for limit, models in FREE_LIMITS:
        print(f"  {limit:>3}회/일  {', '.join(models)}")
    print("\n전체 기록·잔액 조회(다른 앱 사용분 포함): python usage.py --remote")


def show_week(data):
    print("■ 최근 7일 사용량 — 이 컴퓨터의 chat.py/ask.py 기준\n")
    today = datetime.date.today()
    any_row = False
    for i in range(6, -1, -1):
        day = (today - datetime.timedelta(days=i)).isoformat()
        counts = data.get(day, {})
        total = sum(counts.values())
        if counts:
            any_row = True
            detail = ", ".join(f"{m} {c}회" for m, c in sorted(counts.items(), key=lambda x: -x[1]))
            print(f"  {day}  {total:>4}회  ({detail})")
        else:
            print(f"  {day}     0회")
    if not any_row:
        print("\n  아직 기록이 없습니다. chat.py 나 ask.py 를 쓰면 자동으로 기록됩니다.")


def get_api_key():
    api_key = os.environ.get("CHATANYWHERE_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        sys.exit(
            "API Key가 없습니다. 환경변수로 설정하세요:  export OPENAI_API_KEY=\"발급받은_KEY\""
        )
    return api_key


def query_endpoint(path, body, api_key):
    """ChatAnywhere 조회용 API 호출. 주의: Bearer 없이 Key를 그대로 넣는다."""
    base = os.environ.get("CHATANYWHERE_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    if not base.endswith("/v1"):
        base += "/v1"
    req = urllib.request.Request(
        f"{base}/query/{path}",
        data=json.dumps(body).encode() if body is not None else b"",
        headers={"Authorization": api_key, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())


def show_remote():
    """서버에 잔액과 최근 24시간 사용량을 조회한다 (채팅 한도를 소모하지 않음)."""
    api_key = get_api_key()
    print("■ 서버 조회 — 모든 앱에서의 사용량 포함\n")
    try:
        balance = query_endpoint("balance", None, api_key)
    except urllib.error.HTTPError as e:
        print(f"❌ 잔액 조회 실패 (HTTP {e.code}): {e.read().decode(errors='replace')[:200]}")
        print("Key가 잘못됐거나 조회 API가 변경됐을 수 있습니다.")
        print("웹에서 직접 확인: https://api.chatanywhere.tech/")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 잔액 조회 실패: {e}")
        print("네트워크 문제일 수 있습니다. 웹에서 직접 확인: https://api.chatanywhere.tech/")
        sys.exit(1)

    total = balance.get("balanceTotal", 0) or 0
    used = balance.get("balanceUsed", 0) or 0
    if total == 0:
        print("  Key 종류: 무료 Key (횟수 제한제)")
        print(f"  누적 사용액 환산: ${used:.4f}")
    else:
        print("  Key 종류: 유료 Key")
        print(f"  잔액: ${total - used:.4f}  (충전 ${total:.2f} 중 ${used:.4f} 사용)")

    try:
        # model="%" → 모든 모델, 최근 24시간의 시간대별 사용량
        hourly = query_endpoint("usage_details", {"model": "%", "hours": 24}, api_key)
        requests_24h = sum(row.get("count", 0) for row in hourly)
        tokens_24h = sum(row.get("totalTokens", 0) for row in hourly)
        print(f"\n  최근 24시간: 요청 {requests_24h}회, 토큰 {tokens_24h:,}개")
        print("  (무료 Key 전체 한도: 200요청/일 — 브라우저 확장 등 모든 앱 합산)")
    except Exception as e:
        print(f"\n  최근 24시간 사용량 조회 실패: {e}")

    print("\n상세 기록·공지: https://api.chatanywhere.tech/")


def check_key():
    """모델 목록 조회로 Key가 유효한지 확인한다 (채팅 한도를 소모하지 않음)."""
    try:
        from openai import OpenAI
    except ImportError:
        sys.exit("openai 패키지가 필요합니다. 먼저 실행하세요:  pip install openai")

    api_key = get_api_key()
    base_url = os.environ.get("CHATANYWHERE_BASE_URL", DEFAULT_BASE_URL)
    print(f"엔드포인트: {base_url}")
    try:
        models = [m.id for m in OpenAI(api_key=api_key, base_url=base_url).models.list()]
    except Exception as e:
        print(f"❌ Key 확인 실패: {e}")
        print("서비스 상태 확인: https://status.chatanywhere.tech/")
        sys.exit(1)
    print(f"✅ Key 정상 — 사용 가능한 모델 {len(models)}개")
    free_defaults = [m for m in models if m in ("gpt-4o-mini", "gpt-5-mini", "deepseek-r1")]
    if free_defaults:
        print(f"   주요 모델 확인됨: {', '.join(free_defaults)}")


def main():
    parser = argparse.ArgumentParser(description="ChatAnywhere 사용량 확인 CLI")
    parser.add_argument("--week", action="store_true", help="최근 7일 사용량 보기")
    parser.add_argument("--remote", action="store_true", help="서버에서 잔액·최근 24시간 사용량 조회")
    parser.add_argument("--check", action="store_true", help="API Key 유효성 확인 (모델 목록 조회)")
    args = parser.parse_args()

    if args.remote:
        show_remote()
        return
    if args.check:
        check_key()
        return

    data = load_usage()
    if args.week:
        show_week(data)
    else:
        show_today(data)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        # 출력 파이프가 먼저 닫힌 경우 (예: ... | head) — 정상 종료 처리
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(0)
