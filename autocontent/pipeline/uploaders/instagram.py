"""Instagram Reels 업로더 — Graph API(의존성: httpx).

필요 자격증명(환경변수):
  IG_USER_ID, IG_ACCESS_TOKEN (장기 토큰), SITE_BASE_URL (공개 mp4 호스트)
Graph API는 video_url로 '공개 접근 가능한' mp4 URL을 요구한다 →
Cloudflare Pages 배포본(SITE_BASE_URL/<slug>/short.mp4)을 그대로 사용한다.
"""
import os
import time

import httpx

GRAPH = "https://graph.facebook.com/v21.0"


def is_configured() -> bool:
    return all(os.getenv(k) for k in ("IG_USER_ID", "IG_ACCESS_TOKEN", "SITE_BASE_URL"))


def publish_reel(video_url: str, caption: str, poll_timeout: int = 180) -> str:
    """공개 mp4 URL을 릴스로 게시. 성공 시 media_id, 실패 시 None."""
    if not is_configured():
        return None
    ig_user = os.getenv("IG_USER_ID")
    token = os.getenv("IG_ACCESS_TOKEN")
    try:
        # 1) 미디어 컨테이너 생성
        create = httpx.post(
            f"{GRAPH}/{ig_user}/media",
            data={
                "media_type": "REELS",
                "video_url": video_url,
                "caption": caption[:2200],
                "access_token": token,
            },
            timeout=60,
        )
        create.raise_for_status()
        creation_id = create.json()["id"]

        # 2) 처리 완료까지 폴링(Instagram이 원격 mp4를 받아 인코딩)
        deadline = time.time() + poll_timeout
        while time.time() < deadline:
            status = httpx.get(
                f"{GRAPH}/{creation_id}",
                params={"fields": "status_code", "access_token": token},
                timeout=30,
            ).json()
            code = status.get("status_code")
            if code == "FINISHED":
                break
            if code == "ERROR":
                print("  ⚠ Instagram 인코딩 오류")
                return None
            time.sleep(5)
        else:
            print("  ⚠ Instagram 처리 시간 초과")
            return None

        # 3) 게시
        publish = httpx.post(
            f"{GRAPH}/{ig_user}/media_publish",
            data={"creation_id": creation_id, "access_token": token},
            timeout=60,
        )
        publish.raise_for_status()
        return publish.json().get("id")
    except Exception as exc:
        print(f"  ⚠ Instagram 업로드 실패: {exc}")
        return None
