from dataclasses import dataclass, field
from typing import List
from datetime import date, timedelta
import pandas as pd

@dataclass
class Driver:
    id: int
    name: str
    cities: List[str]
    languages: List[str]
    services: List[str]
    attractions: List[str]  
    price_per_day: int        
    rating: float
    unavaialble_date: List[date] = field(default_factory=list)

@dataclass
class DriverScore:
    driver: Driver
    score: int


def generate_driver(file: str) -> List[Driver]:
    df = pd.read_csv(file)
    df.columns = [c.strip().lower() for c in df.columns]

    required = ["id", "name", "cities", "languages", "services", "attractions", "price_per_day", "rating"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"CSV missing required columns: {missing}")

    def parse_list(cell) -> List[str]:
        if pd.isna(cell):
            return []
        s = str(cell).strip()
        if not s:
            return []
        return [x.strip() for x in s.split(",") if x.strip()]
    
    def parse_dates(cell) -> List[date]:
        if pd.isna(cell):
            return []
        s = str(cell).strip()
        if not s:
            return []
        out: List[date] = []
        for part in s.split(","):
            part = part.strip()
            if not part:
                continue
            # expects YYYY-MM-DD
            out.append(date.fromisoformat(part))
        return out
    
    drivers: List[Driver] = []
    for _, row in df.iterrows():
        drivers.append(
            Driver(
                id=int(row["id"]),
                name=str(row["name"]).strip(),
                cities=parse_list(row["cities"]),
                languages=parse_list(row["languages"]),
                services=parse_list(row["services"]),
                attractions=parse_list(row["attractions"]),
                price_per_day=int(row["price_per_day"]),
                rating=float(row["rating"]),
                unavailable_date=parse_dates(row["unavailable_date"]) if "unavailable_date" in df.columns else []
            )
        )

    return drivers


def trip_dates(start: date, end: date) -> List[date]:
  n = (end - start).days
  return [start + timedelta(days=i) for i in range(n + 1)]

def extract_plan_attractions(plan: Plan) -> List[str]:
  # assumes plan.days -> day.items -> item.name
  out = []
  for day in plan.days:
      for item in day.items:
          out.append(item.name)
  return out

def generate_driver_scores(drivers: Driver, plan: Plan, request: TripRequest):
    must_set = set(request.must_visits)
    plan_set = set(extract_plan_attractions(plan))
    optional_set = plan_set - must_set
    tdays = trip_dates(request.start_date, request.end_date)

    scored: List[DriverScore] = []

    for d in drivers:
        # --- mandatory filters ---
        if request.city not in d.cities:
            continue
        if request.language not in d.languages:
            continue
        if request.service not in d.services:
            continue
        if any(day in d.unavailable_dates for day in tdays):
            continue

        # --- scoring ---
        score = 0
        score += 30 * len(must_set.intersection(d.attractions))     
        score += 15 * len(optional_set.intersection(d.attractions))   
        score += int(d.rating * 5)                                   

        scored.append(DriverScore(d, score))

    scored.sort(key=lambda m: m.score, reverse=True)
    return scored
    
    
    
