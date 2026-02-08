import numpy as np
import pandas as pd 
from datetime import datetime, timedelta
import holidays
from dataclasses import dataclass, field

import random




@dataclass
class Driver:
    name: str


@dataclass
class DriverScore:
    driver: Driver
    score: int
    hourly_price: float | None = field(default=None)
    total_price: float | None = field(default=None)


def time_adjust(base_price, time_str):
    dt = datetime.strptime(time_str, "%d/%m/%Y")
    surcharge = 1
    if dt.weekday() >= 5:
        surcharge = 1.5
    if dt.month == 12 and dt.day in [24, 25, 26]:
        surcharge += 4
    if dt.month in [7, 8]:
        surcharge += 1.5

    uk_holidays = holidays.UK(years=dt.year)
    if "Good Friday" in uk_holidays.get(dt.date(), "") or \
       "Easter Monday" in uk_holidays.get(dt.date(), ""):
        surcharge += 1.8

    return base_price * surcharge


def driverplan_compat_adjust(
        structure=test_stucture,
        activities_str=[0], 
        travel_time_str='10/02/2026',
        city_csv_loc='data_collection/Database/oxford.csv'):
    
    df_city = pd.read_csv(city_csv_loc)

    # convert to list if needed
    if isinstance(activities_str, str):
        activities = [x.strip() for x in activities_str.split(",")]
    else:
        activities = activities_str

    matched = df_city[df_city["Activity / Attraction"].isin(activities)]

    plan_price = matched["base_price"].sum()


    @dataclass
    class Driver_total_price:
        deriver: Driver
        Total_price: int

    # sort by compatibility score first
    structure.sort(key=lambda d: d.score, reverse=True)
    # discounting price
    count = len(structure)
    ratio = 0.985
    n = 20

    if count > 5:
        weights = [ratio ** i for i in range(min(count, n))]
        weights += [ratio ** n] * (count - len(weights))
    else:
        weights = [1] * count

    # apply weight
    for ds, w in zip(structure, weights):
        if ds.hourly_price is not None:
            ds.hourly_price *= w

    structure.sort(key=lambda d: d.hourly_price or 0, reverse=True)
    results = []
    for ds in structure:
        if ds.hourly_price is None:
            total = "N/A"
        else:
            base_total = ds.hourly_price * 8
            base_total += plan_price
            total = time_adjust(base_total, travel_time_str)

        results.append(
            Driver_total_price(
                deriver=ds.driver,
                Total_price=total
            )
        )
    return results


if __name__ == "__main__":
    driverplan_compat_adjust()