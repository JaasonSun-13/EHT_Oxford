"""
test_standalone.py — End-to-end test with Oxford data (mock CSV).

CSV: attraction, lat, lng, popularity, price_range
Request includes: budget, service, languages, description

Run:  python test_standalone.py
"""

from __future__ import annotations

import asyncio
import csv
import json
import logging
import os
import sys

sys.path.insert(0, ".")

from datetime import date

from models import Attraction, Budget, GeoPoint, TransportType, TripRequest
from attraction_filter import load_attractions_from_csv, get_candidate_pool
from route_skeleton import generate_skeletons
from route_validation import validate_all
from llm_enrichment import MockLLMClient, enrich_routes, generate_trip_description
from assembly import assemble_response

logging.basicConfig(level=logging.INFO, format="%(levelname)-5s %(message)s")

MOCK_CSV = "test_oxford.csv"

OXFORD_DATA = [
    # (name, lat, lng, popularity, price_range)
    ("Bodleian Library",         51.7540, -1.2544, 92, "0"),
    ("Radcliffe Camera",         51.7536, -1.2540, 88, "0"),
    ("Christ Church College",    51.7500, -1.2568, 85, "8"),
    ("Ashmolean Museum",         51.7555, -1.2610, 80, "0"),
    ("University Church",        51.7527, -1.2536, 60, "0"),
    ("Carfax Tower",             51.7517, -1.2578, 55, "3"),
    ("Covered Market",           51.7521, -1.2560, 65, "0"),
    ("Pitt Rivers Museum",       51.7586, -1.2553, 72, "0"),
    ("Oxford Castle",            51.7510, -1.2625, 70, "12"),
    ("Botanic Garden",           51.7507, -1.2482, 58, "6"),
    ("Bridge of Sighs",          51.7540, -1.2530, 75, "0"),
    ("Sheldonian Theatre",       51.7545, -1.2548, 62, "5"),
    ("Museum of Natural History", 51.7585, -1.2555, 68, "0"),
    ("Port Meadow",              51.7680, -1.2770, 35, "0"),
    ("Iffley Lock",              51.7360, -1.2340, 20, "0"),
    ("Headington Shark",         51.7580, -1.2110, 25, "0"),
    ("St Mary the Virgin",       51.7528, -1.2538, 45, "5"),
    ("Magdalen College",         51.7518, -1.2462, 50, "7"),
    ("New College",              51.7535, -1.2510, 48, "5"),
    ("Tom Tower",                51.7502, -1.2570, 42, "0"),
]


def create_mock_csv():
    with open(MOCK_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["attraction", "lat", "lng", "popularity", "price_range"])
        for name, lat, lng, pop, price in OXFORD_DATA:
            w.writerow([name, lat, lng, pop, price])


async def main():
    create_mock_csv()
    attractions = load_attractions_from_csv(MOCK_CSV)

    request = TripRequest(
        start_point=GeoPoint(51.7520, -1.2577),
        end_point=GeoPoint(51.7500, -1.2568),
        must_visit_ids=["bodleian_library"],
        daily_duration_hours=6,
        budget=Budget(min=0, max=50),
        service=TransportType.WALK,         # "Your GOOD Buddy"
        chosen_date=date(2024, 10, 1),
        city="oxford",
        languages=["en"],
        description="I love history and architecture, prefer quiet spots over crowded ones",
    )

    print("=" * 65)
    print("OXFORD ROUTE PLANNER — FULL PIPELINE TEST")
    print(f"  {request.daily_duration_hours}h | budget £{request.budget.max} | {request.service.value}")
    print(f"  {len(attractions)} attractions loaded")
    print(f"  description: \"{request.description}\"")
    print("=" * 65)

    # Module 1
    print("\n▸ MODULE 1: Attraction Filtering")
    must, cands = get_candidate_pool(attractions, request)

    # Module 2
    print("\n▸ MODULE 2: Route Skeleton Generation")
    G, skeletons = generate_skeletons(
        request.start_point, request.end_point, must, cands, request,
    )

    # Module 3
    print("\n▸ MODULE 3: Route Validation")
    validated = validate_all(skeletons, G, must, cands, request)

    # Module 4
    print("\n▸ MODULE 4: LLM Enrichment (mock)")
    llm = MockLLMClient()
    enrichments = await enrich_routes(validated, request, must + cands, llm)

    # Module 4b: Trip description
    print("\n▸ MODULE 4b: Trip Description (mock)")
    trip_description = await generate_trip_description(validated, request, must + cands, llm)

    # Module 5
    print("\n▸ MODULE 5: Assembly")
    response = assemble_response(validated, enrichments, request, len(must + cands), trip_description)

    # Output
    print("\n" + "=" * 65)
    out = {
        "request_id": response.request_id,
        "candidate_count": response.candidate_count,
        "trip_description": response.trip_description,
        "routes": [],
    }
    for r in response.routes:
        out["routes"].append({
            "route_id": r.route_id,
            "theme": r.theme,
            "attractions": r.attractions,
            "timeline": [
                {"name": t.attraction_name, "start_min": t.offset_start_min,
                 "end_min": t.offset_end_min, "cost": t.cost,
                 "travel_next_min": t.travel_to_next_minutes}
                for t in r.timeline
            ],
            "duration_hours": r.total_duration_hours,
            "total_cost": r.total_cost,
        })
    print(json.dumps(out, indent=2))

    # Assertions
    print("\n" + "=" * 65)
    routes = response.routes
    assert len(routes) > 0
    assert len(routes) <= 5
    print(f"✓ {len(routes)} routes generated")

    for r in routes:
        assert "bodleian_library" in r.attractions
        assert r.total_duration_hours <= request.daily_duration_hours + 0.5
        assert r.total_cost <= request.budget.max + 1
        assert len(r.timeline) > 0
    print("✓ Must-visit present, duration OK, budget OK")

    themes = [r.theme for r in routes]
    print(f"✓ Themes: {themes}")

    unique = len(set(frozenset(r.attractions) for r in routes))
    print(f"✓ Diversity: {unique}/{len(routes)} unique")

    print("\nALL ASSERTIONS PASSED ✓")
    os.remove(MOCK_CSV)


if __name__ == "__main__":
    asyncio.run(main())