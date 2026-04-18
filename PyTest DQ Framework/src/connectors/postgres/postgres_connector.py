
from turtle import pd
import psycopg2
import pandas as pd

class PostgresConnectorContextManager:
    def __init__(self, db_user, db_password, db_host, db_name, db_port):
        self.db_user = db_user
        self.db_password = db_password
        self.db_host = db_host
        self.db_name = db_name
        self.db_port = db_port
        self.connection = None

    def __enter__(self):
        self.connection = psycopg2.connect(
            user=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name
        )
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.connection:
            self.connection.close()

    def get_data_sql(self, query):
        import pandas as pd
        return pd.read_sql_query(query, self.connection)
        


