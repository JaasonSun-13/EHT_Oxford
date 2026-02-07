import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import holidays


def activity_base_price(df):
    mapping = {
    "amenity": 2,
    "historic": 4,
    "tourism": 5,
    "shop": 0,
    "historic": 2,
    "leisure": 3
    }

    df["cat1_index"] = df["Cat1"].map(mapping)

    df['base_price'] = (df["cat1_index"] + 0.5 * df['Popularity'])*3
    df.to_csv('data_collection/Pricing/priced_activity.csv')
    return


def time_adjustment(time_str):
    dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    surcharge = 1
    if dt.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        surcharge = 1.5

    if dt.month == 12 and dt.day in [24, 25, 26]:
        surcharge += 4

    if dt.month in [7, 8]:
        surcharge += 1.5

    uk_holidays = holidays.UK(years=dt.year)
    if "Good Friday" in uk_holidays.get(dt.date(), "") or \
       "Easter Monday" in uk_holidays.get(dt.date(), ""):
        surcharge += 1.8
    return surcharge


# def compat_adjustment()


def main():
    df = pd.read_csv('data_collection/Database/oxford.csv')
    activity_base_price(df)
    return

if __name__ == "__main__":
    main()


    




    


