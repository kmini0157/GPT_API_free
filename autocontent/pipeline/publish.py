"""⑤ 발행 단계 — 글·이미지·음성을 묶어 Markdown과 미리보기 HTML로 떨군다."""
import html
import json


def write_markdown(article: dict, out_path, image_name=None, audio_name=None):
    lines = [f"# {article['title']}", ""]
    if image_name:
        lines += [f"![thumbnail]({image_name})", ""]
    if article.get("summary"):
        lines += ["> **요약**", "> " + article["summary"].replace("\n", "\n> "), ""]
    lines += [article.get("body_md", ""), ""]
    if audio_name:
        lines += ["---", f"🔊 내레이션: `{audio_name}`", ""]
    if article.get("tags"):
        lines += ["", "**태그:** " + " ".join(f"#{t}" for t in article["tags"])]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def write_html(article: dict, out_path, image_name=None, audio_name=None):
    """공유/미리보기용 단일 HTML. 의존성 없는 정적 페이지."""
    title = html.escape(article["title"])
    body = html.escape(article.get("body_md", "")).replace("\n", "<br>")
    summary = html.escape(article.get("summary", "")).replace("\n", "<br>")
    tags = "".join(
        f'<span class="tag">#{html.escape(t)}</span>' for t in article.get("tags", [])
    )
    img = f'<img src="{html.escape(image_name)}" alt="thumbnail">' if image_name else ""
    audio = (
        f'<audio controls src="{html.escape(audio_name)}"></audio>' if audio_name else ""
    )
    doc = f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  body{{max-width:720px;margin:40px auto;padding:0 20px;font-family:system-ui,-apple-system,"Apple SD Gothic Neo",sans-serif;line-height:1.7;color:#1a1a1a}}
  img{{width:100%;border-radius:12px}}
  .summary{{background:#f4f6f8;border-left:4px solid #4f7cff;padding:12px 16px;border-radius:8px;margin:20px 0}}
  .tag{{display:inline-block;background:#eef1ff;color:#4f7cff;border-radius:999px;padding:4px 12px;margin:4px 4px 0 0;font-size:13px}}
  audio{{width:100%;margin-top:20px}}
  h1{{font-size:28px;line-height:1.3}}
</style></head>
<body>
  <h1>{title}</h1>
  {img}
  {f'<div class="summary">{summary}</div>' if summary else ''}
  <div class="body">{body}</div>
  {audio}
  <div class="tags">{tags}</div>
</body></html>"""
    out_path.write_text(doc, encoding="utf-8")


def write_meta(article: dict, out_path, assets: dict):
    """후속 자동화(발행 봇 등)가 읽을 메타데이터 JSON."""
    meta = {k: v for k, v in article.items()}
    meta["assets"] = assets
    out_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
