from typing import List

try:
    import boto3
except ImportError:
    boto3 = None

from ryoma_data.base import BaseDataSource
from ryoma_data.metadata import Catalog


class DynamodbDataSource(BaseDataSource):
    def __init__(self, name: str, region_name: str = None, **kwargs):
        super().__init__(name=name, type="nosql", **kwargs)
        self.region_name = region_name
        self.client = boto3.client("dynamodb", region_name=region_name)

    def get_catalog(self, table_name: str) -> List[Catalog]:
        response = self.client.describe_table(TableName=table_name)
        return response["Table"]


class DynamodbConfig:
    pass
