"""
pipeline.py — Orchestrator
"""

from __future__ import annotations

import logging

from travel_planner.models import Attraction, TripRequest, TripResponse
from travel_planner.attraction_filter import get_candidate_pool
from travel_planner.route_skeleton import generate_skeletons
from travel_planner.route_validation import validate_all
from travel_planner.llm_enrichment import enrich_routes, generate_trip_description, LLMClient
from travel_planner.assembly import assemble_response

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

    return assemble_response(validated, enrichments, request, len(all_attrs), trip_description)