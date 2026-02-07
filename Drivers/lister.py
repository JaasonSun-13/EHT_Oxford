import numpy as np
import pandas as pd


def list_convert(df):
    # Create Name column
    df = df.copy()
    df["Name"] = df["First Name"] + " " + df["Last Name"]

    # Column boundaries
    start_city = df.columns.get_loc("City")
    end_city = df.columns.get_loc("City")+1
    start_attractions = df.columns.get_loc("BikeGuide")+1
    end_attractions = df.columns.get_loc("Language0")
    end_language = df.columns.get_loc("Language3") + 1
    start_services = df.columns.get_loc("Driver")
    end_sercives = df.columns.get_loc("BikeGuide") + 1

    col_city = df.columns[start_city:end_city]
    col_services = df.columns[start_services:end_sercives]
    col_attractions = df.columns[start_attractions:end_attractions]
    col_languages = df.columns[end_attractions:end_language]
    col_rate = "Rating" if "Rating" in df.columns else None
    col_unavaliable = df.columns[end_language+1: ]

    rows = []

    for _, r in df.iterrows():
        rows.append({
            "Name": r["Name"],
            "City": [r[col_city[0]] if len(col_city) else None],
            "Service": [c for c in col_services if r[c] == 1],
            "Activity / Attraction": [c for c in col_attractions if r[c] == 1],
            "Languages": [r[c] for c in col_languages if r[c] != '0'],
            "Rating": r[col_rate] if len(col_rate) else None,
            "Unavailable Dates": [c for c in col_unavaliable if r[c] == 1]
        })

    return pd.DataFrame(rows)



def main():
    df_drivers = pd.read_csv('data_collection/Drivers/drivers.csv')
    df_list_drive = list_convert(df_drivers)
    df_list_drive.to_csv('data_collection/Drivers/list_drive.csv')
    df_list_drive.to_csv('data_collection/Database/driver_identifier.csv')
    return df_list_drive


if __name__ == "__main__":
    main()


