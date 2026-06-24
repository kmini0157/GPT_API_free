"""③ 썸네일 단계 — Pollinations(키·가입 없이)로 이미지를 생성·저장한다."""
from urllib.parse import quote

import httpx

from config import Config


def generate_thumbnail(image_prompt: str, out_path, width: int = 1280, height: int = 720) -> bool:
    """이미지 프롬프트를 Pollinations URL로 변환해 바이트를 내려받아 저장.

    Pollinations 는 GET 요청 자체가 생성 트리거다. 실패 시 False 반환하고
    파이프라인은 이미지 없이 계속 진행한다.
    """
    url = (
        Config.POLLINATIONS
        + quote(image_prompt)
        + f"?width={width}&height={height}&nologo=true"
    )
    try:
        with httpx.Client(timeout=120, follow_redirects=True) as client:
            resp = client.get(url)
            resp.raise_for_status()
            out_path.write_bytes(resp.content)
    except Exception as exc:
        print(f"  ⚠ 썸네일 생성 실패(무시하고 진행): {exc}")
        return False
    return True
