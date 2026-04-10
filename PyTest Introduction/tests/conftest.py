import pytest
import pandas as pd

# Fixture to read the CSV file
@pytest.fixture(scope="session")
def read_csv_file():
    def _read(file_path):
        return pd.read_csv(file_path)
    return _read

# Fixture to validate the schema of the file
@pytest.fixture(scope="session")
def validate_schema():
    def _validate(actual_schema, expected_schema):
        return list(actual_schema)==list(expected_schema)
    return _validate


# Pytest hook to mark unmarked tests with a custom mark
def pytest_collection_modifyitems(items):
    for item in items:
        custom_marks = [mark.name for mark in item.iter_markers()]

        if not custom_marks:
            item.add_marker(pytest.mark.unmarked)

