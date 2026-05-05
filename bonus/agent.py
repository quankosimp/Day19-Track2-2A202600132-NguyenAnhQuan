from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, FieldCondition, Filter, MatchValue, PointStruct, VectorParams


@dataclass
class MemoryHit:
    text: str
    score: float


class HybridMemoryAgent:
    """Minimal hybrid memory agent: episodic memory + profile context.

    - Episodic memory: Qdrant vector + in-memory BM25-like sparse scoring
    - Stable profile/recent activity: simple local dict fallback for clarity
    """

    def __init__(self, collection: str = "bonus_memory", embed_model: str = "BAAI/bge-small-en-v1.5") -> None:
        self.collection = collection
        self.embedder = TextEmbedding(model_name=embed_model)
        self.client = QdrantClient(":memory:")
        self.client.create_collection(
            collection_name=self.collection,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )
        self._next_id = 0
        self._docs: list[dict] = []
        self._profiles: dict[str, dict] = {
            "u_001": {
                "preferred_language": "vi",
                "topic_affinity": "cloud",
                "reading_speed_wpm": 240,
                "queries_last_hour": 6,
                "distinct_topics_24h": 4,
            }
        }

    @staticmethod
    def _chunk_text(text: str, size: int = 220, overlap: int = 40) -> Iterable[str]:
        text = " ".join(text.split())
        if len(text) <= size:
            yield text
            return
        step = max(1, size - overlap)
        for i in range(0, len(text), step):
            chunk = text[i:i + size].strip()
            if chunk:
                yield chunk

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return text.lower().split()

    def _sparse_search(self, query: str, user_id: str, top_k: int) -> list[MemoryHit]:
        q = self._tokenize(query)
        scored: list[tuple[int, float]] = []
        for i, d in enumerate(self._docs):
            if d["user_id"] != user_id:
                continue
            tokens = d["tokens"]
            overlap = sum(1 for t in q if t in tokens)
            # tiny length normalization; enough for a lightweight BM25-ish baseline
            score = overlap / math.sqrt(max(1, len(tokens)))
            if score > 0:
                scored.append((i, score))
        scored.sort(key=lambda x: -x[1])
        return [MemoryHit(text=self._docs[i]["text"], score=s) for i, s in scored[:top_k]]

    def _semantic_search(self, query: str, user_id: str, top_k: int) -> list[MemoryHit]:
        q_vec = next(self.embedder.embed([query])).tolist()
        res = self.client.query_points(
            collection_name=self.collection,
            query=q_vec,
            query_filter=Filter(
                must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
            ),
            limit=top_k,
        )
        return [MemoryHit(text=p.payload["text"], score=float(p.score)) for p in res.points]

    def remember(self, text: str, user_id: str = "u_001") -> None:
        """Add a new piece of episodic memory for this user."""
        points: list[PointStruct] = []
        for chunk in self._chunk_text(text):
            vec = next(self.embedder.embed([chunk])).tolist()
            points.append(
                PointStruct(
                    id=self._next_id,
                    vector=vec,
                    payload={"user_id": user_id, "text": chunk},
                )
            )
            self._docs.append({"user_id": user_id, "text": chunk, "tokens": self._tokenize(chunk)})
            self._next_id += 1

        if points:
            self.client.upsert(collection_name=self.collection, points=points)

    def recall(self, query: str, user_id: str = "u_001") -> str:
        """Retrieve top-K memories + user profile features and assemble context."""
        top_k = 5
        kw_hits = self._sparse_search(query, user_id, top_k)
        sem_hits = self._semantic_search(query, user_id, top_k)

        # Hybrid RRF fusion on text identity for this minimal POC
        rrf_k = 60
        scores: dict[str, float] = {}
        for rank, h in enumerate(kw_hits, start=1):
            scores[h.text] = scores.get(h.text, 0.0) + 1.0 / (rrf_k + rank)
        for rank, h in enumerate(sem_hits, start=1):
            scores[h.text] = scores.get(h.text, 0.0) + 1.0 / (rrf_k + rank)

        top_memories = [t for t, _ in sorted(scores.items(), key=lambda kv: -kv[1])[:3]]
        profile = self._profiles.get(
            user_id,
            {
                "preferred_language": "vi",
                "topic_affinity": "general",
                "reading_speed_wpm": 220,
                "queries_last_hour": 0,
                "distinct_topics_24h": 0,
            },
        )

        return (
            f"User={user_id}; lang={profile['preferred_language']}; "
            f"topic_affinity={profile['topic_affinity']}; "
            f"reading_speed_wpm={profile['reading_speed_wpm']}; "
            f"queries_last_hour={profile['queries_last_hour']}; "
            f"distinct_topics_24h={profile['distinct_topics_24h']}\n"
            f"Query: {query}\n"
            f"Top memories:\n- " + "\n- ".join(top_memories if top_memories else ["(no memory yet)"])
        )
