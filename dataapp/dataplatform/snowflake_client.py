
from snowflake.connector import connect
from snowflake.connector.pandas_tools import write_pandas
import os
from typing import Optional
from dataplatform.datasource_client import DataSourceClient


class SnowflakeClient(DataSourceClient):
    def __init__(self, user, password, account):
        self.user = user
        self.password = password
        self.account = account
    
    def connect(self):
        conn = connect(
            user=self.user,
            password=self.password,
            account=self.account
        )
        return conn        

    def run_query(self, query):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()
    
    def run_query_with_params(self, query, params):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def preview_table(self, database: str, table: str, schema: str):        
        if not database or database == "my_database":
            raise ValueError("we need to specify database name when previewing table")
        if not table or table == "my_table":
            raise ValueError("we need to specify table name when previewing table")
        if not schema or schema == "my_schema":
            raise ValueError("we need to specify schema when previewing table")
        query = f"SELECT * FROM {database}.{schema}.{table} LIMIT 10"
        return self.run_query(query)

    def ingest_data(self, df, database, table, schema: Optional[str] = None):
        if not schema:
            schema = "public"

        # format database, schema and table names to upper case
        database = database.upper()
        schema = schema.upper()
        table = table.upper()

        conn = self.connect()
        res = write_pandas(conn, df, table_name=table, database=database, schema=schema, overwrite=True)
        return res
    
# get snowflake configs from environment variables
snowflake_user = os.environ.get('SNOWFLAKE_USER', "")
snowflake_password = os.environ.get('SNOWFLAKE_PASSWORD', "")
snowflake_account = os.environ.get('SNOWFLAKE_ACCOUNT', "")

snowflake_client = SnowflakeClient(snowflake_user, snowflake_password, snowflake_account)