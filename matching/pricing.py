import pandas as pd
import holidays
from datetime import date
from matching.driver import Driver, DriverScore

from dataclasses import dataclass

@dataclass
class Driver_total_price:
    driver: Driver
    total_price: int


def time_adjust(base_price, dt: date):
    surcharge = 1
    if dt.weekday() >= 5:
        surcharge = 1.5
    if dt.month == 12 and dt.day in [24, 25, 26]:
        surcharge += 4
    if dt.month in [7, 8]:
        surcharge += 1.5

    uk_holidays = holidays.UK(years=dt.year)
    if "Good Friday" in uk_holidays.get(dt, "") or \
       "Easter Monday" in uk_holidays.get(dt, ""):
        surcharge += 1.8

    return base_price * surcharge


def driverplan_compat_adjust(
        driver_score: list[DriverScore],
        chosen_date: date,
        activities: list[str],
        budget: int,
        city_csv_loc='data_collection/Database/oxford.csv'):
    
    df_city = pd.read_csv(city_csv_loc)

    # convert to list if needed
    if isinstance(activities, str):
        activities = [x.strip() for x in activities.split(",")]
    else:
        activities = activities

    matched = df_city[df_city["Activity / Attraction"].isin(activities)]

    plan_price = matched["base_price"].sum()

    # discounting price
    count = len(driver_score)
    ratio = 0.985
    n = 20

    if count > 5:
        weights = [ratio ** i for i in range(min(count, n))]
        weights += [ratio ** n] * (count - len(weights))
    else:
        weights = [1] * count

    # apply weight
    for ds, w in zip(driver_score, weights):
        if ds.driver.hourly_price is not None:
            ds.driver.hourly_price *= w

    driver_score.sort(key=lambda d: d.driver.hourly_price or 0, reverse=True)
    results = []
    for ds in driver_score:
        if ds.driver.hourly_price is None:
            total = "N/A"
        else:
            base_total = ds.driver.hourly_price * 8
            base_total += plan_price
            total = time_adjust(base_total, chosen_date)

        if total <= budget:
            results.append(
                Driver_total_price(
                    driver=ds.driver,
                    total_price=total
                )
            )
    return results
