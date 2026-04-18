import pytest
import pandas as pd
import psycopg2 
from src.connectors.postgres.postgres_connector import PostgresConnectorContextManager
from src.data_quality.data_quality_validation_library import DataQualityLibrary
from src.connectors.file_system.parquet_reader import ParquetReader

def pytest_addoption(parser):
    parser.addoption("--db_host", action="store", default="localhost", help="Database host")
    parser.addoption("--db_port", action="store", default="5434", help="Database port")
    parser.addoption("--db_user", action="store", help="Database user")
    parser.addoption("--db_password", action="store", help="Database password")
    parser.addoption("--db_name", action="store", default="mydatabase", help="Database name")

def pytest_configure(config):
    """
    Validates that all required command-line options are provided.
    """
    required_options = [
        "--db_user", "--db_password"
    ]
    for option in required_options:
        if not config.getoption(option):
            pytest.fail(f"Missing required option: {option}")

@pytest.fixture(scope='session')
def db_connection(request):
    """
    Initializes a database connection using the PostgresConnectorContextManager.
    The connection parameters are retrieved from command-line options.
    """
    db_host = request.config.getoption("--db_host")
    db_port = request.config.getoption("--db_port")
    db_user = request.config.getoption("--db_user")
    db_password = request.config.getoption("--db_password")
    db_name = request.config.getoption("--db_name")
    try:
        with PostgresConnectorContextManager(
            db_user=db_user, 
            db_password=db_password, 
            db_host=db_host, 
            db_port=db_port, 
            db_name=db_name) as db_connector:
            yield db_connector
    except Exception as e:
        pytest.fail(f"Failed to initialize PostgresConnectorContextManager: {e}")

@pytest.fixture(scope='session')
def parquet_reader():
    return ParquetReader()

@pytest.fixture(scope="module")
def target_data(parquet_reader):
    import os
    path = "tests/data/parquet_data/facility_name_min_time_spent_per_visit_date"
    #print("Path exists:",os.path.isdir(path))

    df = parquet_reader.process(path)
    df = df.groupby(['facility_name', 'visit_date'], as_index=False)['min_time_spent'].min()
    # if df is None or df.empty:
    #     pytest.fail("Parquet data is empty or failed to load.")
    #print("Targetshape:", df.shape)
    #print("Duplicates:", df.duplicated(subset=['facility_name', 'visit_date']).sum())

    dups = df[df.duplicated(subset=['facility_name', 'visit_date'], keep=False)]
    print("Sample duplicates:")
    #print(dups.head(10))

    return df

@pytest.fixture(scope="module")
def source_data(db_connection):
   query = """
   SELECT
    f.id,
    f.facility_name,
    DATE(v.visit_timestamp) AS visit_date,
    MIN(v.duration_minutes) AS min_time_spent
   FROM visits v
   JOIN facilities f ON f.id = v.facility_id
   GROUP BY
    f.id,
    f.facility_name,
    DATE(v.visit_timestamp)
   """
   return db_connection.get_data_sql(query)
