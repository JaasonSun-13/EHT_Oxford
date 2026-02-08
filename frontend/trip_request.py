from datetime import date
from travel_planner.models import GeoPoint, TransportType, TripRequest


def create_trip_request(
    *,
    must_visit_ids: list[str],
    duration: float,
    budget: int,
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
    if languages == []:
        languages = ["English"]
        
    return TripRequest(
        start_point=GeoPoint(lat=51.7520, lng=-1.2577),
        end_point=GeoPoint(lat=51.7500, lng=-1.2568),
        must_visit_ids=must_visit_ids,
        daily_duration_hours=duration,
        budget=budget,
        service=service_map[service],
        chosen_date=chosen_date,
        city=city.lower(),
        languages=languages,
        description=description,
    )       
