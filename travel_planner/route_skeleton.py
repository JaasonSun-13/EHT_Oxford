"""
route_skeleton.py — Module 2: Route Skeleton Generation
"""

from __future__ import annotations

import logging
import random

import networkx as nx

from models import (
    Attraction, GeoPoint, RouteSkeleton, RouteTheme,
    THEMES, TripRequest, haversine_km,
)

logger = logging.getLogger(__name__)

START = "__START__"
END = "__END__"
SPEEDS = {"walk": 5.0, "bike": 15.0, "car": 40.0}
DETOUR = {"walk": 1.3, "bike": 1.25, "car": 1.4}


def build_graph(start, end, attractions, transport):
    G = nx.DiGraph()
    G.add_node(START, lat=start.lat, lng=start.lng, virtual=True)
    G.add_node(END, lat=end.lat, lng=end.lng, virtual=True)
    for a in attractions:
        G.add_node(a.id, lat=a.latitude, lng=a.longitude, virtual=False)

    speed = SPEEDS.get(transport, 5.0)
    detour = DETOUR.get(transport, 1.3)
    nodes = list(G.nodes(data=True))
    for u, ud in nodes:
        for v, vd in nodes:
            if u == v:
                continue
            d = haversine_km(ud["lat"], ud["lng"], vd["lat"], vd["lng"]) * detour
            G.add_edge(u, v, weight=int((d / speed) * 3600), distance_km=round(d, 2))
    logger.info(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G


def theme_score(a, theme, penalty=0.0):
    p = a.popularity / 100.0
    if theme == RouteTheme.FASTEST:
        base = 0.5 + 0.5 * p
    elif theme == RouteTheme.POPULAR:
        base = p
    elif theme == RouteTheme.BALANCED:
        base = 0.6 * p + 0.4 * random.uniform(0.3, 1.0)
    elif theme == RouteTheme.RELAXED:
        base = 0.8 * p + 0.2 * random.uniform(0, 1)
    elif theme == RouteTheme.HIDDEN_GEMS:
        base = 0.7 * max(0, 1.0 - p) + 0.3 * random.uniform(0, 1)
    else:
        base = p
    return max(0.0, base - penalty)


MAX_STOPS = {
    RouteTheme.FASTEST: 6,
    RouteTheme.POPULAR: 5,
    RouteTheme.BALANCED: 5,
    RouteTheme.RELAXED: 3,
    RouteTheme.HIDDEN_GEMS: 5,
}


def select_for_theme(candidates, theme, used, reuse_penalty=0.25):
    scored = [
        (theme_score(a, theme, reuse_penalty if a.id in used else 0.0), a)
        for a in candidates
    ]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [a for _, a in scored[:MAX_STOPS[theme]]]


def greedy_nn(G, node_ids):
    if not node_ids:
        return [START, END]
    unvisited, route, cur = set(node_ids), [START], START
    while unvisited:
        best, bw = None, float("inf")
        for n in unvisited:
            if G.has_edge(cur, n) and G[cur][n]["weight"] < bw:
                best, bw = n, G[cur][n]["weight"]
        if best is None:
            break
        route.append(best)
        unvisited.discard(best)
        cur = best
    route.append(END)
    return route


def two_opt(G, route, max_iters=100):
    def cost(r):
        return sum(
            G[r[i]][r[i+1]]["weight"] if G.has_edge(r[i], r[i+1]) else 1_000_000
            for i in range(len(r) - 1)
        )
    best, bc = route[:], cost(route)
    for _ in range(max_iters):
        improved = False
        for i in range(1, len(best) - 2):
            for j in range(i + 1, len(best) - 1):
                cand = best[:i] + best[i:j+1][::-1] + best[j+1:]
                c = cost(cand)
                if c < bc - 1:
                    best, bc, improved = cand, c, True
        if not improved:
            break
    return best


def _build_one(G, must_visit, selected, theme):
    all_ids = list({a.id for a in must_visit}) + [
        a.id for a in selected if a.id not in {m.id for m in must_visit}
    ]
    ordered = greedy_nn(G, all_ids)
    ordered = two_opt(G, ordered)
    travel = sum(
        G[ordered[i]][ordered[i+1]]["weight"]
        for i in range(len(ordered) - 1)
        if G.has_edge(ordered[i], ordered[i+1])
    )
    return RouteSkeleton(theme=theme, ordered_nodes=ordered, total_travel_seconds=travel)


def generate_skeletons(start, end, must_visit, candidates, request):
    G = build_graph(start, end, must_visit + candidates, request.service.value)
    skeletons, used = [], set()
    for theme in THEMES:
        selected = select_for_theme(candidates, theme, used)
        sk = _build_one(G, must_visit, selected, theme)
        skeletons.append(sk)
        used.update(sk.attraction_ids)
        logger.info(f"[{theme.value}] {sk.attraction_ids}")
    return G, skeletons