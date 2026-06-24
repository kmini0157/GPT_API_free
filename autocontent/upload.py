#!/usr/bin/env python3
"""자동 업로드 — content/ 의 숏폼(short.mp4)을 YouTube/Instagram에 게시한다.

자격증명이 있는 채널만 동작하고, 이미 올린 글은 meta.json의 'uploaded'로 건너뛴다.

사용:
    python upload.py                       # 미업로드분 전체, 가능한 채널 모두
    python upload.py --slug my-article     # 특정 글만
    python upload.py --platforms youtube   # 채널 지정
"""
import argparse
import json
import os
from pathlib import Path

from pipeline.uploaders import instagram, youtube


def caption_for(meta: dict) -> str:
    title = meta.get("title", "")
    summary = meta.get("summary", "")
    tags = " ".join(f"#{t}" for t in meta.get("tags", []))
    return "\n\n".join(p for p in (title, summary, tags) if p).strip()


def public_url(slug: str, asset: str) -> str:
    base = (os.getenv("SITE_BASE_URL") or "").rstrip("/")
    return f"{base}/{slug}/{asset}" if base else ""


def upload_one(folder: Path, platforms) -> dict:
    meta_path = folder / "meta.json"
    if not meta_path.exists():
        return {}
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    video = meta.get("assets", {}).get("video")
    if not video or not (folder / video).exists():
        print(f"  · {folder.name}: 숏폼 없음 — 건너뜀")
        return {}

    uploaded = meta.get("uploaded", {})
    caption = caption_for(meta)
    changed = False

    if "youtube" in platforms and "youtube" not in uploaded and youtube.is_configured():
        vid = youtube.upload_short(
            folder / video, meta.get("title", folder.name), caption, meta.get("tags")
        )
        if vid:
            uploaded["youtube"] = vid
            changed = True
            print(f"  ✓ YouTube: https://youtu.be/{vid}")

    if "instagram" in platforms and "instagram" not in uploaded and instagram.is_configured():
        url = public_url(folder.name, video)
        mid = instagram.publish_reel(url, caption)
        if mid:
            uploaded["instagram"] = mid
            changed = True
            print(f"  ✓ Instagram media: {mid}")

    if changed:
        meta["uploaded"] = uploaded
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return uploaded


def main():
    p = argparse.ArgumentParser(description="숏폼 자동 업로드(YouTube/Instagram)")
    p.add_argument("--content", default="content", help="콘텐츠 폴더 (기본: content)")
    p.add_argument("--slug", help="특정 글 슬러그만 업로드")
    p.add_argument("--platforms", default="youtube,instagram", help="대상 채널(쉼표)")
    args = p.parse_args()

    platforms = {x.strip() for x in args.platforms.split(",") if x.strip()}
    base = Path(args.content)

    configured = []
    if youtube.is_configured():
        configured.append("youtube")
    if instagram.is_configured():
        configured.append("instagram")
    if not configured:
        print("업로드 자격증명이 없습니다 — 건너뜀(YouTube/Instagram 시크릿 미설정).")
        return
    print(f"활성 채널: {', '.join(configured)}")

    folders = [base / args.slug] if args.slug else sorted(
        d for d in base.glob("*") if d.is_dir() and not d.name.startswith(".")
    )
    for folder in folders:
        if folder.exists():
            upload_one(folder, platforms)


if __name__ == "__main__":
    main()
