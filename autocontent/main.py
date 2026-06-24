#!/usr/bin/env python3
"""AutoContent — 주제 하나로 글·썸네일·내레이션·발행물을 0원으로 자동 생성.

사용법:
    python main.py "양자컴퓨터가 암호를 깨는 원리"
    python main.py "주제" --no-image --no-voice
    python main.py --from-queue topics.txt --out content   # 큐에서 다음 주제 1건
"""
import argparse
import datetime
import re
import sys
from pathlib import Path

from pipeline import dedupe, image, publish, research, video, voice, write


def slugify(text: str) -> str:
    text = re.sub(r"[^\w가-힣\- ]+", "", text).strip().replace(" ", "-")
    return (text[:50] or "untitled").lower()


def pick_from_queue(queue_path: Path, out_base: Path):
    """큐 파일에서 아직 생성 폴더가 없는 첫 주제를 반환. 없으면 None."""
    if not queue_path.exists():
        raise SystemExit(f"큐 파일이 없습니다: {queue_path}")
    for line in queue_path.read_text(encoding="utf-8").splitlines():
        topic = line.strip()
        if not topic or topic.startswith("#"):
            continue
        if not (out_base / slugify(topic)).exists():
            return topic
    return None


def run(topic, out_base="output", do_research=True, do_image=True,
        do_voice=True, do_video=True, do_dedupe=False):
    slug = slugify(topic)

    # ⓪ 중복 방지 — 의미상 비슷한 글이 이미 있으면 생성 스킵
    embedding = None
    if do_dedupe:
        print("⓪ 중복 검사(벡터DB)…")
        is_dup, score, embedding = dedupe.check_duplicate(topic, out_base)
        if is_dup:
            print(f"   ⏭ 유사 글 존재(유사도 {score:.2f}) — 생성 건너뜀")
            return None
        if score:
            print(f"   신규 주제(최대 유사도 {score:.2f})")

    out_dir = Path(out_base) / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n▶ 주제: {topic}")
    print(f"  출력 폴더: {out_dir}/")

    # ① 리서치
    research_text = ""
    if do_research:
        print("① 리서치(Jina)…")
        research_text = research.research(topic)
        print(f"   자료 {len(research_text)}자 확보")

    # ② 글 작성
    print("② 글 작성(LLM)…")
    article = write.write_article(topic, research_text)
    article["created"] = datetime.datetime.now().strftime("%Y-%m-%d")
    print(f"   제목: {article['title']}")

    assets = {}

    # ③ 썸네일
    image_name = None
    if do_image:
        print("③ 썸네일(Pollinations)…")
        image_name = "thumbnail.jpg"
        if image.generate_thumbnail(article["image_prompt"], out_dir / image_name):
            assets["image"] = image_name
            print("   ✓ thumbnail.jpg")
        else:
            image_name = None

    # ④ 내레이션
    audio_name = None
    if do_voice:
        print("④ 내레이션(edge-tts)…")
        audio_name = "narration.mp3"
        if voice.synthesize(article.get("narration", ""), out_dir / audio_name):
            assets["audio"] = audio_name
            print("   ✓ narration.mp3")
        else:
            audio_name = None

    # ⑤ 숏폼 영상 (썸네일 + 내레이션 → 9:16 mp4)
    if do_video and image_name and audio_name:
        print("⑤ 숏폼 영상(ffmpeg)…")
        if video.make_short(out_dir / image_name, out_dir / audio_name, out_dir / "short.mp4"):
            assets["video"] = "short.mp4"
            print("   ✓ short.mp4")

    # ⑥ 발행물 조립
    print("⑥ 발행물 조립…")
    video_name = assets.get("video")
    publish.write_markdown(article, out_dir / "article.md", image_name, audio_name, video_name)
    publish.write_html(article, out_dir / "index.html", image_name, audio_name, video_name)
    publish.write_meta(article, out_dir / "meta.json", assets)
    print("   ✓ article.md · index.html · meta.json")

    # 중복 방지 저장소에 등록
    if do_dedupe:
        dedupe.register(slug, topic, out_base, embedding)

    print(f"\n✅ 완료 → {out_dir}/index.html 를 브라우저로 열어보세요.\n")
    return out_dir


def main():
    parser = argparse.ArgumentParser(description="주제 → 글·썸네일·음성 자동 생성")
    parser.add_argument("topic", nargs="?", help="콘텐츠 주제")
    parser.add_argument("--from-queue", metavar="FILE", help="큐 파일에서 다음 미생성 주제 1건 처리")
    parser.add_argument("--out", default="output", help="출력 기본 폴더 (기본: output)")
    parser.add_argument("--no-research", action="store_true", help="Jina 리서치 건너뛰기")
    parser.add_argument("--no-image", action="store_true", help="썸네일 생성 건너뛰기")
    parser.add_argument("--no-voice", action="store_true", help="내레이션 생성 건너뛰기")
    parser.add_argument("--no-video", action="store_true", help="숏폼 영상 생성 건너뛰기")
    parser.add_argument("--dedupe", action="store_true", help="벡터DB로 유사 주제 중복 방지")
    args = parser.parse_args()

    out_base = Path(args.out)

    if args.from_queue:
        topic = pick_from_queue(Path(args.from_queue), out_base)
        if topic is None:
            print("큐에 새로 생성할 주제가 없습니다. 종료.")
            return
        print(f"큐에서 선택: {topic}")
    elif args.topic:
        topic = args.topic
    else:
        parser.error("주제를 입력하거나 --from-queue 를 사용하세요.")

    try:
        run(
            topic,
            out_base=str(out_base),
            do_research=not args.no_research,
            do_image=not args.no_image,
            do_voice=not args.no_voice,
            do_video=not args.no_video,
            do_dedupe=args.dedupe,
        )
    except KeyboardInterrupt:
        print("\n중단됨.")
        sys.exit(130)


if __name__ == "__main__":
    main()
