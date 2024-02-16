# create a metadata store the data source connection details
# data source connection details include the username, password
# use postgresql as the database for the metadata store

import os
from sqlalchemy import create_engine


class MetaStore:
    def __init__(self, datasource):
        self.datasource = datasource
        self.engine = create_engine(f'postgresql://postgres:xxxxxxxxxxxxxxxxxx.xxxxxxxxx@xxxxxxxxxxxxxxxxxx:5432/metadb')
    
    def insert(self, datasource, connection_params):
        with self.engine.connect() as conn:
            conn.execute(f"INSERT INTO datasource (datasource, host, port, username, password, database) VALUES ('{datasource}', '{connection_params.host}', {connection_params.port}, '{connection_params.username}', '{connection_params.password}', '{connection_params.database}')")
            conn.close()
    
    def get(self, datasource):
        with self.engine.connect() as conn:
            result = conn.execute(f"SELECT * FROM datasource WHERE datasource = '{datasource}'")
            conn.close()
            return result.fetchone()


class StateStore:
    def __init__(self):
        self.cache = {}


state_store = StateStore()