"""
Description: Data Quality checks (4 tests)
Requirement(s): TICKET-1234
Author(s): Nataliya Shabat
"""

import pytest
import pandas as pd
from src.data_quality.data_quality_validation_library import DataQualityLibrary

pytestmark = pytest.mark.example

@pytest.fixture(scope="module")
def source_data():
   """
   Simulated source data (Postgres)
   """
   return pd.DataFrame({
       "facility_name": ["A", "B", "C"],
       "visit_date": ["2024-01-01", "2024-01-02", "2024-01-03"],
       "min_time_spent": [10, 20, 30]
   })

@pytest.fixture(scope="module")
def target_data():
   """
   Simulated target data (Parquet)
   """
   return pd.DataFrame({
       "facility_name": [],
       "visit_date": [],
       "min_time_spent": []
   })

#Tests 
def test_dataset_is_not_empty(target_data):
   dq = DataQualityLibrary()
   dq.check_dataset_is_not_empty(target_data)


def test_check_count(source_data, target_data):
   dq = DataQualityLibrary()
   dq.check_count(source_data, target_data)


def test_check_not_null_values(target_data):
   dq = DataQualityLibrary()
   dq.check_not_null_values(
       target_data,
       ["facility_name", "visit_date", "min_time_spent"]
   )

def test_check_duplicates(target_data):
   dq = DataQualityLibrary()
   dq.check_duplicates(target_data)