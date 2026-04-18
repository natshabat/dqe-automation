import pandas as pd
import os

class ParquetReader:
   def process(self, path, include_subfolders=True):
       """
       Reads parquet files from a given directory and returns a combined DataFrame
       """
       all_files = []
       # if folder
       if os.path.isdir(path):
           for root, dirs, files in os.walk(path):
               for file in files:
                   if file.endswith(".parquet"):
                       full_path = os.path.join(root, file)
                       all_files.append(full_path)
               if not include_subfolders:
                   break
       # if one file
       elif path.endswith(".parquet"):
           all_files.append(path)
       else:
           raise ValueError(f"Invalid path: {path}")
       if not all_files:
           raise ValueError("No parquet files found")
       # read all files
       dataframes = [pd.read_parquet(file) for file in all_files]
       return pd.concat(dataframes, ignore_index=True)