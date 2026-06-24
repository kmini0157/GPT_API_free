#!/usr/bin/env python3
"""트렌드 자동 수집 — 키 없이 트렌딩 주제를 모아 topics.txt 큐에 추가한다.

소스(키 불필요):
  - trends : Google Trends 일일 인기검색 RSS (geo 지정)
  - hn     : Hacker News 인기글 제목

사용:
    python fill_queue.py --source trends --geo KR --limit 5
    python fill_queue.py --source hn --limit 5
"""
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path

import httpx


def from_google_trends(geo: str, limit: int):
    url = f"https://trends.google.com/trends/trendingsearches/daily/rss?geo={geo}"
    with httpx.Client(timeout=30, follow_redirects=True) as client:
        resp = client.get(url, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
    root = ET.fromstring(resp.text)
    titles = [item.findtext("title", "").strip() for item in root.iter("item")]
    return [t for t in titles if t][:limit]


def from_hackernews(limit: int):
    base = "https://hacker-news.firebaseio.com/v0"
    with httpx.Client(timeout=30) as client:
        ids = client.get(f"{base}/topstories.json").json()[: limit * 2]
        titles = []
        for sid in ids:
            item = client.get(f"{base}/item/{sid}.json").json() or {}
            title = (item.get("title") or "").strip()
            if title:
                titles.append(title)
            if len(titles) >= limit:
                break
    return titles


def existing_topics(queue_path: Path):
    if not queue_path.exists():
        return set()
    out = set()
    for line in queue_path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s and not s.startswith("#"):
            out.add(s)
    return out


def append_topics(queue_path: Path, topics):
    have = existing_topics(queue_path)
    fresh = [t for t in topics if t not in have]
    if not fresh:
        print("새로 추가할 트렌드 주제가 없습니다(이미 큐에 존재).")
        return 0
    with queue_path.open("a", encoding="utf-8") as f:
        if queue_path.exists() and queue_path.stat().st_size > 0:
            f.write("\n")
        f.write("\n".join(fresh) + "\n")
    print(f"큐에 {len(fresh)}개 주제 추가:")
    for t in fresh:
        print(f"  + {t}")
    return len(fresh)


def main():
    p = argparse.ArgumentParser(description="트렌드 주제를 큐에 자동 추가")
    p.add_argument("--source", choices=["trends", "hn"], default="trends")
    p.add_argument("--geo", default="KR", help="Google Trends 지역코드 (기본 KR)")
    p.add_argument("--limit", type=int, default=5)
    p.add_argument("--queue", default="topics.txt")
    args = p.parse_args()

    try:
        if args.source == "trends":
            topics = from_google_trends(args.geo, args.limit)
        else:
            topics = from_hackernews(args.limit)
    except Exception as exc:
        print(f"⚠ 트렌드 수집 실패(큐 변경 없음): {exc}")
        return

    if not topics:
        print("수집된 주제가 없습니다.")
        return
    append_topics(Path(args.queue), topics)


if __name__ == "__main__":
    main()
