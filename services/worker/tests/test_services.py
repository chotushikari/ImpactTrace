"""Tests for Sprint 01 domain services and CRUD operations."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from contracts import (
    ClaimCreate,
    ClaimType,
    CloudinaryAssetRef,
    ObservationCreate,
    ObservationType,
    ProjectCreate,
    SiteCreate,
    VerificationStatus,
)
from app.db import memory_db
from app.services.asset_service import AssetService
from app.services.evidence_service import EvidenceService
from app.services.observation_service import ObservationService
from app.services.project_service import ProjectService
from app.services.vector_store import VectorStore, cosine_similarity


@pytest.fixture(autouse=True)
def reset_db():
    memory_db.clear()
    yield
    memory_db.clear()


def test_project_crud():
    svc = ProjectService()
    p_data = ProjectCreate(
        name="Jaipur Water Infrastructure",
        description="Pipeline installation project",
        objective="Clean drinking water supply",
        default_lat=26.9124,
        default_lng=75.7873,
    )
    proj = svc.create_project(p_data)
    assert proj["name"] == "Jaipur Water Infrastructure"
    assert "id" in proj

    pid = proj["id"]
    fetched = svc.get_project(pid)
    assert fetched is not None
    assert fetched["name"] == "Jaipur Water Infrastructure"

    all_projs = svc.list_projects()
    assert len(all_projs) == 1

    s_data = SiteCreate(
        project_id=pid,
        name="Site 01 - Pipeline North",
        lat=26.9150,
        lng=75.7890,
    )
    site = svc.create_site(s_data)
    assert site["name"] == "Site 01 - Pipeline North"

    sites = svc.list_sites(pid)
    assert len(sites) == 1


def test_asset_and_observation_crud():
    proj_svc = ProjectService()
    asset_svc = AssetService()
    obs_svc = ObservationService()

    proj = proj_svc.create_project(ProjectCreate(name="Test Project"))
    pid = proj["id"]

    ref = CloudinaryAssetRef(
        asset_id="c_asset_100",
        public_id="impacttrace/projects/p1/site1/pipe_01",
        resource_type="image",
        secure_url="https://res.cloudinary.com/demo/image/upload/pipe_01.jpg",
    )

    asset = asset_svc.create_asset(
        project_id=pid,
        cloudinary_ref=ref,
        source_filename="pipe_01.jpg",
        lat=26.9124,
        lng=75.7873,
        status="queued",
    )

    assert asset.status == "queued"
    assert asset.cloudinary.asset_id == "c_asset_100"

    updated = asset_svc.update_status(asset.id, "ready")
    assert updated.status == "ready"

    obs_data = ObservationCreate(
        asset_id=asset.id,
        type=ObservationType.CAPTION,
        text="A blue water pipe being positioned in trench",
        structured_json={"tags": ["water", "pipe", "trench"]},
        model_provider="local",
        model_name="lfm2_vl",
        confidence=0.92,
    )

    obs = obs_svc.create_observation(obs_data)
    assert obs["asset_id"] == str(asset.id)
    assert obs["confidence"] == 0.92

    obs_list = obs_svc.list_observations(asset.id)
    assert len(obs_list) == 1


def test_evidence_chain():
    proj_svc = ProjectService()
    asset_svc = AssetService()
    obs_svc = ObservationService()
    evidence_svc = EvidenceService()

    proj = proj_svc.create_project(ProjectCreate(name="Evidence Test"))
    pid = proj["id"]

    ref = CloudinaryAssetRef(
        asset_id="c_asset_200",
        public_id="pipe_installed_01",
        resource_type="image",
        secure_url="https://res.cloudinary.com/demo/image/upload/pipe_installed_01.jpg",
    )
    asset = asset_svc.create_asset(project_id=pid, cloudinary_ref=ref, status="ready")

    obs = obs_svc.create_observation(
        ObservationCreate(
            asset_id=asset.id,
            type=ObservationType.CAPTION,
            text="Completed pipe line section",
            model_provider="local",
            model_name="test_model",
        )
    )

    claim = evidence_svc.create_claim(
        ClaimCreate(
            project_id=pid,
            text="500m of water pipeline installed at Site 01",
            claim_type=ClaimType.AI_OBSERVATION,
            verification_status=VerificationStatus.UNVERIFIED,
            confidence=0.89,
            evidence_asset_ids=[asset.id],
            observation_ids=[obs["id"]],
        )
    )

    assert claim.id is not None

    chain = evidence_svc.get_evidence_chain(claim.id)
    assert chain is not None
    assert chain.claim.text == "500m of water pipeline installed at Site 01"
    assert len(chain.assets) == 1
    assert chain.assets[0].id == asset.id


def test_vector_store():
    store = VectorStore()
    aid1 = uuid4()
    aid2 = uuid4()

    v1 = [1.0, 0.0, 0.0]
    v2 = [0.0, 1.0, 0.0]
    q = [0.9, 0.1, 0.0]

    store.add_embedding(aid1, "image", "clip", v1)
    store.add_embedding(aid2, "image", "clip", v2)

    res = store.search(q, limit=2)
    assert len(res) == 2
    assert res[0][0] == aid1
    assert res[0][1] > res[1][1]
