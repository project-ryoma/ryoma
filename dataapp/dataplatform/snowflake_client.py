
from snowflake.connector import connect
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

    def preview_table(self, database, table, schema: Optional[str] = None):        
        if not database or database == "my_database":
            raise ValueError("we need to specify database name when previewing table")
        if not table or table == "my_table":
            raise ValueError("we need to specify table name when previewing table")
        if not schema:
            schema = "public"
        query = f"SELECT * FROM {database}.{schema}.{table} LIMIT 10"
        return self.run_query(query)
    
    def ingest_data(self, configs, data):
        if not configs or not configs.get("database") or not configs.get("schema") or not configs.get("table"):
            raise ValueError("we need to specify database, schema and table name when ingesting data, got %s" % configs)
        database, schema, table = configs["database"], configs["schema"], configs["table"]
        conn = self.connect()
        cursor = conn.cursor()
        query = f"INSERT INTO {database}.{schema}.{table} VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.executemany(query, data)
        conn.commit()
        return


# get snowflake configs from environment variables
snowflake_user = os.environ.get('SNOWFLAKE_USER', "")
snowflake_password = os.environ.get('SNOWFLAKE_PASSWORD', "")
snowflake_account = os.environ.get('SNOWFLAKE_ACCOUNT', "")

snowflake_client = SnowflakeClient(snowflake_user, snowflake_password, snowflake_account)