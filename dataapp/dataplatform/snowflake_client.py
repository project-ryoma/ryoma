
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
