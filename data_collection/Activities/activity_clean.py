import numpy as np
import pandas as pd 
import random


df = pd.read_csv('data_collection/Activities/oxford236v1.csv')

df[["Cat1", "Cat2"]] = df["Category"].str.split(":", expand=True)
df['Popularity'] = [random.randint(1, 5) for _ in range(236)]
df.to_csv('data_collection/Activities/oxford.csv')
df.to_csv('data_collection/Databse/oxford.csv')