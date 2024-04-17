from abc import ABC
from typing import Optional
import json
from sqlalchemy import create_engine, MetaData


class DataSource(ABC):
    pass


class SqlDataSource(DataSource):

    def __init__(self, connection_url: Optional[str] = None):
        self.engine = self.create_engine(connection_url)

    def create_engine(self, connection_url: Optional[str] = None):
        return create_engine(connection_url)

    def connect(self):
        return self.engine.connect()

    def execute(self, query: str, params=None):
        with self.connect() as connection:
            return connection.execute(query, *(params or ()))

    def get_metadata(self, **kwargs):
        # Reflect metadata from the existing database
        metadata = MetaData(bind=self.engine)
        metadata.reflect()

        # Serialize the database structure to a dictionary
        db_structure = {}
        for table_name, table in metadata.tables.items():
            db_structure[table_name] = {
                "columns": [{
                    "name": column.name,
                    "type": str(column.type),
                    "nullable": column.nullable,
                    "default": str(column.default),
                    "primary_key": column.primary_key,
                } for column in table.columns]
            }

        # Convert the dictionary to a JSON string
        db_structure_json = json.dumps(db_structure, indent=4)

        # For demonstration, print the JSON string
        return db_structure_json


class NosqlDataSource(DataSource):
    def __init__(self):
        pass

