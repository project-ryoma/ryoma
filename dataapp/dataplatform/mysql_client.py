import mysql.connector
import os

class MysqlClient:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def run_query(self, query):
        conn = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()
    
    def run_query_with_params(self, query, params):
        conn = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    

# get mysql configs from environment variables
mysql_host = os.environ.get('MYSQL_HOST', "")
mysql_user = os.environ.get('MYSQL_USER', "")
mysql_password = os.environ.get('MYSQL_PASSWORD', "")
mysql_database = os.environ.get('MYSQL_DATABASE', "")

mysql_client = MysqlClient(mysql_host, mysql_user, mysql_password, mysql_database)
