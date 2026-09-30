"""ImpactTrace API and domain contracts.

The contracts are intentionally implementation-neutral so the same shapes can be
used by a FastAPI worker and validated from the web application.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class ClaimType(str, Enum):
    VERIFIED_FACT = "verified_fact"
    AI_OBSERVATION = "ai_observation"
    INFERENCE = "inference"


class VerificationStatus(str, Enum):
    UNVERIFIED = "unverified"
    HUMAN_VERIFIED = "human_verified"
    REJECTED = "rejected"


class ObservationType(str, Enum):
    CAPTION = "caption"
    TAGS = "tags"
    OCR = "ocr"
    SCENE = "scene"
    LOCATION = "location"
    CHANGE = "change"
    ACTIVITY = "activity"


class ProjectCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=2, max_length=160)
    description: str | None = Field(default=None, max_length=4000)
    objective: str | None = Field(default=None, max_length=4000)
    default_lat: float | None = Field(default=None, ge=-90, le=90)
    default_lng: float | None = Field(default=None, ge=-180, le=180)


class SiteCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    project_id: UUID
    name: str = Field(min_length=1, max_length=160)
    address: str | None = Field(default=None, max_length=500)
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)
    geocode_source: str | None = None


class CloudinaryAssetRef(BaseModel):
    model_config = ConfigDict(extra="forbid")
    asset_id: str = Field(min_length=1)
    public_id: str = Field(min_length=1)
    resource_type: Literal["image", "video", "raw"]
    version: int | None = Field(default=None, ge=0)
    format: str | None = None
    secure_url: HttpUrl


class AssetRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID
    project_id: UUID
    site_id: UUID | None
    cloudinary: CloudinaryAssetRef
    source_filename: str | None
    captured_at: datetime | None
    captured_at_source: str | None
    uploaded_at: datetime
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)
    location_source: str | None
    duration_seconds: float | None = Field(default=None, ge=0)
    status: Literal["queued", "processing", "ready", "failed"]


class AIResultEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")
    provider: str
    model: str
    model_version: str | None = None
    prompt_version: str = "v1"
    created_at: datetime
    confidence: float | None = Field(default=None, ge=0, le=1)
    source_asset_ids: list[UUID] = Field(min_length=1)
    observation_type: ObservationType
    content: dict[str, Any]


class ObservationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    asset_id: UUID
    type: ObservationType
    text: str | None = None
    structured_json: dict[str, Any] = Field(default_factory=dict)
    model_provider: str
    model_name: str
    model_version: str | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)


class SearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(min_length=3, max_length=1000)
    project_id: UUID | None = None
    site_id: UUID | None = None
    activity: str | None = None
    phase: str | None = None
    start: datetime | None = None
    end: datetime | None = None
    limit: int = Field(default=8, ge=1, le=50)

    @field_validator("end")
    @classmethod
    def validate_range(cls, value: datetime | None, info):
        start = info.data.get("start")
        if value and start and value < start:
            raise ValueError("end must be >= start")
        return value


class SearchResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    asset_id: UUID
    project_id: UUID
    site_id: UUID | None
    secure_url: HttpUrl
    captured_at: datetime | None
    similarity: float = Field(ge=0, le=1)
    lexical_score: float = Field(default=0, ge=0, le=1)
    final_score: float = Field(ge=0, le=1)
    match_reasons: list[str]
    source_cloudinary_asset_id: str


class SearchResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str
    results: list[SearchResult]
    retrieval_mode: Literal["hybrid", "vector", "lexical", "retrieval_only"]


class CompareRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    before_asset_id: UUID
    after_asset_id: UUID
    target: str | None = Field(default=None, max_length=240)


class AlignmentInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    method: str
    score: float = Field(ge=0, le=1)
    reliable: bool
    message: str | None = None


class ChangeObservation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["addition", "removal", "movement", "structural", "condition", "uncertain"]
    description: str
    confidence: float = Field(ge=0, le=1)
    method: str


class CompareResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    relation_id: UUID
    before_asset_id: UUID
    after_asset_id: UUID
    alignment: AlignmentInfo
    diff_preview_url: HttpUrl | None = None
    changes: list[ChangeObservation]
    limitations: list[str]
    source_asset_ids: list[UUID] = Field(min_length=2)


class ClaimCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    project_id: UUID
    text: str = Field(min_length=5, max_length=2000)
    claim_type: ClaimType
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    confidence: float | None = Field(default=None, ge=0, le=1)
    evidence_asset_ids: list[UUID] = Field(min_length=1)
    observation_ids: list[UUID] = Field(default_factory=list)
    relation_ids: list[UUID] = Field(default_factory=list)


class ClaimRecord(ClaimCreate):
    id: UUID
    created_at: datetime


class EvidenceLink(BaseModel):
    model_config = ConfigDict(extra="forbid")
    claim_id: UUID
    asset_id: UUID | None = None
    observation_id: UUID | None = None
    relation_id: UUID | None = None
    role: str


class EvidenceChain(BaseModel):
    model_config = ConfigDict(extra="forbid")
    claim: ClaimRecord
    assets: list[AssetRecord]
    observations: list[ObservationCreate]
    evidence_links: list[EvidenceLink]


class ReportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    project_id: UUID
    claim_ids: list[UUID] = Field(default_factory=list)
    relation_ids: list[UUID] = Field(default_factory=list)
    asset_ids: list[UUID] = Field(min_length=1)
    title: str = Field(default="Impact Dossier", max_length=200)


class StoryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    project_id: UUID
    asset_ids: list[UUID] = Field(min_length=1)
    claim_ids: list[UUID] = Field(default_factory=list)
    format: Literal["donor_update", "social_post", "project_summary"]
