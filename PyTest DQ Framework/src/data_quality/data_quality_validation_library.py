import pandas as pd


class DataQualityLibrary:
    """
    A library of static methods for performing data quality checks on pandas DataFrames.

    This class is intended to be used in a PyTest-based testing framework to validate
    the quality of data in DataFrames. Each method performs a specific data quality
    check and uses assertions to ensure that the data meets the expected conditions.
    """

    @staticmethod
    def check_duplicates(df, column_names=None):
        if column_names:
            df.duplicates = df.duplicated(subset=column_names).sum()
        else:
            duplicates = df.duplicated().sum()
        assert duplicates == 0, f"DataFrame contains {duplicates} duplicate rows."

    @staticmethod
    def check_count(df1, df2):
        assert len(df1) == len(df2), f"Row counts differ: source {len(df1)} vs target {len(df2)}."

    @staticmethod
    def check_data_full_data_set(df1, df2):
        assert df1.shape == df2.shape, f"Data shapes differ: source {df1.shape} vs target {df2.shape}."

    @staticmethod
    def check_dataset_is_not_empty(df):
       assert not df.empty, "DataFrame is empty."

    @staticmethod
    def check_not_null_values(df, column_names=None):
        if column_names:
           for col in column_names:
               assert df[col].notnull().all(), f"Column '{col}' contains null values."
        else:
            assert df.notnull().all().all(), "DataFrame contains null values."