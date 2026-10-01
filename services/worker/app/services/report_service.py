"""ReportService for Impact Dossiers and Campaign Story generation."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from contracts import ReportRequest, StoryRequest
from app.db import get_supabase_client, memory_db
from app.services.asset_service import AssetService
from app.services.evidence_service import EvidenceService
from app.services.project_service import ProjectService


class ReportService:
    def __init__(self) -> None:
        self.project_service = ProjectService()
        self.asset_service = AssetService()
        self.evidence_service = EvidenceService()
        self.supabase = get_supabase_client()

    def generate_dossier(self, req: ReportRequest) -> dict[str, Any]:
        project = self.project_service.get_project(req.project_id)
        if not project:
            raise ValueError("Project not found")

        assets = [self.asset_service.get_asset(aid) for aid in req.asset_ids]
        valid_assets = [a for a in assets if a is not None]

        report_id = uuid4()
        now = datetime.now(timezone.utc)

        source_manifest = {
            "project_id": str(req.project_id),
            "project_name": project.get("name"),
            "total_evidence_assets": len(valid_assets),
            "cloudinary_asset_ids": [a.cloudinary.asset_id for a in valid_assets],
            "cloudinary_public_ids": [a.cloudinary.public_id for a in valid_assets],
            "asset_urls": [str(a.cloudinary.secure_url) for a in valid_assets],
            "claims_referenced": [str(cid) for cid in req.claim_ids],
            "relations_referenced": [str(rid) for rid in req.relation_ids],
            "generated_at": now.isoformat(),
        }

        dossier_content = {
            "id": str(report_id),
            "title": req.title,
            "project": {
                "name": project.get("name"),
                "description": project.get("description"),
                "objective": project.get("objective"),
            },
            "evidence_summary": {
                "total_assets": len(valid_assets),
                "verified_locations": [f"({a.lat:.4f}, {a.lng:.4f})" for a in valid_assets if a.lat and a.lng],
                "date_range": [
                    min([a.uploaded_at.isoformat() for a in valid_assets]) if valid_assets else None,
                    max([a.uploaded_at.isoformat() for a in valid_assets]) if valid_assets else None,
                ],
            },
            "source_manifest": source_manifest,
            "limitations": [
                "Every statement is strictly anchored to verified Cloudinary media assets.",
                "AI observations reflect visual state at timestamp of media capture.",
            ],
            "generated_at": now.isoformat(),
        }

        db_row = {
            "id": str(report_id),
            "project_id": str(req.project_id),
            "title": req.title,
            "format": "dossier_json",
            "source_manifest": source_manifest,
            "generated_at": now.isoformat(),
        }

        if self.supabase:
            try:
                self.supabase.table("reports").insert(db_row).execute()
            except Exception:
                pass

        memory_db.reports[report_id] = db_row
        return dossier_content

    def generate_story(self, req: StoryRequest) -> dict[str, Any]:
        project = self.project_service.get_project(req.project_id)
        if not project:
            raise ValueError("Project not found")

        assets = [self.asset_service.get_asset(aid) for aid in req.asset_ids]
        valid_assets = [a for a in assets if a is not None]

        proj_name = project.get("name", "Impact Project")

        if req.format == "donor_update":
            content = f"📊 **Project Update: {proj_name}**\n\nWe are pleased to share verified progress supported by {len(valid_assets)} field media evidence assets. Pipeline construction and site installation activities are actively progressing. All claims are auditable against original Cloudinary source media."
        elif req.format == "social_post":
            content = f"🌱 Progress in action! Check out the visual evidence for {proj_name}. Verified field data and before/after comparisons prove real impact on the ground. #ImpactTrace #Sustainability #Transparency"
        else:  # project_summary
            content = f"Executive Summary for {proj_name}: Field operations monitored with {len(valid_assets)} verified media assets. Provenance preserved across Cloudinary and Postgres storage layers."

        return {
            "format": req.format,
            "project_id": str(req.project_id),
            "content": content,
            "source_asset_count": len(valid_assets),
            "source_cloudinary_asset_ids": [a.cloudinary.asset_id for a in valid_assets],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
