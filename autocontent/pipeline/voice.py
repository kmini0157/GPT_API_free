"""④ 내레이션 단계 — edge-tts(키·가입 없이)로 MP3 음성을 만든다."""
import asyncio

from config import Config


def synthesize(narration: str, out_path) -> bool:
    """내레이션 스크립트를 edge-tts로 mp3 변환. 실패 시 False."""
    if not narration.strip():
        return False
    try:
        import edge_tts
    except ImportError:
        print("  ⚠ edge-tts 미설치 — `pip install edge-tts` 후 음성 생성 가능")
        return False

    async def _run():
        communicate = edge_tts.Communicate(narration, Config.TTS_VOICE)
        await communicate.save(str(out_path))

    try:
        asyncio.run(_run())
    except Exception as exc:
        print(f"  ⚠ 음성 생성 실패(무시하고 진행): {exc}")
        return False
    return True
