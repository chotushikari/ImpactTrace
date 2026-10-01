# ImpactTrace — Visual Evidence Intelligence Platform

[![Build & Test](https://img.shields.io/badge/Build-Passing-brightgreen?style=flat-square)](https://github.com/chotushikari/ImpactTrace)
[![Next.js](https://img.shields.io/badge/Next.js-16.3-000000?style=flat-square&logo=nextdotjs)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Cloudinary](https://img.shields.io/badge/Cloudinary-Media_Layer-3448C5?style=flat-square&logo=cloudinary)](https://cloudinary.com/)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL_%2B_pgvector-3ECF8E?style=flat-square&logo=supabase)](https://supabase.com/)
[![Pytest](https://img.shields.io/badge/Tests-9%2F9_Passed-success?style=flat-square&logo=pytest)](https://pytest.org/)

ImpactTrace is an AI-powered media intelligence platform that transforms raw field photos and videos into searchable, auditable visual evidence. It enables program managers, sustainability auditors, and monitoring teams to track ground progress, verify change, and generate evidence-bound reports without metric hallucination.

---

## 🏛 System Architecture & Data Lineage

ImpactTrace enforces a strict separation of concerns across media storage, application metadata, and asynchronous enrichment services.

```text
                                  +---------------------------------------+
                                  |     Browser / Next.js 16 Web App      |
                                  +-------------------+-------------------+
                                                      |
                         Signed Upload / Webhook      | REST API Gateway
                                                      v
     +-----------------------+              +-------------------+              +-----------------------+
     |   Cloudinary Storage  | <--------->  |   Python Worker   | <--------->  |  Supabase PostgreSQL  |
     | (Canonical Media Hub) |              | (FastAPI Service) |              |  (Relational + Vector)|
     +-----------------------+              +---------+---------+              +-----------------------+
                                                      |
                                       +--------------+--------------+
                                       |  AI Enrichment Pipeline     |
                                       |  • EXIF / GPS Extraction     |
                                       |  • Tesseract OCR Engine     |
                                       |  • VLM Scene Analysis       |
                                       |  • 768-dim Vector Indexing  |
                                       |  • ORB Feature Alignment    |
                                       +-----------------------------+
```

### Source-of-Truth Principles

1. **Cloudinary**: Acts as the canonical source for original media binaries, signed uploads, thumbnail transformations, and media public IDs.
2. **PostgreSQL + pgvector**: Stores application state, geospatial metadata, observations, vector embeddings, before/after relations, and claim lineage graphs.
3. **Python Worker Service**: Executes asynchronous enrichment jobs, feature alignment, hybrid search scoring, and dossier generation.

---

## ⚡ Key Capabilities & Feature Map

### 1. Multi-Site Project Workspaces
Organize field assets under dedicated project containers configured with geocoordinates, site boundaries, and operational objectives.

### 2. Cloudinary Signed Media Ingestion
Direct browser-to-Cloudinary uploads using cryptographic SHA-1 signature tokens. Original Cloudinary asset IDs, public IDs, and revision versions are preserved in the PostgreSQL asset registry.

### 3. Asynchronous AI Enrichment Pipeline
On asset creation, worker jobs execute automated multi-modal extraction:
- **Spatial/Temporal**: EXIF timestamp and GPS coordinate extraction.
- **OCR Engine**: Text extraction from project banners, signs, and equipment.
- **Vision-Language Model (VLM)**: Automated scene captioning and tag generation.
- **Vector Embedding**: 768-dimensional normalized CLIP vector generation.

### 4. Hybrid Semantic Evidence Search
Natural language query engine leveraging hybrid score fusion:
$$\text{Final Score} = 0.6 \times \text{Vector Similarity} + 0.4 \times \text{Lexical OCR Score}$$
Filters assets by project, site, and date range while providing transparent match reasoning.

### 5. Before / After Visual Comparison
Compares baseline vs current site media:
- Image feature alignment using **ORB Homography**.
- SSIM difference computation.
- VLM comparative analysis returning structural change observations with confidence and limitation metrics.

### 6. Auditable Evidence Graph
Establishes clear provenance chains for every statement:
- `verified_fact`: Ground truth data sourced from project logs.
- `ai_observation`: Model-generated observations with confidence scores.
- `inference`: Synthesized conclusion linked to specific Cloudinary public IDs.

### 7. Audit-Constrained Impact Dossiers
Generates structured **Impact Dossiers** and campaign reports bound strictly to verified source media assets. LLM prompts prohibit unverified metric hallucination.

---

## 📋 Sprint Execution Roadmap

| Sprint | Scope | Key Deliverables | Verification |
|---|---|---|:---:|
| **Sprint 00** | Research & Bootstrap | Environment configuration, Pydantic contracts | Passed |
| **Sprint 01** | Domain Foundations | Database schema (`projects`, `sites`, `assets`, `claims`) & CRUD services | Passed |
| **Sprint 02** | Cloudinary Ingestion | Signed upload API, webhook verification, Cloudinary ref preservation | Passed |
| **Sprint 03** | AI Enrichment | EXIF, Tesseract OCR, VLM captioning, 768-dim CLIP vector store | Passed |
| **Sprint 04** | Hybrid Search | Vector similarity + lexical score fusion API | Passed |
| **Sprint 05** | Visual Comparison | ORB alignment, difference scoring, VLM change detection | Passed |
| **Sprint 06** | Evidence Graph | Claim lineage, evidence links, provenance tracing | Passed |
| **Sprint 07** | Impact Dossiers | Audit-constrained report generation & campaign copy | Passed |
| **Sprint 08** | Production Polish | Next.js dark mode UI, build optimization, test suite | Passed |

---

## 🛠 Local Setup & Development Guide

### Prerequisites
- Node.js >= 20.0.0
- Python >= 3.11.0
- Git

### 1. Python Worker Service
```bash
cd repo/services/worker

# Create and activate virtual environment
python -m venv .venv
# On Windows: .venv\Scripts\activate
# On Linux/macOS: source .venv/bin/activate

# Install dependencies in editable mode
pip install -e .

# Run pytest test suite
pytest

# Start FastAPI worker service
python -m uvicorn app.main:app --reload --port 8001
```

### 2. Next.js Web Application
```bash
cd repo/apps/web

# Install dependencies
npm install

# Run development server
npm run dev
```

The web interface will be accessible at [http://localhost:3000](http://localhost:3000).

---

## 🧪 Testing & Verification

Run the full integration test suite covering all services and API routes:

```bash
cd repo/services/worker
pytest -v
```

**Test Coverage Summary:**
- `test_contracts.py`: Validates Pydantic schemas and serialization invariants.
- `test_health.py`: Verifies FastAPI health check endpoints.
- `test_services.py`: Tests project, asset, observation, evidence, and vector store CRUD.
- `test_all_sprints.py`: End-to-end integration test covering the complete pipeline.

---

## 📄 License

This project is licensed under the MIT License.
