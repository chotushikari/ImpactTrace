"""ObservationService implementation for AI observations."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from contracts import ObservationCreate, ObservationType
from app.db import get_supabase_client, memory_db


class ObservationService:
    def __init__(self) -> None:
        self.supabase = get_supabase_client()

    def create_observation(self, data: ObservationCreate) -> dict[str, Any]:
        obs_id = uuid4()
        now = datetime.now(timezone.utc)
        record = {
            "id": str(obs_id),
            "asset_id": str(data.asset_id),
            "type": data.type.value if isinstance(data.type, ObservationType) else str(data.type),
            "text": data.text,
            "structured_json": data.structured_json,
            "model_provider": data.model_provider,
            "model_name": data.model_name,
            "model_version": data.model_version,
            "confidence": data.confidence,
            "created_at": now.isoformat(),
        }

        if self.supabase:
            try:
                res = self.supabase.table("observations").insert(record).execute()
                if res.data:
                    return res.data[0]
            except Exception:
                pass

        memory_db.observations[obs_id] = record
        return record

    def list_observations(self, asset_id: UUID) -> list[dict[str, Any]]:
        if self.supabase:
            try:
                res = self.supabase.table("observations").select("*").eq("asset_id", str(asset_id)).execute()
                if res.data:
                    return res.data
            except Exception:
                pass

        return [o for o in memory_db.observations.values() if o.get("asset_id") == str(asset_id)]
