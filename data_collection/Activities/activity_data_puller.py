import time
import requests
import pandas as pd
from tqdm import tqdm
import time
import random

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"

OXFORD_BBOX = [(51.705, -1.305, 51.780, -1.180), 'oxford']
BRISTOL_BBOX = [(51.397, -2.699, 51.507, -2.510), 'bristol']
ALL_BOX = [OXFORD_BBOX, BRISTOL_BBOX]

# A rough Greater London bounding box (south,west,north,east)
# Overpass query: pull lots of tourist-relevant POIs
# We request nodes only for simplicity (fast + enough volume).
# OVERPASS_QUERY = f"""
# [out:json][timeout:180];
# (
#   node["tourism"~"attraction|museum|gallery|zoo|theme_park|viewpoint|information"]({TARGET_BBOX[0]},{TARGET_BBOX[1]},{TARGET_BBOX[2]},{TARGET_BBOX[3]});
#   node["amenity"~"theatre|cinema|arts_centre|library"]({TARGET_BBOX[0]},{TARGET_BBOX[1]},{TARGET_BBOX[2]},{TARGET_BBOX[3]});
#   node["leisure"~"park|garden|sports_centre|stadium"]({TARGET_BBOX[0]},{TARGET_BBOX[1]},{TARGET_BBOX[2]},{TARGET_BBOX[3]});
#   node["historic"]({TARGET_BBOX[0]},{TARGET_BBOX[1]},{TARGET_BBOX[2]},{TARGET_BBOX[3]});
#   node["shop"~"mall|department_store|gift|antiques|books"]({TARGET_BBOX[0]},{TARGET_BBOX[1]},{TARGET_BBOX[2]},{TARGET_BBOX[3]});
#   node["man_made"~"tower|bridge"]({TARGET_BBOX[0]},{TARGET_BBOX[1]},{TARGET_BBOX[2]},{TARGET_BBOX[3]});
# );
# out body;
# """

def get_overpass_query(ALL_BOX):
    overpass_querys = []

    for bbox, city in ALL_BOX:
        s, w, n, e = bbox

        query = f"""
        [out:json][timeout:180];
        (
        node["tourism"~"attraction|museum|gallery|zoo|theme_park|viewpoint|information"]({s},{w},{n},{e});
        node["amenity"~"theatre|cinema|arts_centre|library"]({s},{w},{n},{e});
        node["leisure"~"park|garden|sports_centre|stadium"]({s},{w},{n},{e});
        node["historic"]({s},{w},{n},{e});
        node["shop"~"mall|department_store|gift|antiques|books"]({s},{w},{n},{e});
        node["man_made"~"tower|bridge"]({s},{w},{n},{e});
        );
        out body;
        """

        overpass_querys.append((city, query))  # keep the name!

    return overpass_querys
    

def overpass_fetch(overpass_query):
    wait =  1
    while True:
        try:
            r = requests.post(OVERPASS_URL, data=overpass_query.encode("utf-8"))
            if r.status_code == 200:
                return r.json()["elements"]
            if r.status_code == 504:
                print(f"504 timeout. Sleeping {wait}s and retrying...")
                time.sleep(wait)
                continue
            
        except requests.exceptions.RequestException as e:
            print(f"Connection problem: {e}. Retry in {wait}s")
            time.sleep(wait)


def normalize_category(tags: dict) -> str:
    # Pick a simple “category” label
    for k in ["tourism", "amenity", "leisure", "historic", "shop", "man_made"]:
        if k in tags:
            return f"{k}:{tags.get(k)}"
    return "other"

def reverse_geocode(lat, lon, session):
    params = {
        "format": "jsonv2",
        "lat": lat,
        "lon": lon,
        "zoom": 18,
        "addressdetails": 1,
    }
    headers = {
        "User-Agent": "LondonPOI-Generator/1.0 (personal use; contact: none)"
    }
    r = session.get(NOMINATIM_URL, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    j = r.json()
    addr = j.get("address", {})
    postcode = addr.get("postcode", "")
    # Borough/district fields vary; try common keys:
    borough = (
        addr.get("borough")
        or addr.get("city_district")
        or addr.get("suburb")
        or addr.get("county")
        or ""
    )
    city = addr.get("city") or addr.get("town") or addr.get("village") or ""
    return postcode, borough, city


def get_activities(overpass_query, city, target_n=500):
    out_csv = f"data_collection/Activities/{city}_attractions_unfilt.csv"
    elements = overpass_fetch(overpass_query)
    rows = []
    seen = set()

    # Keep only named POIs with coordinates
    candidates = []
    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name")
        if not name:
            continue
        lat = el.get("lat")
        lon = el.get("lon")
        if lat is None or lon is None:
            continue
        key = (name.strip().lower(), round(lat, 6), round(lon, 6))
        if key in seen:
            continue
        seen.add(key)
        candidates.append((name, lat, lon, tags))

    # If there are tons, take the first chunk; you can also randomize.
    candidates = candidates[: max(target_n * 2, target_n)]

    with requests.Session() as session:
        for name, lat, lon, tags in tqdm(candidates, total=len(candidates)):
            category = normalize_category(tags)

            try:
                postcode, borough, city = reverse_geocode(lat, lon, session)
            except Exception:
                postcode, borough, city = "", "", ""

            # Only accept rows with a postcode (your requirement)
            if postcode:
                rows.append({
                    "No.": len(rows) + 1,
                    "Activity / Attraction": name,
                    "Category": category,
                    "Postcode": postcode,
                    "District/Borough": borough,
                    "City": city,
                    "Latitude": lat,
                    "Longitude": lon,
                })

            # Respect Nominatim usage: slow down (important)
            time.sleep(1.1)

            if len(rows) >= target_n:
                break

    df = pd.DataFrame(rows)
    df.to_csv(out_csv, index=False)
    print(f"Saved {len(df)} rows to {out_csv}")


def main(target_n=500, clean = False):
    for city, overpass_query in get_overpass_query(ALL_BOX):
        get_activities(overpass_query, city=city, target_n=target_n)

        if clean:
            df = pd.read_csv(f"data_collection/Activities/{city}_attractions_unfilt.csv")

            df[["Cat1", "Cat2"]] = df["Category"].str.split(":", expand=True)
            df['Popularity'] = [random.randint(1, 5) for _ in range(236)]
            df.to_csv(f'data_collection/Activities/{city}_attractions.csv')
            df.to_csv(f'data_collection/Databse/{city}_attractions.csv')


if __name__ == "__main__":
    main(target_n=20)
