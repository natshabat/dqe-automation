import pandas as pd
import pytest
import re

file_path=r"C:\\Users\\NataliyaShabat\\dqe-automation\\PyTest Introduction\\src\\data\\data.csv"

def test_file_not_empty(read_csv_file):
    df =read_csv_file(file_path)
    assert not df.empty, "data.csv is empty"

@pytest.mark.validate_csv
def test_validate_schema(read_csv_file,validate_schema):
    df =read_csv_file(file_path)
    expected_colunms = ["id","name","age","email","is_active"]
    assert validate_schema(df.columns, expected_colunms), f"Schema mismatch.Expected {expected_colunms}, got {list(df.columns)}"

@pytest.mark.validate_csv
@pytest.mark.skip 
def test_age_column_valid(read_csv_file):
    df =read_csv_file(file_path)
    assert df["age"].between(0,100).all, "Invalid values in AGE column"
    
@pytest.mark.validate_csv
def test_email_column_valid(read_csv_file):
    df =read_csv_file(file_path)
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    invalid_emails = df[~df["email"].str.match(pattern)]
    assert invalid_emails.empty, f"Invalid email: {invalid_emails["email"].tolist()}"

@pytest.mark.validate_csv
@pytest.mark.xfail (reason="Known duplicate")
def test_duplicates(read_csv_file):
    df =read_csv_file(file_path)
    duplicates = df[df.duplicated()]
    assert duplicates.empty, f"Duplicates found:{duplicates}"

@pytest.mark.parametrize("id, is_active", [(1,False),(2,True)])
def test_active_players(id, is_active, read_csv_file):
    df =read_csv_file(file_path)
    actual_value =df.loc[df["id"]==id,"is_active"].iloc[0]
    assert actual_value == is_active, f"For id {id}:expected is_active={is_active}, but got{actual_value}"


def test_active_player(read_csv_file):
    df =read_csv_file(file_path)
    actual_values = df.loc[df["id"] == 2, "is_active"].values
    assert len(actual_values) > 0, "No record found for ID 2"
    actual_value = actual_values[0]
    assert actual_value == True, f"Expected is_active=True for ID 2, but got {actual_value}"
