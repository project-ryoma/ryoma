
from snowflake.connector import connect
import os


class SnowflakeClient:
    def __init__(self, user, password, account):
        self.user = user
        self.password = password
        self.account = account

    def run_query(self, query):
        conn = connect(
            user=self.user,
            password=self.password,
            account=self.account
        )
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()


# get snowflake configs from environment variables
snowflake_user = os.environ.get('SNOWFLAKE_USER', "")
snowflake_password = os.environ.get('SNOWFLAKE_PASSWORD', "")
snowflake_account = os.environ.get('SNOWFLAKE_ACCOUNT', "")

snowflake_client = SnowflakeClient(snowflake_user, snowflake_password, snowflake_account)