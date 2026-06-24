#!/usr/bin/env python3
"""콘텐츠 폴더(content/)를 읽어 배포용 정적 사이트(site/)를 빌드한다.

각 <slug>/ 폴더(article.md·index.html·thumbnail·meta.json)를 site/ 로 복사하고,
모든 글을 카드로 모은 갤러리형 홈페이지 site/index.html 을 생성한다.
의존성 없음 — Cloudflare Pages 의 publish 디렉터리로 그대로 올린다.
"""
import argparse
import html
import json
import shutil
from pathlib import Path

CARD = """    <a class="card" href="{slug}/index.html">
      {thumb}
      <div class="card-body">
        <h2>{title}</h2>
        <p class="summary">{summary}</p>
        <div class="meta"><span>{created}</span>{tags}</div>
      </div>
    </a>"""

PAGE = """<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{site_title}</title>
<style>
  :root{{--accent:#4f7cff}}
  *{{box-sizing:border-box}}
  body{{margin:0;font-family:system-ui,-apple-system,"Apple SD Gothic Neo",sans-serif;background:#f7f8fa;color:#1a1a1a}}
  header{{padding:48px 20px 32px;text-align:center}}
  header h1{{margin:0;font-size:32px}}
  header p{{color:#667085;margin:8px 0 0}}
  .grid{{max-width:1080px;margin:0 auto;padding:0 20px 60px;display:grid;
    grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px}}
  .card{{background:#fff;border-radius:14px;overflow:hidden;text-decoration:none;color:inherit;
    box-shadow:0 1px 3px rgba(16,24,40,.08);transition:transform .15s,box-shadow .15s;display:flex;flex-direction:column}}
  .card:hover{{transform:translateY(-3px);box-shadow:0 8px 24px rgba(16,24,40,.12)}}
  .thumb{{position:relative}}
  .card img{{width:100%;aspect-ratio:16/9;object-fit:cover;background:#eef1ff;display:block}}
  .play{{position:absolute;left:10px;bottom:10px;background:rgba(0,0,0,.7);color:#fff;
    font-size:12px;padding:3px 9px;border-radius:999px}}
  .card-body{{padding:16px}}
  .card h2{{font-size:18px;margin:0 0 8px;line-height:1.35}}
  .summary{{color:#475467;font-size:14px;margin:0;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}}
  .meta{{margin-top:12px;font-size:12px;color:#98a2b3;display:flex;gap:6px;flex-wrap:wrap;align-items:center}}
  .tag{{background:#eef1ff;color:var(--accent);border-radius:999px;padding:2px 8px}}
  footer{{text-align:center;color:#98a2b3;font-size:13px;padding:24px}}
</style></head>
<body>
  <header><h1>{site_title}</h1><p>{site_desc} · 글 {count}편</p></header>
  <main class="grid">
{cards}
  </main>
  <footer>AutoContent 로 0원 자동 생성 · 매일 갱신</footer>
</body></html>"""


def build(src: str, dest: str, site_title: str, site_desc: str):
    src_dir, dest_dir = Path(src), Path(dest)
    dest_dir.mkdir(parents=True, exist_ok=True)

    articles = []
    for meta_path in sorted(src_dir.glob("*/meta.json")):
        slug = meta_path.parent.name
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        # 글 폴더 통째로 복사
        target = dest_dir / slug
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(meta_path.parent, target)
        meta["_slug"] = slug
        articles.append(meta)

    # 최신순 정렬(생성일 내림차순)
    articles.sort(key=lambda m: m.get("created", ""), reverse=True)

    cards = []
    for m in articles:
        assets = m.get("assets", {})
        thumb = assets.get("image")
        badge = '<span class="play">▶ 숏폼</span>' if assets.get("video") else ""
        thumb_html = (
            f'<div class="thumb"><img src="{html.escape(m["_slug"])}/{html.escape(thumb)}" alt="">{badge}</div>'
            if thumb
            else f'<div class="thumb"><img alt="">{badge}</div>'
        )
        tags = "".join(
            f'<span class="tag">#{html.escape(str(t))}</span>' for t in m.get("tags", [])[:3]
        )
        cards.append(
            CARD.format(
                slug=html.escape(m["_slug"]),
                thumb=thumb_html,
                title=html.escape(m.get("title", m["_slug"])),
                summary=html.escape(m.get("summary", "")),
                created=html.escape(m.get("created", "")),
                tags=tags,
            )
        )

    (dest_dir / "index.html").write_text(
        PAGE.format(
            site_title=html.escape(site_title),
            site_desc=html.escape(site_desc),
            count=len(articles),
            cards="\n".join(cards) or "    <p>아직 글이 없습니다.</p>",
        ),
        encoding="utf-8",
    )
    print(f"✅ 사이트 빌드 완료: {dest_dir}/index.html ({len(articles)}편)")


def main():
    p = argparse.ArgumentParser(description="content/ → site/ 정적 사이트 빌드")
    p.add_argument("--src", default="content", help="콘텐츠 소스 폴더 (기본: content)")
    p.add_argument("--dest", default="site", help="빌드 출력 폴더 (기본: site)")
    p.add_argument("--title", default="AutoContent", help="사이트 제목")
    p.add_argument("--desc", default="매일 자동 생성되는 콘텐츠", help="사이트 설명")
    args = p.parse_args()
    build(args.src, args.dest, args.title, args.desc)


if __name__ == "__main__":
    main()
