"""YouTube Shorts 업로더 — Data API v3 resumable upload(의존성: httpx).

필요 자격증명(환경변수):
  YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN
refresh token 발급은 README의 'YouTube 자동 업로드 준비' 참고.
무료 쿼터 10,000 units/day, 업로드 1건 ~1,600 units → 하루 약 6건.
"""
import os

import httpx

TOKEN_URL = "https://oauth2.googleapis.com/token"
UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos"


def is_configured() -> bool:
    return all(os.getenv(k) for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"))


def _access_token() -> str:
    resp = httpx.post(
        TOKEN_URL,
        data={
            "client_id": os.getenv("YT_CLIENT_ID"),
            "client_secret": os.getenv("YT_CLIENT_SECRET"),
            "refresh_token": os.getenv("YT_REFRESH_TOKEN"),
            "grant_type": "refresh_token",
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def upload_short(video_path, title: str, description: str, tags=None) -> str:
    """숏폼 mp4 업로드. 성공 시 video_id, 실패 시 None 반환."""
    if not is_configured():
        return None
    try:
        token = _access_token()
        meta = {
            "snippet": {
                "title": title[:100],
                "description": description[:4900],
                "tags": (tags or [])[:15],
                "categoryId": "22",  # People & Blogs
            },
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False},
        }
        data = video_path.read_bytes()
        # 1) resumable 세션 시작
        init = httpx.post(
            UPLOAD_URL,
            params={"uploadType": "resumable", "part": "snippet,status"},
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json; charset=UTF-8",
                "X-Upload-Content-Type": "video/*",
                "X-Upload-Content-Length": str(len(data)),
            },
            json=meta,
            timeout=30,
        )
        init.raise_for_status()
        session_url = init.headers["Location"]
        # 2) 바이트 업로드
        put = httpx.put(
            session_url,
            content=data,
            headers={"Content-Type": "video/*"},
            timeout=300,
        )
        put.raise_for_status()
        return put.json().get("id")
    except Exception as exc:
        print(f"  ⚠ YouTube 업로드 실패: {exc}")
        return None
