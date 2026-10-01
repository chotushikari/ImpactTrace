"""ProjectService implementation."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from contracts import ProjectCreate, SiteCreate
from app.db import get_supabase_client, memory_db


class ProjectService:
    def __init__(self) -> None:
        self.supabase = get_supabase_client()

    def create_project(self, data: ProjectCreate) -> dict[str, Any]:
        project_id = uuid4()
        now = datetime.now(timezone.utc)
        record = {
            "id": str(project_id),
            "name": data.name,
            "description": data.description,
            "objective": data.objective,
            "default_lat": data.default_lat,
            "default_lng": data.default_lng,
            "created_at": now.isoformat(),
        }

        if self.supabase:
            try:
                res = self.supabase.table("projects").insert(record).execute()
                if res.data:
                    return res.data[0]
            except Exception:
                pass

        memory_db.projects[project_id] = record
        return record

    def get_project(self, project_id: UUID | str) -> dict[str, Any] | None:
        pid_str = str(project_id)
        pid_uuid = UUID(pid_str) if isinstance(project_id, str) else project_id
        if self.supabase:
            try:
                res = self.supabase.table("projects").select("*").eq("id", pid_str).execute()
                if res.data:
                    return res.data[0]
            except Exception:
                pass

        return memory_db.projects.get(pid_uuid) or memory_db.projects.get(pid_str)


    def list_projects(self) -> list[dict[str, Any]]:
        if self.supabase:
            try:
                res = self.supabase.table("projects").select("*").order("created_at", desc=True).execute()
                if res.data:
                    return res.data
            except Exception:
                pass

        return list(memory_db.projects.values())

    def create_site(self, data: SiteCreate) -> dict[str, Any]:
        site_id = uuid4()
        record = {
            "id": str(site_id),
            "project_id": str(data.project_id),
            "name": data.name,
            "address": data.address,
            "lat": data.lat,
            "lng": data.lng,
            "geocode_source": data.geocode_source,
        }

        if self.supabase:
            try:
                res = self.supabase.table("sites").insert(record).execute()
                if res.data:
                    return res.data[0]
            except Exception:
                pass

        memory_db.sites[site_id] = record
        return record

    def list_sites(self, project_id: UUID) -> list[dict[str, Any]]:
        if self.supabase:
            try:
                res = self.supabase.table("sites").select("*").eq("project_id", str(project_id)).execute()
                if res.data:
                    return res.data
            except Exception:
                pass

        return [s for s in memory_db.sites.values() if s.get("project_id") == str(project_id)]
