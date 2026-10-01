"""Comprehensive test suite verifying Sprint 00 to Sprint 08 workflows."""

from uuid import uuid4

import pytest
from contracts import (
    ClaimCreate,
    ClaimType,
    CloudinaryAssetRef,
    CompareRequest,
    ProjectCreate,
    ReportRequest,
    SearchRequest,
    StoryRequest,
    VerificationStatus,
)
from app.db import memory_db
from app.services.asset_service import AssetService
from app.services.cloudinary_service import CloudinaryService
from app.services.comparison_service import ComparisonService
from app.services.enrichment_service import EnrichmentService
from app.services.evidence_service import EvidenceService
from app.services.project_service import ProjectService
from app.services.report_service import ReportService
from app.services.search_service import SearchService


@pytest.fixture(autouse=True)
def reset_db():
    memory_db.clear()
    yield
    memory_db.clear()


def test_full_hackathon_end_to_end_flow():
    # 1. Sprint 01: Project Creation
    proj_svc = ProjectService()
    proj = proj_svc.create_project(
        ProjectCreate(
            name="Jaipur Water Infrastructure",
            description="Clean drinking water pipeline installation",
            objective="Provide water access to 5000 households",
            default_lat=26.9124,
            default_lng=75.7873,
        )
    )
    pid = proj["id"]
    assert pid is not None

    # 2. Sprint 02: Cloudinary Upload Signature & Ingestion
    c_svc = CloudinaryService()
    sign_params = c_svc.generate_signed_upload_params(pid)
    assert "signature" in sign_params
    assert "upload_preset" in sign_params

    asset_svc = AssetService()
    ref_before = CloudinaryAssetRef(
        asset_id="c_pipe_before_100",
        public_id="impacttrace/projects/jaipur/pipe_before",
        resource_type="image",
        secure_url="https://res.cloudinary.com/demo/image/upload/pipe_before.jpg",
    )
    before_asset = asset_svc.create_asset(
        project_id=pid,
        cloudinary_ref=ref_before,
        source_filename="jaipur_pipe_before.jpg",
        lat=26.9124,
        lng=75.7873,
        status="queued",
    )

    ref_after = CloudinaryAssetRef(
        asset_id="c_pipe_after_200",
        public_id="impacttrace/projects/jaipur/pipe_after",
        resource_type="image",
        secure_url="https://res.cloudinary.com/demo/image/upload/pipe_after.jpg",
    )
    after_asset = asset_svc.create_asset(
        project_id=pid,
        cloudinary_ref=ref_after,
        source_filename="jaipur_pipe_after.jpg",
        lat=26.9125,
        lng=75.7874,
        status="queued",
    )

    # 3. Sprint 03: AI Enrichment Pipeline
    enrich_svc = EnrichmentService()
    res_b = enrich_svc.enrich_asset(before_asset.id)
    res_a = enrich_svc.enrich_asset(after_asset.id)
    assert res_b["status"] == "ready"
    assert res_a["status"] == "ready"

    # 4. Sprint 04: Hybrid Semantic Evidence Search
    search_svc = SearchService()
    search_res = search_svc.search(
        SearchRequest(
            query="water pipeline installation jaipur",
            project_id=pid,
            limit=5,
        )
    )
    assert len(search_res.results) == 2
    assert search_res.results[0].final_score > 0.0

    # 5. Sprint 05: Before/After Comparison Engine
    comp_svc = ComparisonService()
    comp_res = comp_svc.compare_assets(
        CompareRequest(
            before_asset_id=before_asset.id,
            after_asset_id=after_asset.id,
            target="water pipe",
        )
    )
    assert comp_res.alignment.reliable is True
    assert len(comp_res.changes) > 0
    assert comp_res.relation_id is not None

    # 6. Sprint 06: Evidence Chain & Claim Lineage
    ev_svc = EvidenceService()
    claim = ev_svc.create_claim(
        ClaimCreate(
            project_id=pid,
            text="Water pipeline installation completed at Site 01 Jaipur",
            claim_type=ClaimType.AI_OBSERVATION,
            verification_status=VerificationStatus.HUMAN_VERIFIED,
            confidence=0.95,
            evidence_asset_ids=[before_asset.id, after_asset.id],
            relation_ids=[comp_res.relation_id],
        )
    )
    chain = ev_svc.get_evidence_chain(claim.id)
    assert chain is not None
    assert len(chain.assets) == 2

    # 7. Sprint 07: Impact Dossier & Story Generation
    rep_svc = ReportService()
    dossier = rep_svc.generate_dossier(
        ReportRequest(
            project_id=pid,
            claim_ids=[claim.id],
            relation_ids=[comp_res.relation_id],
            asset_ids=[before_asset.id, after_asset.id],
            title="Jaipur Water Infrastructure Dossier",
        )
    )
    assert dossier["title"] == "Jaipur Water Infrastructure Dossier"
    assert len(dossier["source_manifest"]["cloudinary_asset_ids"]) == 2

    story = rep_svc.generate_story(
        StoryRequest(
            project_id=pid,
            asset_ids=[before_asset.id, after_asset.id],
            format="donor_update",
        )
    )
    assert "Jaipur Water Infrastructure" in story["content"]
    assert story["source_asset_count"] == 2
