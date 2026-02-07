"""
pipeline.py — Orchestrator
"""

from __future__ import annotations

import logging

from models import Attraction, TripRequest, TripResponse
from attraction_filter import get_candidate_pool
from route_skeleton import generate_skeletons
from route_validation import validate_all
from llm_enrichment import enrich_routes, LLMClient
from assembly import assemble_response

logger = logging.getLogger(__name__)


async def generate_trip_plans(attractions, request, llm):
    must_visit, candidates = get_candidate_pool(attractions, request)
    all_attrs = must_visit + candidates
    if not all_attrs:
        return assemble_response([], [], request, 0)

    graph, skeletons = generate_skeletons(
        request.start_point, request.end_point,
        must_visit, candidates, request,
    )

    validated = validate_all(skeletons, graph, must_visit, candidates, request)
    if not validated:
        return assemble_response([], [], request, len(all_attrs))

    enrichments = await enrich_routes(validated, request, all_attrs, llm)
    
    trip_description = await generate_trip_description(validated, request, all_attrs, llm)

    return assemble_response(validated, enrichments, request, len(all_attrs))