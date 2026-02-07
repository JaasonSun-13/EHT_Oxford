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


def build_test_structure():
    names = [
        "Aaron Harris",
        "Abel Johnston",
        "Abraham Hicks",
        "Ace Kennedy",
        "Adam Silva",
        "Adonis Vasquez",
        "Adrian Webb",
        "Adriel Cole",
        "Aidan Gonzales",
        "Aiden Moreno",
        "Alan Garza",
        "Albert Sandoval",
        "Alden Bailey",
        "Alden Jimenez",
        "Alec Rogers",
        "Alejandro Rogers",
        "Alessandro Perez",
        "Alex Armstrong",
        "Alexander Carpenter",
        "Alfredo Clark",
        "Ali Spencer",
        "Allan Miller",
        "Alonzo Robinson",
    ]

    structure = []
    for n in names:
        d = Driver(name=n)
        structure.append(
            DriverScore(driver=d, score=random.randint(50, 100))
        )

    return structure


# build global test data
test_stucture = build_test_structure()

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


def driverplan_compat_adjust(structure, travel_time_str):

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
            total = time_adjust(base_total, travel_time_str)

        results.append(
            Driver_total_price(
                deriver=ds.driver,
                Total_price=total
            )
        )
    return results


def pricing():
    driverplan_compat_adjust(
        structure=test_stucture, travel_time_str='10/02/2026'
        )
    return

if __name__ == "__main__":
    pricing()