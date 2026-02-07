from pathlib import Path
import pandas as pd

def load_attractions_by_city(city: str) -> list[str]:

    path = Path("data/attractions") / city.strip().lower().replace(" ", "_") + ".csv"

    if not path.exists():
        return []

    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]

    # adjust column name if needed
    if "Activity / Attraction" not in df.columns:
        raise ValueError(f"{path.name} must contain an 'attraction' column")

    return (
        df["Activity / Attraction"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )
