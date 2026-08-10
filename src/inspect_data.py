import pandas as pd

file_path = "data/raw/SP500_Historical_Data.csv"

df = pd.read_csv(file_path)

print("First 5 rows:")
print(df.head())

print("\nColumns:")
print(df.columns.tolist())

print("\nShape:")
print(df.shape)

print("\nData types:")
print(df.dtypes)

print("\nMissing values:")
print(df.isnull().sum())