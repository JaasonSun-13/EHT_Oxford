"""
models.py — Shared types.

CSV columns:  attraction, lat, lng, popularity, price_range
Request has:  start/end points, must_visit, duration, budget, service,
              languages, description (free-text for LLM)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

DEFAULT_VISIT_MINUTES = 45


class TransportType(str, Enum):
    WALK = "walk"
    BIKE = "bike"
    CAR = "car"


class RouteTheme(str, Enum):
    FASTEST = "fastest"
    POPULAR = "popular"
    BALANCED = "balanced"
    RELAXED = "relaxed"
    HIDDEN_GEMS = "hidden_gems"


THEMES = list(RouteTheme)


@dataclass
class GeoPoint:
    lat: float
    lng: float


@dataclass
class Budget:
    min: float = 0
    max: float = 500


@dataclass
class TripRequest:
    start_point: GeoPoint
    end_point: GeoPoint
    must_visit_ids: list[str] = field(default_factory=list)
    daily_duration_hours: float = 8.0
    budget: Budget = field(default_factory=Budget)
    service: TransportType = TransportType.WALK
    date: Optional[str] = None          # ISO date string, e.g. "2024-10-01"
    city: Optional[str] = None          # for future use, e.g. to adjust LLM prompts
    languages: list[str] = field(default_factory=lambda: ["en"])
    description: str = ""           # free-text trip preference → forwarded to LLM

    @property
    def daily_minutes(self) -> int:
        return int(self.daily_duration_hours * 60)


# Attraction  (from CSV: attraction, lat, lng, popularity, price_range)

@dataclass
class Attraction:
    id: str
    name: str
    latitude: float
    longitude: float
    popularity: float = 0.0         # 0-100
    price: float = 0.0              # per-visit cost from price_range column
    visit_minutes: int = DEFAULT_VISIT_MINUTES


# Internal pipeline types

@dataclass
class RouteSkeleton:
    theme: RouteTheme
    ordered_nodes: list[str]
    total_travel_seconds: int = 0

    @property
    def attraction_ids(self) -> list[str]:
        return [n for n in self.ordered_nodes if n not in ("__START__", "__END__")]


@dataclass
class ScheduleEntry:
    attraction_id: str
    attraction_name: str
    offset_start_min: int
    offset_end_min: int
    visit_minutes: int
    travel_from_prev_min: int
    cost: float


@dataclass
class ValidatedRoute:
    theme: RouteTheme
    entries: list[ScheduleEntry]
    ordered_ids: list[str]
    total_duration_min: int
    total_cost: float
    path_points: list[tuple[float, float]]


@dataclass
class EnrichmentResult:
    explanation: str
    micro_stops: list[str]
    timeline_narrative: str


# Response types

@dataclass
class TimelineEntry:
    attraction_id: str
    attraction_name: str
    offset_start_min: int
    offset_end_min: int
    visit_duration_minutes: int
    travel_to_next_minutes: Optional[int]
    cost: float


@dataclass
class RoutePlan:
    route_id: str
    theme: str
    attractions: list[str]
    timeline: list[TimelineEntry]
    total_duration_hours: float
    total_cost: float
    explanation: str
    path: list[dict]
    micro_stops: list[str]


@dataclass
class TripResponse:
    request_id: str
    routes: list[RoutePlan]
    generated_at: str
    candidate_count: int
    trip_description: str | None = None



def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371.0
    dlat, dlng = math.radians(lat2 - lat1), math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(dlng / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))