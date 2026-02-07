"""
llm_enrichment.py — Module 4: LLM Enrichment

Passes request.description (user's free-text trip preference) to the LLM
so it can tailor explanations and micro-stop suggestions accordingly.
"""

from __future__ import annotations

import json
import logging

from travel_planner.models import (
    Attraction, EnrichmentResult, RouteTheme,
    TripRequest, ValidatedRoute,
)

logger = logging.getLogger(__name__)


def build_prompt(route, request, lookup, unused):
    attrs = [
        {"id": lookup[i].id, "name": lookup[i].name,
         "popularity": lookup[i].popularity, "price": lookup[i].price}
        for i in route.ordered_ids if i in lookup
    ]
    schedule = [
        {"name": e.attraction_name, "start_min": e.offset_start_min,
         "end_min": e.offset_end_min, "visit_min": e.visit_minutes,
         "travel_min": e.travel_from_prev_min, "cost": e.cost}
        for e in route.entries
    ]
    micro = [
        {"id": a.id, "name": a.name, "popularity": a.popularity, "price": a.price}
        for a in unused[:15]
    ]

    # Include user description if provided
    desc_block = ""
    if request.description:
        desc_block = f"""
=== USER PREFERENCE ===
{request.description}

Use this preference to tailor your explanation and micro-stop suggestions.
"""

    return f"""You are a travel planning assistant. Enrich this pre-computed single-day route.

=== RULES ===
1. ONLY suggest micro-stops from "micro_stop_candidates" below.
2. Do NOT invent any attraction not in the provided data.
3. Return ONLY a valid JSON object — no markdown, no preamble.

=== ROUTE ===
Theme: {route.theme.value}
Duration: {route.total_duration_min} minutes
Total cost: £{route.total_cost:.0f}
Transport: {request.service.value}
Budget: £{request.budget.min:.0f}–£{request.budget.max:.0f}
City: {request.city or "unknown"}
Date: {request.chosen_date or "not specified"}
{desc_block}
=== ATTRACTIONS (visit order) ===
{json.dumps(attrs, indent=2)}

=== SCHEDULE ===
{json.dumps(schedule, indent=2)}

=== MICRO-STOP CANDIDATES (suggest up to 3) ===
{json.dumps(micro, indent=2)}

=== REQUIRED OUTPUT ===
{{
    "explanation": "2-3 sentences on why this route is great. Mention specific attraction names. If user preference is given, explain how the route matches it.",
    "micro_stops": ["id_from_list"],
    "timeline_narrative": "3-5 sentence friendly narrative of the day."
}}"""


# LLM clients

class LLMClient:
    async def complete(self, prompt, system=""):
        raise NotImplementedError


class OpenAIClient(LLMClient):
    def __init__(self, api_key, model="gpt-4o-mini"):
        from openai import AsyncOpenAI
        api_key = "sk-your-key-here"
        self.model = model

    async def complete(self, prompt, system=""):
        resp = await self.client.chat.completions.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {"role": "system", "content": system or "You are a travel planning assistant. Return only valid JSON."},
                {"role": "user", "content": prompt},
            ],
        )
        return resp.choices[0].message.content


class MockLLMClient(LLMClient):
    EXPLANATIONS = {
        RouteTheme.FASTEST: "This route packs the most stops into minimum travel time.",
        RouteTheme.POPULAR: "Hit all the crowd favorites — the most visited attractions.",
        RouteTheme.BALANCED: "A well-rounded mix of popular highlights and lesser-known spots.",
        RouteTheme.RELAXED: "Just a few stops with generous time at each — no rushing.",
        RouteTheme.HIDDEN_GEMS: "Skip the crowds — these low-profile spots are worth discovering.",
    }

    async def complete(self, prompt, system=""):
        # Trip description prompt
        if "trip description" in prompt.lower() or "trip_description" in prompt.lower():
            return json.dumps({
                "trip_description": "A wonderful day exploring the area's highlights. Multiple route options let you choose between efficiency, hidden gems, and a relaxed pace — all within your budget and time."
            })
        # Per-route enrichment prompt
        theme = RouteTheme.FASTEST
        for t in RouteTheme:
            if t.value in prompt:
                theme = t
                break
        return json.dumps({
            "explanation": self.EXPLANATIONS.get(theme, "A great route."),
            "micro_stops": [],
            "timeline_narrative": "Start at the first attraction, then follow the route through each curated stop.",
        })


