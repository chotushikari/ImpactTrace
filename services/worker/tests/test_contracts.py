import sys
from pathlib import Path

# Ensure repo root and packages directory are in python path for test discovery
repo_root = Path(__file__).resolve().parents[3]
packages_dir = repo_root / "packages"
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))
if str(packages_dir) not in sys.path:
    sys.path.insert(0, str(packages_dir))

from packages.contracts import ProjectCreate, SearchRequest, ClaimType, VerificationStatus


def test_project_create_contract():
    proj = ProjectCreate(
        name="Test Water Infrastructure",
        description="Testing project creation contract",
        objective="Verify contracts work",
        default_lat=26.9124,
        default_lng=75.7873,
    )
    assert proj.name == "Test Water Infrastructure"
    assert proj.default_lat == 26.9124


def test_search_request_contract():
    req = SearchRequest(
        query="water pipeline installation",
        limit=10,
    )
    assert req.query == "water pipeline installation"
    assert req.limit == 10


def test_claim_types():
    assert ClaimType.VERIFIED_FACT.value == "verified_fact"
    assert VerificationStatus.UNVERIFIED.value == "unverified"
