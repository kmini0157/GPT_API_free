"""숏폼 영상화 — 썸네일 + 내레이션 음성을 9:16 mp4 로 합성한다(ffmpeg).

ffmpeg/ffprobe 가 PATH 에 없으면 건너뛴다(graceful). GitHub ubuntu 러너에는
ffmpeg 가 기본 설치돼 있어 워크플로우에서 그대로 동작한다.
"""
import shutil
import subprocess


def _has_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None


def make_short(image_path, audio_path, out_path, width=1080, height=1920) -> bool:
    """정지 이미지(썸네일)를 세로 캔버스로 채우고 내레이션을 입혀 mp4 생성.

    오디오 길이에 맞춰 자동 종료(-shortest). 이미지나 오디오가 없으면 False.
    """
    if not _has_ffmpeg():
        print("  ⚠ ffmpeg 미설치 — 숏폼 생성 건너뜀 (`apt install ffmpeg`)")
        return False
    if not (image_path.exists() and audio_path.exists()):
        print("  ⚠ 썸네일/음성이 없어 숏폼 생성 불가")
        return False

    # 이미지를 9:16 캔버스에 꽉 차게(crop) + x264 인코딩 + AAC 오디오
    vf = (
        f"scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},format=yuv420p"
    )
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(image_path),
        "-i", str(audio_path),
        "-vf", vf,
        "-c:v", "libx264", "-tune", "stillimage", "-preset", "veryfast",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(out_path),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as exc:
        print(f"  ⚠ 숏폼 생성 실패(무시하고 진행): {exc.stderr.decode()[-200:]}")
        return False
    return True
