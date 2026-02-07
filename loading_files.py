from pathlib import Path
import pandas as pd

def load_attractions_by_city(city: str) -> list[str]:

    filename = city.strip().lower().replace(" ", "_") + ".csv"
    path = Path("data_collection/Database") / filename

    if not path.exists():
        return []

    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]

    # adjust column name if needed
    if "activity / attraction" not in df.columns:
        raise ValueError(f"Must contain an 'attraction' column")

    return (
        df["activity / attraction"]
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
    if "languages" not in df.columns:
        raise ValueError(f"Must contain an 'language' column")

    return (
        df["languages"]
        .dropna()
        .astype(str)
        .str.split(",")      # split each cell
        .explode()           # flatten into one column
        .str.strip()         # clean whitespace
        .str.lower()         # optional: normalize case
        .drop_duplicates()   # remove duplicates
        .sort_values()       # optional: nice ordering
        .tolist())
