import psycopg2
import os
from abc import ABC, abstractmethod
from dataplatform.datasource.datasource_client import DataSourceClient


class PostgresClient(DataSourceClient):
    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        conn = psycopg2.connect(
            host=self.host,
            port=self.port,
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


# get postgresql configs from environment variables
postgres_host = os.environ.get('POSTGRES_HOST', "")
postgres_port = os.environ.get('POSTGRES_PORT', "")
postgres_user = os.environ.get('POSTGRES_USER', "")
postgres_password = os.environ.get('POSTGRES_PASSWORD', "")
postgres_database = os.environ.get('POSTGRES_DATABASE', "")

postgres_client = PostgresClient(postgres_host, postgres_port, postgres_user, postgres_password, postgres_database)