import pandas as pd
from bs4 import BeautifulSoup
from typing import Optional, Tuple
from robot.api import logger
import pyarrow.parquet as pq

def extract_html_table_to_df(table_element, filter_date: Optional[str]=None) -> pd.DataFrame:
    html = table_element.get_attribute("outerHTML")
    soup = BeautifulSoup(html, "html.parser")

    columns = soup.find_all("g", class_="y-column")
    data=[]
    for col in columns:
        texts = [t.get_text(strip=True) for t in col.find_all("text", class_="cell-text")]

        texts = [t for t in texts if t.lower() not in ["facility type", "visit date", "average time spent"]]
        data.append(texts)

    min_len = min(len(col) for col in data)
    data = [col[:min_len] for col in data]

    df = pd.DataFrame(list(zip(*data)))
    df.columns = ["facility_type", "visit_date","average_time_spent"]

    df["visit_date"]=pd.to_datetime(df["visit_date"]).dt.date
    df["average_time_spent"]=pd.to_numeric(df["average_time_spent"], errors="coerce")

    if filter_date:
        df = df[df["visit_date"] == pd.to_datetime(filter_date).date()]



    return df

def read_parquet_dataset(folder_path: str, filter_date: Optional[str] = None) -> pd.DataFrame:
    """
    Reads partitioned parquet dataset and optionally filters by date.
    """

    df = pd.read_parquet(folder_path)

    # normalize column names
    df.columns = [c.strip().lower() for c in df.columns]
    df=df.rename(columns={"avg_time_spent": "average_time_spent"})


    needed_cols=["facility_type", "visit_date", "average_time_spent"]
    df = df[[c for c in needed_cols if c in df.columns]]

    df["visit_date"]=pd.to_datetime(df["visit_date"], unit="ms").dt.date
    df["average_time_spent"]=pd.to_numeric(df["average_time_spent"], errors="coerce")

    if filter_date:
        df = df[df["visit_date"] == pd.to_datetime(filter_date).date()]
    
    df = df.groupby(["facility_type", "visit_date"], as_index=False)["average_time_spent"].mean()
    return df

def normalize_df(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    # strip column names
    df.columns = [c.strip().lower() for c in df.columns]

    # strip string values
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip()

    # sort columns
    df = df.reindex(sorted(df.columns), axis=1)

    # sort rows for stable comparison
    df = df.sort_values(by=list(df.columns)).reset_index(drop=True)

    return df

def compare_dataframes(df1: pd.DataFrame, df2: pd.DataFrame) -> Tuple[bool, str]:

    df1_n = normalize_df(df1)
    df2_n = normalize_df(df2)

    if df1_n.equals(df2_n):
        return True, "Datasets match exactly."

    # detailed diff
    only_html = pd.merge(df1_n, df2_n, how="left", indicator=True).query('_merge == "left_only"').drop(columns="_merge")
    only_parquet = pd.merge(df2_n, df1_n, how="left", indicator=True).query('_merge == "left_only"').drop(columns="_merge")

    report = f""" DATA MISMATCH DETECTED
    ---only in HTML---     
    {only_html.to_string(index=False) }

    ---only in Parquet---
    {only_parquet.to_string(index=False) }
   
    """
    return False, report
