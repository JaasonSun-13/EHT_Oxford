import numpy as np
import pandas as pd

def base_price(df):
    mapping = {
    "['Driver']": 3.5,
    "['Buddy']": 2,
    "['Driver-guide']": 5,
    "['BikeGuide']": 2.25
    }

    df["Hourly Price"] = round(5.5*df["Service"].map(mapping)*(1+0.1*df['Rating']), 2)

    df.to_csv('data_collection/Pricing/priced_driver.csv')
    df.to_csv('data_collection/Database/driver_identifier.csv')
    return


def Driver_pricing():
    df = pd.read_csv('data_collection/Database/driver_identifier.csv')
    base_price(df)
    return

if __name__ == "__main__":
    Driver_pricing()
