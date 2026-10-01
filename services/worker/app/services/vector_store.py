"""VectorStore implementation for asset embeddings and similarity search."""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from app.db import get_supabase_client, memory_db


def cosine_similarity(v1: list[float], v2: list[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return max(0.0, min(1.0, dot / (norm1 * norm2)))


class VectorStore:
    def __init__(self) -> None:
        self.supabase = get_supabase_client()

    def add_embedding(
        self,
        asset_id: UUID,
        modality: str,
        model_name: str,
        embedding: list[float],
    ) -> dict[str, Any]:
        emb_id = uuid4()
        now = datetime.now(timezone.utc)
        record = {
            "id": str(emb_id),
            "asset_id": str(asset_id),
            "modality": modality,
            "model_name": model_name,
            "dimensions": len(embedding),
            "embedding": embedding,
            "created_at": now.isoformat(),
        }

        if self.supabase:
            try:
                res = self.supabase.table("embeddings").insert(record).execute()
                if res.data:
                    return res.data[0]
            except Exception:
                pass

        memory_db.embeddings[emb_id] = record
        return record

    def search(
        self,
        query_embedding: list[float],
        limit: int = 8,
        project_id: UUID | None = None,
        candidate_asset_ids: list[UUID] | None = None,
    ) -> list[tuple[UUID, float]]:
        """Return list of (asset_id, similarity) sorted descending by similarity."""

        candidates: dict[UUID, float] = {}

        if self.supabase:
            try:
                # If Supabase RPC match_embeddings is configured
                res = self.supabase.rpc(
                    "match_embeddings",
                    {
                        "query_embedding": query_embedding,
                        "match_threshold": 0.0,
                        "match_count": limit,
                    },
                ).execute()
                if res.data:
                    return [(UUID(r["asset_id"]), float(r["similarity"])) for r in res.data]
            except Exception:
                pass

        # Memory store search fallback
        cand_str_set = {str(a) for a in candidate_asset_ids} if candidate_asset_ids else None

        for emb in memory_db.embeddings.values():
            aid_str = emb.get("asset_id")
            if not aid_str:
                continue
            if cand_str_set and aid_str not in cand_str_set:
                continue

            aid = UUID(aid_str)
            sim = cosine_similarity(query_embedding, emb.get("embedding", []))
            if aid not in candidates or sim > candidates[aid]:
                candidates[aid] = sim

        sorted_cand = sorted(candidates.items(), key=lambda item: item[1], reverse=True)
        return sorted_cand[:limit]
