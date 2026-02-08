"""
assembly.py — Module 5: Response Assembly
"""

from __future__ import annotations

import logging
import uuid
import datetime

from travel_planner.models import (
     RoutePlan, TimelineEntry, TripResponse
)

logger = logging.getLogger(__name__)


def _build_timeline(route):
    timeline = []
    entries = route.entries
    for i, e in enumerate(entries):
        travel_next = entries[i + 1].travel_from_prev_min if i + 1 < len(entries) else None
        timeline.append(TimelineEntry(
            attraction_id=e.attraction_id,
            attraction_name=e.attraction_name,
            offset_start_min=e.offset_start_min,
            offset_end_min=e.offset_end_min,
            visit_duration_minutes=e.visit_minutes,
            travel_to_next_minutes=travel_next,
            cost=e.cost,
        ))
    return timeline


def assemble_response(routes, enrichments, request, candidate_count, trip_description=""):
    n = min(len(routes), len(enrichments))
    plans = []
    for i in range(n):
        route, enr = routes[i], enrichments[i]
        explanation = enr.explanation
        if enr.timeline_narrative:
            explanation += "\n\n" + enr.timeline_narrative

        plans.append(RoutePlan(
            route_id=f"route_{i + 1}_{route.theme.value}",
            theme=route.theme.value,
            attractions=route.ordered_ids,
            timeline=_build_timeline(route),
            total_duration_hours=round(route.total_duration_min / 60, 1),
            total_cost=round(route.total_cost, 2),
            explanation=explanation,
            path=[{"lat": p[0], "lng": p[1]} for p in route.path_points],
            micro_stops=enr.micro_stops,
        ))

    resp = TripResponse(
        request_id=str(uuid.uuid4()),
        routes=plans,
        generated_at=datetime.datetime.now().isoformat(),
        candidate_count=candidate_count,
        trip_description=trip_description,
    )
    logger.info(f"Assembled {len(plans)} routes")
    return resp