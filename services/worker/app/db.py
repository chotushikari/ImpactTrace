"""Database connection and in-memory fallback storage module for ImpactTrace worker."""

from __future__ import annotations

import os
from typing import Any
from uuid import UUID, uuid4
from datetime import datetime, timezone

try:
    from supabase import Client, create_client
except Exception:
    Client = None
    create_client = None



class MemoryStore:
    """In-memory thread-safe store for development and testing when Supabase is not configured."""

    def __init__(self) -> None:
        self.projects: dict[UUID, dict[str, Any]] = {}
        self.sites: dict[UUID, dict[str, Any]] = {}
        self.assets: dict[UUID, dict[str, Any]] = {}
        self.observations: dict[UUID, dict[str, Any]] = {}
        self.embeddings: dict[UUID, dict[str, Any]] = {}
        self.asset_relations: dict[UUID, dict[str, Any]] = {}
        self.change_observations: dict[UUID, dict[str, Any]] = {}
        self.claims: dict[UUID, dict[str, Any]] = {}
        self.evidence_links: dict[UUID, dict[str, Any]] = {}
        self.reports: dict[UUID, dict[str, Any]] = {}

    def clear(self) -> None:
        self.projects.clear()
        self.sites.clear()
        self.assets.clear()
        self.observations.clear()
        self.embeddings.clear()
        self.asset_relations.clear()
        self.change_observations.clear()
        self.claims.clear()
        self.evidence_links.clear()
        self.reports.clear()


memory_db = MemoryStore()


def get_supabase_client() -> Client | None:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    if url and key:
        try:
            return create_client(url, key)
        except Exception:
            return None
    return None
