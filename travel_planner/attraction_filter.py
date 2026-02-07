"""
attraction_filter.py — Module 1: Attraction Filtering

CSV columns: attraction, lat, lng, popularity, price_range
Filters by: radius from corridor, per-attraction price vs budget
Scores by:  proximity (0.50) + popularity (0.50)
"""

from __future__ import annotations

import csv
import logging
from pathlib import Path
import re

from models import Attraction, GeoPoint, TripRequest, haversine_km

logger = logging.getLogger(__name__)

MAX_SEARCH_RADIUS_KM = 50.0
MAX_CANDIDATES = 100


# =============================================================================
# CSV loader
# =============================================================================

def load_attractions_from_csv(city: str) -> list[Attraction]:
    """
    Load from CSV.  Expected columns: attraction, lat, lng, popularity, price_range
    ID is auto-generated as a slug from the name.
    """
    path = Path("data/attractions") / city.strip().lower().replace(" ", "_") + ".csv"

    attractions: list[Attraction] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("attraction", "").strip()
            if not name:
                continue
            try:
                lat = float(row["lat"])
                lng = float(row["lng"])
                pop = float(row.get("popularity", 0))
                price = _parse_price(row.get("price_range", "0"))
            except (ValueError, KeyError):
                logger.warning(f"Skipping bad row: {row}")
                continue

            attractions.append(Attraction(
                id=_slugify(name),
                name=name,
                latitude=lat,
                longitude=lng,
                popularity=pop,
                price=price,
            ))

    logger.info(f"Loaded {len(attractions)} attractions from {path}")
    return attractions


def _slugify(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")


def _parse_price(raw: str) -> float:
    """
    Parse price_range into a single float.
    Handles: "0", "5", "10.50", "5-15" (takes midpoint), "free" → 0
    """
    raw = raw.strip().lower()
    if not raw or raw == "free":
        return 0.0
    # Range like "5-15" or "5.00-15.00"
    if "-" in raw:
        parts = raw.split("-")
        try:
            lo, hi = float(parts[0]), float(parts[1])
            return (lo + hi) / 2
        except (ValueError, IndexError):
            pass
    # Single number
    try:
        return float(re.sub(r"[^0-9.]", "", raw))
    except ValueError:
        return 0.0


# =============================================================================
# Spatial filter
# =============================================================================

def filter_by_radius(attractions, midpoint, radius_km):
    return [
        a for a in attractions
        if haversine_km(midpoint.lat, midpoint.lng, a.latitude, a.longitude) <= radius_km
    ]


# =============================================================================
# Budget filter
# =============================================================================

def filter_by_budget(candidates, budget_max, must_ids):
    """Drop attractions whose price exceeds 50% of total budget (unless must-visit)."""
    return [
        a for a in candidates
        if a.id in must_ids or a.price <= budget_max * 0.5
    ]


# =============================================================================
# Scoring
# =============================================================================

def score_candidates(candidates, midpoint, radius_km):
    scored = []
    for a in candidates:
        dist = haversine_km(midpoint.lat, midpoint.lng, a.latitude, a.longitude)
        proximity = max(0, 1.0 - dist / radius_km)
        pop = a.popularity / 100.0
        score = 0.50 * proximity + 0.50 * pop
        scored.append((score, a))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [a for _, a in scored]


# =============================================================================
# Main entry
# =============================================================================

def get_candidate_pool(attractions, request):
    corridor = haversine_km(
        request.start_point.lat, request.start_point.lng,
        request.end_point.lat, request.end_point.lng,
    )
    radius = min(max(corridor / 2 + 10, 5.0), MAX_SEARCH_RADIUS_KM)
    midpoint = GeoPoint(
        lat=(request.start_point.lat + request.end_point.lat) / 2,
        lng=(request.start_point.lng + request.end_point.lng) / 2,
    )

    nearby = filter_by_radius(attractions, midpoint, radius)
    logger.info(f"Radius: {len(attractions)} → {len(nearby)} (r={radius:.1f}km)")

    must_ids = set(request.must_visit_ids)
    must_visit = [a for a in nearby if a.id in must_ids]
    if len(must_visit) < len(must_ids):
        for a in attractions:
            if a.id in must_ids and a.id not in {m.id for m in must_visit}:
                must_visit.append(a)

    missing = must_ids - {a.id for a in must_visit}
    if missing:
        logger.warning(f"Must-visit not found: {missing}")

    candidates = [a for a in nearby if a.id not in must_ids]
    candidates = filter_by_budget(candidates, request.budget.max, must_ids)
    candidates = score_candidates(candidates, midpoint, radius)
    candidates = candidates[:MAX_CANDIDATES]

    logger.info(f"Pool: {len(must_visit)} must-visit + {len(candidates)} candidates")
    return must_visit, candidates