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
    df.to_csv('data_collection/Database/oxford.csv')
    return


# def compat_adjustment()


def Activities_pricing():
    df = pd.read_csv('data_collection/Database/oxford.csv')
    activity_base_price(df)
    return

if __name__ == "__main__":
    Activities_pricing()


    




    


