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

def load_languages(file: str) -> list[str]:
    df = pd.read_csv(file)
    df.columns = [c.strip().lower() for c in df.columns]

    # adjust column name if needed
    if "Languages" not in df.columns:
        raise ValueError(f"{file.name} must contain an 'attraction' column")

    return (
        df["Languages"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )
