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


async def actual_response(request: TripRequest):
    # 1. Load your CSV
    attractions = load_attractions_from_csv(request.city)
    print(f"Loaded {len(attractions)} attractions")

    # 3. Choose LLM client
    #    Set OPENAI_API_KEY env var to use real OpenAI, otherwise falls back to mock
    
    api_key = "sk-your-key-here"
    if api_key:
        llm = OpenAIClient(api_key=api_key)  # default: gpt-4o-mini
        print("Using OpenAI")
    else:
        llm = MockLLMClient()
        print("No OPENAI_API_KEY set — using mock LLM")

    # 4. Generate routes
    response = await generate_trip_plans(attractions, request, llm)

    return response
