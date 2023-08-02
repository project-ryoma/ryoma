import mysql.connector
import os

class MysqlClient:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        conn = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
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
    
    def preview_table(self, database, table):
        query = f"SELECT * FROM {database}.{table} LIMIT 10"
        return self.run_query(query)
    

# get mysql configs from environment variables
mysql_host = os.environ.get('MYSQL_HOST', "")
mysql_user = os.environ.get('MYSQL_USER', "")
mysql_password = os.environ.get('MYSQL_PASSWORD', "")
mysql_database = os.environ.get('MYSQL_DATABASE', "")

mysql_client = MysqlClient(mysql_host, mysql_user, mysql_password, mysql_database)
