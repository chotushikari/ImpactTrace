"""EvidenceService implementation for claims, links, and evidence chains."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from contracts import (
    ClaimCreate,
    ClaimRecord,
    EvidenceChain,
    EvidenceLink,
    ObservationCreate,
    ObservationType,
)
from app.db import get_supabase_client, memory_db
from app.services.asset_service import AssetService
from app.services.observation_service import ObservationService


class EvidenceService:
    def __init__(self) -> None:
        self.supabase = get_supabase_client()
        self.asset_service = AssetService()
        self.observation_service = ObservationService()

    def create_claim(self, data: ClaimCreate) -> ClaimRecord:
        claim_id = uuid4()
        now = datetime.now(timezone.utc)

        claim_record = ClaimRecord(
            id=claim_id,
            project_id=data.project_id,
            text=data.text,
            claim_type=data.claim_type,
            verification_status=data.verification_status,
            confidence=data.confidence,
            evidence_asset_ids=data.evidence_asset_ids,
            observation_ids=data.observation_ids,
            relation_ids=data.relation_ids,
            created_at=now,
        )

        db_row = {
            "id": str(claim_id),
            "project_id": str(data.project_id),
            "text": data.text,
            "claim_type": data.claim_type.value,
            "verification_status": data.verification_status.value,
            "confidence": data.confidence,
            "created_at": now.isoformat(),
        }

        if self.supabase:
            try:
                self.supabase.table("claims").insert(db_row).execute()
            except Exception:
                pass

        memory_db.claims[claim_id] = claim_record.model_dump(mode="json")

        links: list[EvidenceLink] = []
        for asset_id in data.evidence_asset_ids:
            link = EvidenceLink(claim_id=claim_id, asset_id=asset_id, role="primary_source")
            self._save_link(link)
            links.append(link)

        for obs_id in data.observation_ids:
            link = EvidenceLink(claim_id=claim_id, observation_id=obs_id, role="supporting_observation")
            self._save_link(link)
            links.append(link)

        for rel_id in data.relation_ids:
            link = EvidenceLink(claim_id=claim_id, relation_id=rel_id, role="comparison_evidence")
            self._save_link(link)
            links.append(link)

        return claim_record

    def _save_link(self, link: EvidenceLink) -> None:
        link_id = uuid4()
        row = {
            "id": str(link_id),
            "claim_id": str(link.claim_id),
            "asset_id": str(link.asset_id) if link.asset_id else None,
            "observation_id": str(link.observation_id) if link.observation_id else None,
            "relation_id": str(link.relation_id) if link.relation_id else None,
            "role": link.role,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        if self.supabase:
            try:
                self.supabase.table("evidence_links").insert(row).execute()
            except Exception:
                pass
        memory_db.evidence_links[link_id] = link.model_dump(mode="json")

    def get_claim(self, claim_id: UUID) -> ClaimRecord | None:
        if self.supabase:
            try:
                res = self.supabase.table("claims").select("*").eq("id", str(claim_id)).execute()
                if res.data:
                    row = res.data[0]
                    links_res = self.supabase.table("evidence_links").select("*").eq("claim_id", str(claim_id)).execute()
                    asset_ids = [UUID(l["asset_id"]) for l in links_res.data if l.get("asset_id")]
                    obs_ids = [UUID(l["observation_id"]) for l in links_res.data if l.get("observation_id")]
                    rel_ids = [UUID(l["relation_id"]) for l in links_res.data if l.get("relation_id")]
                    return ClaimRecord(
                        id=UUID(row["id"]),
                        project_id=UUID(row["project_id"]),
                        text=row["text"],
                        claim_type=row["claim_type"],
                        verification_status=row["verification_status"],
                        confidence=row.get("confidence"),
                        evidence_asset_ids=asset_ids,
                        observation_ids=obs_ids,
                        relation_ids=rel_ids,
                        created_at=datetime.fromisoformat(row["created_at"]),
                    )
            except Exception:
                pass

        data = memory_db.claims.get(claim_id)
        if data:
            return ClaimRecord.model_validate(data)
        return None

    def list_claims(self, project_id: UUID) -> list[ClaimRecord]:
        if self.supabase:
            try:
                res = self.supabase.table("claims").select("*").eq("project_id", str(project_id)).execute()
                if res.data:
                    return [self.get_claim(UUID(r["id"])) for r in res.data if self.get_claim(UUID(r["id"]))]
            except Exception:
                pass

        return [
            ClaimRecord.model_validate(c)
            for c in memory_db.claims.values()
            if c.get("project_id") == str(project_id) or c.get("project_id") == project_id
        ]

    def get_evidence_chain(self, claim_id: UUID) -> EvidenceChain | None:
        claim = self.get_claim(claim_id)
        if not claim:
            return None

        assets = [self.asset_service.get_asset(aid) for aid in claim.evidence_asset_ids]
        valid_assets = [a for a in assets if a is not None]

        observations = []
        for aid in claim.evidence_asset_ids:
            obs_list = self.observation_service.list_observations(aid)
            for o in obs_list:
                observations.append(
                    ObservationCreate(
                        asset_id=UUID(o["asset_id"]),
                        type=ObservationType(o["type"]),
                        text=o.get("text"),
                        structured_json=o.get("structured_json", {}),
                        model_provider=o["model_provider"],
                        model_name=o["model_name"],
                        model_version=o.get("model_version"),
                        confidence=o.get("confidence"),
                    )
                )

        links = []
        for data in memory_db.evidence_links.values():
            if data.get("claim_id") == str(claim_id) or data.get("claim_id") == claim_id:
                links.append(EvidenceLink.model_validate(data))

        return EvidenceChain(
            claim=claim,
            assets=valid_assets,
            observations=observations,
            evidence_links=links,
        )
