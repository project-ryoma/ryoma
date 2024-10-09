from typing import List

try:
    import boto3
except ImportError:
    boto3 = None

from ryoma_ai.datasource.base import DataSource
from ryoma_ai.datasource.metadata import Catalog


class DynamodbDataSource(DataSource):
    def __init__(self, region_name: str = None, **kwargs):
        super().__init__("nosql", **kwargs)
        self.region_name = region_name
        self.client = boto3.client("dynamodb", region_name=region_name)

    def get_catalog(self, table_name: str) -> List[Catalog]:
        response = self.client.describe_table(TableName=table_name)
        return response["Table"]


class DynamodbConfig:
    pass
