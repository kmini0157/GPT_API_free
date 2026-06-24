#!/usr/bin/env python3
"""AutoContent — 주제 하나로 글·썸네일·내레이션·발행물을 0원으로 자동 생성.

사용법:
    python main.py "양자컴퓨터가 암호를 깨는 원리"
    python main.py "주제" --no-image --no-voice
"""
import argparse
import re
import sys
from pathlib import Path

from config import Config
from pipeline import image, publish, research, voice, write


def slugify(text: str) -> str:
    text = re.sub(r"[^\w가-힣\- ]+", "", text).strip().replace(" ", "-")
    return (text[:50] or "untitled").lower()


def run(topic: str, do_research=True, do_image=True, do_voice=True) -> Path:
    out_dir = Path("output") / slugify(topic)
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

    # ⑤ 발행물 조립
    print("⑤ 발행물 조립…")
    publish.write_markdown(article, out_dir / "article.md", image_name, audio_name)
    publish.write_html(article, out_dir / "index.html", image_name, audio_name)
    publish.write_meta(article, out_dir / "meta.json", assets)
    print("   ✓ article.md · index.html · meta.json")

    print(f"\n✅ 완료 → {out_dir}/index.html 를 브라우저로 열어보세요.\n")
    return out_dir


def main():
    parser = argparse.ArgumentParser(description="주제 → 글·썸네일·음성 자동 생성")
    parser.add_argument("topic", help="콘텐츠 주제")
    parser.add_argument("--no-research", action="store_true", help="Jina 리서치 건너뛰기")
    parser.add_argument("--no-image", action="store_true", help="썸네일 생성 건너뛰기")
    parser.add_argument("--no-voice", action="store_true", help="내레이션 생성 건너뛰기")
    args = parser.parse_args()

    try:
        run(
            args.topic,
            do_research=not args.no_research,
            do_image=not args.no_image,
            do_voice=not args.no_voice,
        )
    except KeyboardInterrupt:
        print("\n중단됨.")
        sys.exit(130)


if __name__ == "__main__":
    main()
