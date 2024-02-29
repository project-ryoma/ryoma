from abc import ABC, abstractmethod

from sqlalchemy import create_engine


class DataSource(ABC):
    @abstractmethod
    def execute(self, query, params=None):
        pass


class SqlDataSource(DataSource):
    def __init__(self, connection_url: str):
        self.engine = create_engine(connection_url)

    def execute(self, query: str, params=None):
        with self.engine.connect() as connection:
            return connection.execute(query, *(params or ()))
