"""
route_validation.py — Module 3: Route Validation & Scheduling

Constraints: duration limit + budget limit.
"""

from __future__ import annotations

import logging

import networkx as nx

from travel_planner.models import (
    Attraction, RouteSkeleton, ScheduleEntry,
    TripRequest, ValidatedRoute,
)

logger = logging.getLogger(__name__)

START = "__START__"
END = "__END__"


def _edge_weight(G, u, v):
    return G[u][v]["weight"] if G.has_edge(u, v) else 600


def validate_skeleton(sk, G, must_visit, candidates, request):
    lookup = {a.id: a for a in must_visit + candidates}
    must_ids = {a.id for a in must_visit}
    daily_limit = request.daily_minutes
    budget_left = request.budget.max

    elapsed = 0
    prev = START
    entries = []
    scheduled = []

    interior = [n for n in sk.ordered_nodes if n not in (START, END)]

    for nid in interior:
        a = lookup.get(nid)
        if not a:
            continue

        travel_s = _edge_weight(G, prev, nid)
        travel_m = travel_s // 60
        block = travel_m + a.visit_minutes

        # Duration check
        if elapsed + block > daily_limit:
            if nid in must_ids:
                logger.warning(f"Must-visit {nid} can't fit — infeasible")
                return None
            continue

        # Budget check
        if a.price > budget_left:
            if nid in must_ids:
                pass  # must-visit overrides budget
            else:
                continue

        offset_start = elapsed + travel_m
        offset_end = offset_start + a.visit_minutes

        entries.append(ScheduleEntry(
            attraction_id=a.id,
            attraction_name=a.name,
            offset_start_min=offset_start,
            offset_end_min=offset_end,
            visit_minutes=a.visit_minutes,
            travel_from_prev_min=travel_m,
            cost=a.price,
        ))
        scheduled.append(a.id)
        budget_left -= a.price
        elapsed = offset_end
        prev = nid

    if must_ids - set(scheduled):
        logger.warning(f"[{sk.theme.value}] missing must-visit — infeasible")
        return None

    total_dur = entries[-1].offset_end_min if entries else 0
    total_cost = sum(e.cost for e in entries)

    path = []
    if START in G.nodes:
        d = G.nodes[START]
        path.append((d["lat"], d["lng"]))
    for i in scheduled:
        if i in G.nodes:
            d = G.nodes[i]
            path.append((d["lat"], d["lng"]))
    if END in G.nodes:
        d = G.nodes[END]
        path.append((d["lat"], d["lng"]))

    v = ValidatedRoute(
        theme=sk.theme, entries=entries, ordered_ids=scheduled,
        total_duration_min=total_dur, total_cost=total_cost,
        path_points=path,
    )
    logger.info(f"[{sk.theme.value}] {len(scheduled)} stops, {total_dur}min, £{total_cost:.0f}")
    return v


def validate_all(skeletons, G, must_visit, candidates, request):
    results = []
    for sk in skeletons:
        v = validate_skeleton(sk, G, must_visit, candidates, request)
        if v:
            results.append(v)
        else:
            logger.warning(f"[{sk.theme.value}] dropped")
    return results