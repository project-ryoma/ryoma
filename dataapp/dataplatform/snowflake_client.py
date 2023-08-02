
from snowflake.connector import connect
import os


class SnowflakeClient:
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

    def preview_table(self, database, schema, table):        
        if not database:
            raise ValueError("database cannot be None")
        if not schema:
            raise ValueError("schema cannot be None")
        if not table:
            raise ValueError("table cannot be None")
        query = f"SELECT * FROM {database}.{schema}.{table} LIMIT 10"
        return self.run_query(query)


# get snowflake configs from environment variables
snowflake_user = os.environ.get('SNOWFLAKE_USER', "")
snowflake_password = os.environ.get('SNOWFLAKE_PASSWORD', "")
snowflake_account = os.environ.get('SNOWFLAKE_ACCOUNT', "")

snowflake_client = SnowflakeClient(snowflake_user, snowflake_password, snowflake_account)