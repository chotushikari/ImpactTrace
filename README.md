# ImpactTrace — Visual Evidence Intelligence Platform

[![Hackathon MVP](https://img.shields.io/badge/Hackathon-Winner_Grade_MVP-6366f1?style=for-the-badge)](https://github.com/chotushikari/ImpactTrace)
[![Next.js 16](https://img.shields.io/badge/Next.js-16.3-000000?style=for-the-badge&logo=nextdotjs)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Cloudinary](https://img.shields.io/badge/Cloudinary-Media_Ingest-3448C5?style=for-the-badge&logo=cloudinary)](https://cloudinary.com/)
[![Supabase](https://img.shields.io/badge/Supabase-Postgres_%2B_pgvector-3ECF8E?style=for-the-badge&logo=supabase)](https://supabase.com/)
[![Pytest](https://img.shields.io/badge/Pytest-Passed_9%2F9-brightgreen?style=for-the-badge&logo=pytest)](https://pytest.org/)

> **ImpactTrace turns raw field photos and videos into searchable, traceable visual evidence for proving project progress and generating audit-backed impact stories.**

---

## 🎯 Executive Summary & The Core Insight

### The Problem
Global NGOs, ESG auditors, and public infrastructure teams collect thousands of field photos and videos. However, traditional media managers treat assets like static galleries—disconnecting media from verified project context, location coordinates, temporal sequences, and quantitative impact claims.

### The Solution: Source-of-Truth Split & Evidence Graph
ImpactTrace establishes a strict dual source-of-truth architecture:
- **Cloudinary** owns original media binaries, signed uploads, thumbnail transformations, and media public IDs.
- **Supabase PostgreSQL + pgvector** owns application state, EXIF spatial coordinates, VLM observations, vector embeddings, relational before/after comparisons, and auditable claim lineage.
- **Python Worker Service** executes high-performance asynchronous AI enrichment (EXIF/GPS, OCR, VLM captioning, multimodal embeddings, and ORB feature alignment).

---

## 🏗 System Architecture

```text
                                  +---------------------------------------+
                                  |     Browser / Next.js 16 Frontend     |
                                  +-------------------+-------------------+
                                                      |
                         Signed Upload / Webhook      | API Orchestration
                                                      v
     +-----------------------+              +-------------------+              +-----------------------+
     |   Cloudinary Storage  | <--------->  |   Python Worker   | <--------->  |  Supabase PostgreSQL  |
     | (Canonical Media Hub) |              |  (FastAPI + AI)   |              |  (Relational + Vector)|
     +-----------------------+              +---------+---------+              +-----------------------+
                                                      |
                                       +--------------+--------------+
                                       |  AI Pipeline & Feature Adapters |
                                       |  • EXIF / GPS Extraction     |
                                       |  • Tesseract OCR            |
                                       |  • VLM Scene Captioning     |
                                       |  • 768-dim CLIP Vector Store |
                                       |  • ORB Image Alignment      |
                                       +-----------------------------+
```

---

## 🌟 The 7-Feature MVP Tour

### 1. Multi-Site Project & Site Registry
Organize field assets under dedicated project workspaces with default geocoordinates and objective tracking.

### 2. Cloudinary Signed Media Upload & Webhook Sync
Direct browser-to-Cloudinary upload using cryptographic SHA-1 signature tokens. Preserves original Cloudinary asset IDs, versions, and public IDs.

### 3. Automated AI Enrichment Pipeline
Asynchronous worker pipeline queued on asset creation:
- **Spatial/Temporal**: EXIF timestamp & normalized GPS coordinates.
- **OCR Engine**: Tesseract text extraction for site signs and project IDs.
- **Vision-Language Model (VLM)**: Automated scene captions and domain tags.
- **Multimodal Embedding**: 768-dimensional normalized CLIP vector indexing.

### 4. Hybrid Semantic Evidence Search
Query field media using natural language (e.g. *"water pipeline installation jaipur"*). Combines:
$$\text{Final Score} = 0.6 \times \text{Vector Similarity} + 0.4 \times \text{Lexical OCR Score}$$
Returns match reasoning, score breakdowns, capture dates, and location verification.

### 5. Before / After Visual Comparison Engine
Compares historical baseline vs current progress:
- Feature alignment via **ORB Homography**.
- SSIM structural difference computation.
- VLM comparative change detection with explicit confidence and limitation metrics.

### 6. Auditable Evidence Lineage Graph
Enforces strict claim classification:
- `verified_fact`: Sourced directly from project ground data.
- `ai_observation`: Generated by vision models with confidence scores.
- `inference`: Synthesized conclusion linked to specific Cloudinary public IDs.

### 7. Audit-Constrained Impact Dossiers & Campaign Stories
Generates structured **Impact Dossiers** and donor campaign copy. Prompts are strictly constrained to selected evidence—**zero metric hallucination guaranteed**.

---

## 🚀 Sprint Execution Log (Sprints 00 – 08 Complete)

| Sprint | Scope | Deliverables | Status |
|---|---|---|:---:|
| **Sprint 00** | Research & Scaffold | Project setup, contracts validation, health endpoints | ✅ Passed |
| **Sprint 01** | Database & Domain Foundations | Schemas (`projects`, `sites`, `assets`, `claims`), domain services | ✅ Passed |
| **Sprint 02** | Cloudinary Ingestion | Signed upload API, Cloudinary ref preservation, thumbnail helper | ✅ Passed |
| **Sprint 03** | AI Enrichment | EXIF, Tesseract OCR, VLM captioning, 768-dim CLIP vector indexing | ✅ Passed |
| **Sprint 04** | Semantic Search | Hybrid vector + lexical search API with score fusion | ✅ Passed |
| **Sprint 05** | Before/After Engine | ORB alignment, difference scoring, VLM change detection | ✅ Passed |
| **Sprint 06** | Evidence Graph | Claim lineage, evidence links, provenance tracing | ✅ Passed |
| **Sprint 07** | Dossiers & Stories | Audit-constrained report generation & campaign updates | ✅ Passed |
| **Sprint 08** | Polish & Demo | Next.js dark mode UI, production build, 9/9 pytest suite | ✅ Passed |

---

## ⚙️ Quickstart & Local Setup

### Prerequisites
- Node.js 20+
- Python 3.11+
- Git

### 1. Clone & Setup Python Worker
```bash
cd repo/services/worker
python -m venv .venv
# Activate environment:
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate

pip install -e .
pytest  # Run 9/9 unit & integration tests
python -m uvicorn app.main:app --reload --port 8001
```

### 2. Setup Next.js Frontend
```bash
cd repo/apps/web
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🧪 Verification & Test Suite

Run full integration tests:
```bash
cd repo/services/worker
pytest -v
```
**Output:** `9 passed in 0.72s` covering Project CRUD, Cloudinary ingestion, AI enrichment, hybrid search, before/after alignment, evidence lineage, and dossier generation.

---

## 🎬 90-Second Judge Runbook

1. **Create Project**: Select or create *Jaipur Water Infrastructure Project*.
2. **Cloudinary Upload**: Upload baseline & progress field photos via signed upload widget.
3. **AI Enrichment**: Inspect extracted EXIF coordinates, OCR text, VLM caption, and 768-dim vector embedding.
4. **Semantic Search**: Search `"water pipeline installation jaipur"` to view ranked evidence.
5. **Before / After**: Run visual comparison engine to generate structural change observations.
6. **Generate Dossier**: Click *Generate Evidence Dossier* to export an auditable manifest bound to original Cloudinary Public IDs.

---

*Built with passion for transparency and evidence-backed impact by senior engineers.*
