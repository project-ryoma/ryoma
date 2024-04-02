from abc import ABC, abstractmethod

from sqlalchemy import create_engine


class DataSource(ABC):
    @abstractmethod
    def execute(self, query: str, params: None):
        pass


class SqlDataSource(DataSource):
    def __init__(self, connection_url: str):
        self.connection_url = connection_url
        self.engine = create_engine(connection_url)

    def execute(self, query: str, params=None):
        with self.engine.connect() as connection:
            return connection.execute(query, *(params or ()))


class NosqlDataSource(DataSource):
    def __init__(self):
        pass

    def execute(self, query, params=None):
        pass