# Response parsing

def parse_response(raw, valid_ids):
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        cleaned = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:]).strip()
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        return EnrichmentResult("A curated route for your day.", [], "")

    stops = data.get("micro_stops", [])
    if not isinstance(stops, list):
        stops = []
    validated = [s for s in stops if isinstance(s, str) and s in valid_ids]

    return EnrichmentResult(
        explanation=str(data.get("explanation", "A curated route.")),
        micro_stops=validated[:3],
        timeline_narrative=str(data.get("timeline_narrative", "")),
    )


def fallback_enrichment(route):
    desc = {
        RouteTheme.FASTEST: "Optimized for efficiency — max stops, min travel.",
        RouteTheme.POPULAR: "The most popular attractions in the area.",
        RouteTheme.BALANCED: "A balanced mix of well-known and off-the-radar stops.",
        RouteTheme.RELAXED: "A leisurely pace with fewer stops.",
        RouteTheme.HIDDEN_GEMS: "Hidden gems — great spots without the crowds.",
    }
    return EnrichmentResult(
        explanation=desc.get(route.theme, "A curated route."),
        micro_stops=[],
        timeline_narrative=f"A {route.total_duration_min // 60}-hour day with {len(route.ordered_ids)} stops.",
    )


async def enrich_routes(routes, request, all_attractions, llm):
    lookup = {a.id: a for a in all_attractions}
    valid_ids = set(lookup.keys())
    results = []
    for route in routes:
        unused = [a for a in all_attractions if a.id not in set(route.ordered_ids)]
        prompt = build_prompt(route, request, lookup, unused)
        try:
            raw = await llm.complete(prompt)
            enrichment = parse_response(raw, valid_ids)
        except Exception as e:
            logger.error(f"LLM failed for {route.theme.value}: {e}")
            enrichment = fallback_enrichment(route)
        results.append(enrichment)
    return results


# =============================================================================
# Trip-level description (covers all routes at once)
# =============================================================================

def _build_trip_description_prompt(routes, request, lookup):
    """Prompt for a single trip-level summary across all generated routes."""
    route_summaries = []
    for r in routes:
        names = [lookup[i].name for i in r.ordered_ids if i in lookup]
        route_summaries.append({
            "theme": r.theme.value,
            "stops": len(r.ordered_ids),
            "duration_min": r.total_duration_min,
            "cost": r.total_cost,
            "attractions": names,
        })

    desc_block = ""
    if request.description:
        desc_block = f'\nUser preference: "{request.description}"\n'

    return f"""You are a travel planning assistant. Write a short, engaging trip description (3-5 sentences) that summarises what this day trip offers.

=== TRIP INFO ===
City: {request.city or "unknown"}
Date: {request.chosen_date or "not specified"}
Location: near ({request.start_point.lat}, {request.start_point.lng})
Duration: {request.daily_duration_hours} hours
Budget: £{request.budget.max}
Transport: {request.service.value}
{desc_block}
=== ROUTES GENERATED ({len(route_summaries)}) ===
{json.dumps(route_summaries, indent=2)}

=== RULES ===
1. Return ONLY a JSON object: {{"trip_description": "your 3-5 sentence summary"}}
2. Mention the area, highlight standout attractions across routes, and reference the user's preference if given.
3. No markdown, no preamble."""


def _parse_trip_description(raw):
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        cleaned = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:]).strip()
    try:
        data = json.loads(cleaned)
        return str(data.get("trip_description", ""))
    except json.JSONDecodeError:
        return ""


def _fallback_trip_description(routes, request):
    themes = ", ".join(r.theme.value for r in routes)
    total_attractions = len(set(a for r in routes for a in r.ordered_ids))
    desc = (
        f"A {request.daily_duration_hours}-hour day trip with {len(routes)} route options "
        f"({themes}) covering {total_attractions} unique attractions."
    )
    if request.description:
        desc += f' Tailored for: "{request.description}".'
    return desc


async def generate_trip_description(routes, request, all_attractions, llm):
    """Generate a single trip-level description summarising all routes."""
    lookup = {a.id: a for a in all_attractions}
    prompt = _build_trip_description_prompt(routes, request, lookup)
    try:
        raw = await llm.complete(prompt)
        desc = _parse_trip_description(raw)
        if desc:
            return desc
    except Exception as e:
        logger.error(f"Trip description LLM failed: {e}")
    return _fallback_trip_description(routes, request)