"""ImpactTrace Worker FastAPI Application."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel

from contracts import (
    ClaimCreate,
    ClaimRecord,
    CloudinaryAssetRef,
    CompareRequest,
    CompareResponse,
    EvidenceChain,
    ProjectCreate,
    ReportRequest,
    SearchRequest,
    SearchResponse,
    SiteCreate,
    StoryRequest,
)
from app.services.asset_service import AssetService
from app.services.cloudinary_service import CloudinaryService
from app.services.comparison_service import ComparisonService
from app.services.enrichment_service import EnrichmentService
from app.services.evidence_service import EvidenceService
from app.services.project_service import ProjectService
from app.services.report_service import ReportService
from app.services.search_service import SearchService

app = FastAPI(title="ImpactTrace Worker API", version="1.0.0")

project_service = ProjectService()
asset_service = AssetService()
cloudinary_service = CloudinaryService()
enrichment_service = EnrichmentService()
search_service = SearchService()
comparison_service = ComparisonService()
evidence_service = EvidenceService()
report_service = ReportService()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "worker"}


# --- Projects & Sites ---
@app.post("/api/projects", status_code=status.HTTP_201_CREATED)
async def create_project(data: ProjectCreate) -> dict:
    return project_service.create_project(data)


@app.get("/api/projects/{project_id}")
async def get_project(project_id: UUID) -> dict:
    proj = project_service.get_project(project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    return proj


@app.get("/api/projects")
async def list_projects() -> list[dict]:
    return project_service.list_projects()


@app.post("/api/sites", status_code=status.HTTP_201_CREATED)
async def create_site(data: SiteCreate) -> dict:
    return project_service.create_site(data)


@app.get("/api/projects/{project_id}/sites")
async def list_sites(project_id: UUID) -> list[dict]:
    return project_service.list_sites(project_id)


# --- Cloudinary & Assets ---
class CloudinarySignRequest(BaseModel):
    project_id: UUID
    site_id: UUID | None = None


@app.post("/api/cloudinary/sign")
async def sign_upload(req: CloudinarySignRequest) -> dict:
    return cloudinary_service.generate_signed_upload_params(req.project_id, req.site_id)


class RegisterAssetRequest(BaseModel):
    project_id: UUID
    site_id: UUID | None = None
    cloudinary: CloudinaryAssetRef
    source_filename: str | None = None
    lat: float | None = None
    lng: float | None = None
    location_source: str | None = None


@app.post("/api/assets", status_code=status.HTTP_201_CREATED)
async def register_asset(req: RegisterAssetRequest) -> dict:
    asset = asset_service.create_asset(
        project_id=req.project_id,
        site_id=req.site_id,
        cloudinary_ref=req.cloudinary,
        source_filename=req.source_filename,
        lat=req.lat,
        lng=req.lng,
        location_source=req.location_source,
        status="queued",
    )
    # Trigger async enrichment
    enrichment_service.enrich_asset(asset.id)
    return asset.model_dump(mode="json")


@app.get("/api/assets/{asset_id}")
async def get_asset(asset_id: UUID) -> dict:
    asset = asset_service.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset.model_dump(mode="json")


@app.get("/api/projects/{project_id}/assets")
async def list_assets(project_id: UUID) -> list[dict]:
    assets = asset_service.list_assets(project_id)
    return [a.model_dump(mode="json") for a in assets]


@app.post("/api/assets/{asset_id}/enrich")
async def enrich_asset(asset_id: UUID) -> dict:
    res = enrichment_service.enrich_asset(asset_id)
    if res.get("status") == "error":
        raise HTTPException(status_code=404, detail=res.get("message"))
    return res


# --- Search & Comparison ---
@app.post("/api/search")
async def search_evidence(req: SearchRequest) -> SearchResponse:
    return search_service.search(req)


@app.post("/api/compare")
async def compare_assets(req: CompareRequest) -> CompareResponse:
    try:
        return comparison_service.compare_assets(req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Claims & Evidence Graph ---
@app.post("/api/claims", status_code=status.HTTP_201_CREATED)
async def create_claim(data: ClaimCreate) -> ClaimRecord:
    return evidence_service.create_claim(data)


@app.get("/api/claims/{claim_id}")
async def get_claim(claim_id: UUID) -> ClaimRecord:
    claim = evidence_service.get_claim(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim


@app.get("/api/projects/{project_id}/claims")
async def list_claims(project_id: UUID) -> list[ClaimRecord]:
    return evidence_service.list_claims(project_id)


@app.get("/api/claims/{claim_id}/evidence-chain")
async def get_evidence_chain(claim_id: UUID) -> EvidenceChain:
    chain = evidence_service.get_evidence_chain(claim_id)
    if not chain:
        raise HTTPException(status_code=404, detail="Evidence chain not found")
    return chain


# --- Reports & Story Generation ---
@app.post("/api/reports", status_code=status.HTTP_201_CREATED)
async def generate_report(req: ReportRequest) -> dict:
    try:
        return report_service.generate_dossier(req)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/stories", status_code=status.HTTP_201_CREATED)
async def generate_story(req: StoryRequest) -> dict:
    try:
        return report_service.generate_story(req)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
