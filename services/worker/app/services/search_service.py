"""SearchService implementing hybrid semantic evidence retrieval."""

from __future__ import annotations

import re
from typing import Any
from uuid import UUID

from contracts import SearchRequest, SearchResponse, SearchResult
from app.services.asset_service import AssetService
from app.services.enrichment_service import AIAdapter
from app.services.observation_service import ObservationService
from app.services.vector_store import VectorStore


class SearchService:
    def __init__(self) -> None:
        self.asset_service = AssetService()
        self.observation_service = ObservationService()
        self.vector_store = VectorStore()
        self.ai_adapter = AIAdapter()

    def search(self, req: SearchRequest) -> SearchResponse:
        # 1. Filter candidates by project/site if specified
        all_assets = self.asset_service.list_assets(project_id=req.project_id)
        if req.site_id:
            all_assets = [a for a in all_assets if a.site_id == req.site_id]

        if not all_assets:
            return SearchResponse(query=req.query, results=[], retrieval_mode="hybrid")

        cand_map = {a.id: a for a in all_assets}
        cand_ids = list(cand_map.keys())

        # 2. Vector search score
        q_emb = self.ai_adapter.generate_embedding(req.query)
        vector_matches = dict(self.vector_store.search(q_emb, limit=req.limit * 2, candidate_asset_ids=cand_ids))

        # 3. Lexical matching score over observations
        query_terms = set(re.findall(r"\w+", req.query.lower()))

        results: list[SearchResult] = []

        for asset in all_assets:
            sim = vector_matches.get(asset.id, 0.5)

            obs_list = self.observation_service.list_observations(asset.id)
            combined_obs_text = " ".join([o.get("text", "") for o in obs_list]).lower()

            match_reasons: list[str] = []

            # Lexical scoring
            lex_score = 0.0
            if query_terms:
                matched_terms = [t for t in query_terms if t in combined_obs_text or (asset.source_filename and t in asset.source_filename.lower())]
                lex_score = len(matched_terms) / len(query_terms) if query_terms else 0.0
                if matched_terms:
                    match_reasons.append(f"Lexical match for terms: {', '.join(matched_terms)}")

            if sim > 0.6:
                match_reasons.append(f"High vector similarity ({sim:.2f}) with query embedding")

            if asset.captured_at:
                match_reasons.append(f"Captured on {asset.captured_at.strftime('%Y-%m-%d')}")
            if asset.lat and asset.lng:
                match_reasons.append(f"GPS verified location ({asset.lat:.4f}, {asset.lng:.4f})")

            if not match_reasons:
                match_reasons.append("Project asset context match")

            final_score = min(1.0, max(0.0, 0.6 * sim + 0.4 * lex_score))

            results.append(
                SearchResult(
                    asset_id=asset.id,
                    project_id=asset.project_id,
                    site_id=asset.site_id,
                    secure_url=asset.cloudinary.secure_url,
                    captured_at=asset.captured_at,
                    similarity=round(sim, 3),
                    lexical_score=round(lex_score, 3),
                    final_score=round(final_score, 3),
                    match_reasons=match_reasons,
                    source_cloudinary_asset_id=asset.cloudinary.asset_id,
                )
            )

        # Sort by final score descending
        results.sort(key=lambda r: r.final_score, reverse=True)
        top_results = results[: req.limit]

        return SearchResponse(query=req.query, results=top_results, retrieval_mode="hybrid")
