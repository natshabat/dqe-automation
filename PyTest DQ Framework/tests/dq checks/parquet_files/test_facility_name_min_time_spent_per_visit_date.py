"""
Description: Data Quality checks (4 tests)
Requirement(s): TICKET-DQ-Automation-Framework
Author(s): Nataliya Shabat
"""

import pytest
import pandas as pd
from src.data_quality.data_quality_validation_library import DataQualityLibrary

#Tests 
@pytest.mark.parquet_data
def test_dataset_is_not_empty(target_data):
   dq = DataQualityLibrary()
   dq.check_dataset_is_not_empty(target_data)

@pytest.mark.parquet_data
def test_check_count(source_data, target_data):
   dq = DataQualityLibrary()
   dq.check_count(source_data, target_data)

@pytest.mark.parquet_data
def test_check_not_null_values(target_data):
   dq = DataQualityLibrary()
   dq.check_not_null_values(target_data)

@pytest.mark.parquet_data
def test_check_duplicates(target_data):
   dq = DataQualityLibrary()
   dq.check_duplicates(target_data)