"""AssetService implementation for Cloudinary asset records."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from contracts import AssetRecord, CloudinaryAssetRef
from app.db import get_supabase_client, memory_db


class AssetService:
    def __init__(self) -> None:
        self.supabase = get_supabase_client()

    def create_asset(
        self,
        project_id: UUID,
        cloudinary_ref: CloudinaryAssetRef,
        site_id: UUID | None = None,
        source_filename: str | None = None,
        captured_at: datetime | None = None,
        captured_at_source: str | None = None,
        lat: float | None = None,
        lng: float | None = None,
        location_source: str | None = None,
        duration_seconds: float | None = None,
        status: str = "queued",
    ) -> AssetRecord:
        asset_id = uuid4()
        now = datetime.now(timezone.utc)
        record = AssetRecord(
            id=asset_id,
            project_id=project_id,
            site_id=site_id,
            cloudinary=cloudinary_ref,
            source_filename=source_filename,
            captured_at=captured_at,
            captured_at_source=captured_at_source,
            uploaded_at=now,
            lat=lat,
            lng=lng,
            location_source=location_source,
            duration_seconds=duration_seconds,
            status=status,
        )

        db_row = {
            "id": str(record.id),
            "project_id": str(record.project_id),
            "site_id": str(record.site_id) if record.site_id else None,
            "cloudinary_asset_id": record.cloudinary.asset_id,
            "cloudinary_public_id": record.cloudinary.public_id,
            "cloudinary_version": record.cloudinary.version,
            "resource_type": record.cloudinary.resource_type,
            "format": record.cloudinary.format,
            "secure_url": str(record.cloudinary.secure_url),
            "source_filename": record.source_filename,
            "captured_at": record.captured_at.isoformat() if record.captured_at else None,
            "captured_at_source": record.captured_at_source,
            "uploaded_at": record.uploaded_at.isoformat(),
            "lat": record.lat,
            "lng": record.lng,
            "location_source": record.location_source,
            "duration_seconds": record.duration_seconds,
            "status": record.status,
            "created_at": now.isoformat(),
        }

        if self.supabase:
            try:
                res = self.supabase.table("assets").insert(db_row).execute()
            except Exception:
                pass

        memory_db.assets[asset_id] = record.model_dump(mode="json")
        return record

    def get_asset(self, asset_id: UUID) -> AssetRecord | None:
        if self.supabase:
            try:
                res = self.supabase.table("assets").select("*").eq("id", str(asset_id)).execute()
                if res.data:
                    row = res.data[0]
                    return self._row_to_record(row)
            except Exception:
                pass

        data = memory_db.assets.get(asset_id)
        if data:
            return AssetRecord.model_validate(data)
        return None

    def get_asset_by_cloudinary_id(self, cloudinary_asset_id: str) -> AssetRecord | None:
        if self.supabase:
            try:
                res = self.supabase.table("assets").select("*").eq("cloudinary_asset_id", cloudinary_asset_id).execute()
                if res.data:
                    return self._row_to_record(res.data[0])
            except Exception:
                pass

        for data in memory_db.assets.values():
            if data.get("cloudinary", {}).get("asset_id") == cloudinary_asset_id:
                return AssetRecord.model_validate(data)
        return None

    def list_assets(self, project_id: UUID | None = None) -> list[AssetRecord]:
        if self.supabase:
            try:
                q = self.supabase.table("assets").select("*")
                if project_id:
                    q = q.eq("project_id", str(project_id))
                res = q.order("created_at", desc=True).execute()
                if res.data:
                    return [self._row_to_record(r) for r in res.data]
            except Exception:
                pass

        results = []
        for data in memory_db.assets.values():
            rec = AssetRecord.model_validate(data)
            if project_id is None or rec.project_id == project_id:
                results.append(rec)
        return results

    def update_status(self, asset_id: UUID, status: str) -> AssetRecord | None:
        if self.supabase:
            try:
                self.supabase.table("assets").update({"status": status}).eq("id", str(asset_id)).execute()
            except Exception:
                pass

        if asset_id in memory_db.assets:
            memory_db.assets[asset_id]["status"] = status
            return AssetRecord.model_validate(memory_db.assets[asset_id])
        return None

    def _row_to_record(self, row: dict[str, Any]) -> AssetRecord:
        ref = CloudinaryAssetRef(
            asset_id=row["cloudinary_asset_id"],
            public_id=row["cloudinary_public_id"],
            resource_type=row["resource_type"],
            version=row.get("cloudinary_version"),
            format=row.get("format"),
            secure_url=row["secure_url"],
        )
        return AssetRecord(
            id=UUID(row["id"]),
            project_id=UUID(row["project_id"]),
            site_id=UUID(row["site_id"]) if row.get("site_id") else None,
            cloudinary=ref,
            source_filename=row.get("source_filename"),
            captured_at=datetime.fromisoformat(row["captured_at"]) if row.get("captured_at") else None,
            captured_at_source=row.get("captured_at_source"),
            uploaded_at=datetime.fromisoformat(row["uploaded_at"]),
            lat=row.get("lat"),
            lng=row.get("lng"),
            location_source=row.get("location_source"),
            duration_seconds=float(row["duration_seconds"]) if row.get("duration_seconds") is not None else None,
            status=row["status"],
        )
