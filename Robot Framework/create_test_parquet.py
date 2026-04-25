import pandas as pd

data=[
    {"facility_type": "Clinic", "visit_date": "2026-03-17", "average_time_spent": 19.00},
    {"facility_type": "Hospital", "visit_date": "2026-03-17", "average_time_spent": 35.33},
    {"facility_type": "Specialty Center", "visit_date": "2026-03-17", "average_time_spent": 57.50}
]

df = pd.DataFrame(data)

df["visit_date"] = pd.to_datetime(df["visit_date"]).map(lambda x: int(x.timestamp() * 1000))
df=df.rename(columns={"average_time_spent": "avg_time_spent"})

print(type(df))
print(df)
df.to_parquet("test_dataset.parquet", index=False)

print("Parquet file created successfully.")