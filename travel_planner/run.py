"""
run.py — Run the pipeline with your real oxford.csv

Usage:
    python run.py

Expects oxford.csv in the same directory with columns:
    attraction, lat, lng, popularity, price_range
"""

import asyncio
import json
import os
import sys

sys.path.insert(0, ".")

from datetime import date

from models import Budget, GeoPoint, TransportType, TripRequest
from attraction_filter import load_attractions_from_csv
from pipeline import generate_trip_plans
from llm_enrichment import OpenAIClient, MockLLMClient


async def main():
    # 1. Load your CSV
    attractions = load_attractions_from_csv("oxford.csv")
    print(f"Loaded {len(attractions)} attractions")

    # 2. Define your trip
    request = TripRequest(
        start_point=GeoPoint(51.7520, -1.2577),   # Oxford city centre
        end_point=GeoPoint(51.7500, -1.2568),      # Christ Church area
        must_visit_ids=["bodleian_library"],        # use slugified names
        daily_duration_hours=6,
        budget=Budget(min=0, max=50),
        service=TransportType.WALK,         # "Your GOOD Buddy"
        chosen_date= date(2024, 10, 1),
        city="oxford",
        languages=["en"],
        description="I love history and architecture, prefer quiet spots",
    )

    # 3. Choose LLM client
    #    Set OPENAI_API_KEY env var to use real OpenAI, otherwise falls back to mock
    
<<<<<<< Updated upstream
    api_key = "sk-your-key-here"
=======

    api_key = os.environ.get("OPENAI_API_KEY")
>>>>>>> Stashed changes
    if api_key:
        llm = OpenAIClient(api_key=api_key)  # default: gpt-4o-mini
        print("Using OpenAI")
    else:
        llm = MockLLMClient()
        print("No OPENAI_API_KEY set — using mock LLM")

    # 4. Generate routes
    response = await generate_trip_plans(attractions, request, llm)

    # 4. Print result
    print(json.dumps({
        "request_id": response.request_id,
        "candidate_count": response.candidate_count,
        "trip_description": response.trip_description,
        "routes": [
            {
                "route_id": r.route_id,
                "theme": r.theme,
                "attractions": r.attractions,
                "duration_hours": r.total_duration_hours,
                "total_cost": r.total_cost,
                "stops": len(r.timeline),
                "explanation": r.explanation,
                "micro_stops": r.micro_stops,
                "timeline": [
                    {
                        "name": t.attraction_name,
                        "start_min": t.offset_start_min,
                        "end_min": t.offset_end_min,
                        "cost": t.cost,
                        "travel_next_min": t.travel_to_next_minutes,
                    }
                    for t in r.timeline
                ],
            }
            for r in response.routes
        ]
    }, indent=2))


if __name__ == "__main__":
    asyncio.run(main())