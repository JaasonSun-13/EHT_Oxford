from dataclasses import dataclass, field
from enum import Enum
from datetime import date
from typing import Optional

@dataclass
class GeoPoint:
    lat: float
    lng: float

@dataclass
class Budget:
    min: int = 0
    max: int = 500

class TransportType(Enum):
    WALK = "walk"
    BIKE = "bike"
    CAR = "car"
    DRIVERGUIDE = "driver_guide"

@dataclass
class TripRequest:
    start_point: Optional[GeoPoint] = None
    end_point: Optional[GeoPoint] = None
    must_visit_ids: list[str] = field(default_factory=list)
    daily_duration_hours: float = 8.0
    budget: Budget = field(default_factory=Budget)
    service: TransportType = TransportType.WALK
    chosen_date: date = field(default_factory=date.today)    
    city: str = "oxford"     
    languages: list[str] = field(default_factory=lambda: ["en"])
    description: str = ""  

    @property
    def daily_minutes(self) -> int:
        return int(self.daily_duration_hours * 60)


def create_trip_request(
    *,
    must_visit_ids: list[str],
    duration: float,
    max_budget: int,
    service: str,
    chosen_date: date,
    city: str,
    languages: list[str],
    description: str = "",
) -> TripRequest:
    
    service_map = {
        "Your GOOD Buddy": TransportType.WALK,
        "Bike Guide": TransportType.BIKE,
        "Driver only": TransportType.CAR,
        "Driver Guide": TransportType.DRIVERGUIDE,
    }

    return TripRequest(
        start_point=None,
        end_point=None,
        must_visit_ids=must_visit_ids,
        daily_duration_hours=duration,
        budget=Budget(min=0, max=max_budget),
        service=service_map[service],
        chosen_date=chosen_date,
        city=city.lower(),
        languages=languages,
        description=description,
    )       
