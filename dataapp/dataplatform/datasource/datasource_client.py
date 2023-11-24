from abc import ABC, abstractmethod

class DataSourceClient(ABC):
    """Base class for all data source clients"""

    @abstractmethod
    def connect(self):
        """connect to data source"""
        pass       

    @abstractmethod
    def run_query(self, query):
        """run query on data source"""
        pass

    @abstractmethod
    def run_query_with_params(self, query, params):
        """run query on data source with params"""
        pass

    @abstractmethod
    def preview_table(self, database, table, schema):
        """preview table on data source"""
        pass

    @abstractmethod
    def ingest_data(self, database, table, data):
        """ingest data to data source"""
        pass