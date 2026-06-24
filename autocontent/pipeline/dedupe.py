"""중복 방지 — 무료 임베딩 API로 주제를 벡터화하고 기존 글과 의미 유사도를 비교한다.

저장소는 Chroma(설치 시) 우선, 없으면 의존성 없는 JSON 파일 폴백을 쓴다.
임베딩 호출이 실패하면(네트워크 등) 중복 판정을 건너뛰어 생성은 막지 않는다.
"""
import json
import math
from pathlib import Path

import httpx

from config import Config


def embed(text: str):
    """OpenAI 호환 /embeddings 로 텍스트 임베딩. 실패 시 None."""
    if not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY.startswith("여기에"):
        return None
    url = f"{Config.OPENAI_BASE_URL}/embeddings"
    headers = {
        "Authorization": f"Bearer {Config.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    try:
        with httpx.Client(timeout=60) as client:
            resp = client.post(url, headers=headers, json={"model": Config.EMBED_MODEL, "input": text})
            resp.raise_for_status()
            return resp.json()["data"][0]["embedding"]
    except Exception as exc:
        print(f"  ⚠ 임베딩 실패(중복검사 생략): {exc}")
        return None


def _cosine(a, b) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


class _JsonStore:
    """Chroma 미설치 시 폴백. {id: embedding} 를 JSON 으로 보관."""

    def __init__(self, path: Path):
        self.path = path
        self.data = json.loads(path.read_text()) if path.exists() else {}

    def nearest(self, vec):
        best_id, best = None, 0.0
        for cid, emb in self.data.items():
            s = _cosine(vec, emb)
            if s > best:
                best_id, best = cid, s
        return best_id, best

    def add(self, cid, vec, _doc):
        self.data[cid] = vec
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data))


class _ChromaStore:
    def __init__(self, path: Path):
        import chromadb

        self.client = chromadb.PersistentClient(path=str(path))
        # 임베딩을 직접 넣으므로 별도 임베딩 함수 불필요(로컬 모델 다운로드 X)
        self.col = self.client.get_or_create_collection("articles")

    def nearest(self, vec):
        if self.col.count() == 0:
            return None, 0.0
        res = self.col.query(query_embeddings=[vec], n_results=1)
        ids = res.get("ids", [[]])[0]
        dists = res.get("distances", [[]])[0]
        if not ids:
            return None, 0.0
        # chroma 기본 거리(L2/cosine distance) → 유사도 근사. cosine distance=1-sim
        return ids[0], 1.0 - dists[0]

    def add(self, cid, vec, doc):
        self.col.add(ids=[cid], embeddings=[vec], documents=[doc])


def get_store(base_dir: Path):
    """Chroma 가 있으면 Chroma, 없으면 JSON 폴백 저장소 반환."""
    path = Path(base_dir) / ".vectorstore"
    try:
        return _ChromaStore(path)
    except ImportError:
        return _JsonStore(path / "store.json")
    except Exception as exc:
        print(f"  ⚠ Chroma 초기화 실패 → JSON 폴백: {exc}")
        return _JsonStore(path / "store.json")


def check_duplicate(topic: str, base_dir, threshold: float = None):
    """(is_dup, score, embedding) 반환. embedding 은 등록용으로 재사용.

    임베딩 불가 시 (False, 0.0, None) — 생성을 막지 않는다.
    """
    threshold = Config.DEDUPE_THRESHOLD if threshold is None else threshold
    vec = embed(topic)
    if vec is None:
        return False, 0.0, None
    store = get_store(base_dir)
    _, score = store.nearest(vec)
    return score >= threshold, score, vec


def register(slug: str, topic: str, base_dir, embedding=None):
    """생성 성공한 글을 저장소에 등록."""
    vec = embedding if embedding is not None else embed(topic)
    if vec is None:
        return
    get_store(base_dir).add(slug, vec, topic)
