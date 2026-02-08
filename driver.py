from dataclasses import dataclass, field
from typing import List
from datetime import date, timedelta
import pandas as pd

from travel_planner.models import RoutePlan, TransportType
from trip_request import TripRequest

@dataclass
class Driver:
    name: str
    cities: List[str]
    languages: List[str]
    services: List[TransportType]
    attractions: List[str]  
    hourly_price: int        
    rating: float
    unavailable_dates: List[date] = field(default_factory=list)

@dataclass
class DriverScore:
    driver: Driver
    score: int

def _norm(s: str) -> str:
    return str(s).strip().replace("'", "").replace("[", "").replace("]", "").lower()


def generate_driver(file: str) -> List[Driver]:
    df = pd.read_csv(file)
    df.columns = [c.strip().lower() for c in df.columns]

    rename_map = {
        "name": "name",
        "city": "cities",
        "service": "services",
        "activity / attraction": "attractions",
        "languages": "languages",
        "rating": "rating",
        "unavailable dates": "unavailable_dates",
        "hourly price": "hourly_price",
    }
    df = df.rename(columns=rename_map)


    required = [ "name", "cities", "services", "attractions", "languages", "rating"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"CSV missing required columns: {missing}")

    def _parse_list(cell) -> List[str]:
        if pd.isna(cell):
            return []
        s = _norm(cell)
        if not s:
            return []
        return [x.strip() for x in s.split(",") if x.strip()]
        
    def _parse_dates(cell) -> List[date]:
        out = _parse_list(cell)
        dates: List[date] = []
        for x in out:
            try:
                dates.append(date.fromisoformat(str(x).strip()))
            except Exception:
                continue
        return dates
    
    SERVICE_TRANS = {
        "driver": TransportType.CAR,
        "driver-guide" : TransportType.DRIVERGUIDE,
        "buddy": TransportType.WALK,
        "bikeguide": TransportType.BIKE,
    }

    def _parse_services(cell) -> list[TransportType]:
        raw = _parse_list(cell)
        out: list[TransportType] = []

        for s in raw:
            key = s.lower().strip()
            if key in SERVICE_TRANS:
                out.append(SERVICE_TRANS[key])
            else:
                print(f"⚠️ Unknown service: {s}")  # optional debug

        return out
        
    drivers: List[Driver] = []
    for _, row in df.iterrows():
        drivers.append(
            Driver(
                name=str(row["name"]).strip(),
                cities=_parse_list(row["cities"]),
                languages=_parse_list(row["languages"]),
                services=_parse_services(row["services"]),
                attractions=_parse_list(row["attractions"]),
                hourly_price=int(row["hourly_price"]),
                rating=float(row["rating"]) if not pd.isna(row["rating"]) else 0.0,
                unavailable_dates=_parse_dates(row["unavailable_dates"]) if "unavailable_dates" in df.columns else [],
            )
        )
    return drivers


def generate_driver_scores(drivers: list[Driver], plan: RoutePlan, request: TripRequest):
    req_city = _norm(request.city)
    req_service = request.service

    req_langs = set(_norm(x) for x in (getattr(request, "languages", []) or []))
    req_date = getattr(request, "chosen_date", None)  # adjust if your field differs

    must_set = set(getattr(request, "must_visit_ids", []) or [])
    plan_set = set(getattr(plan, "attractions", []) or [])
    optional_set = plan_set - must_set

    scored: List[DriverScore] = []

    for d in drivers:
        driver_cities = { _norm(c) for c in d.cities }
        driver_langs = { _norm(l) for l in d.languages }
        driver_services = d.services

        if req_city not in driver_cities:
            continue

        if req_service not in driver_services:
            continue

        # if user selected languages, require at least one overlap
        if req_langs and not (req_langs & driver_langs):
            continue

        if req_date is not None and req_date in d.unavailable_dates:
            continue

        # --- scoring ---
        score = 0
        score += 30 * len(must_set.intersection(d.attractions))     
        score += 15 * len(optional_set.intersection(d.attractions))   
        score += int(d.rating * 5)                                   

        scored.append(DriverScore(d, score))

    scored.sort(key=lambda m: m.score, reverse=True)
    return scored
    
    
    
