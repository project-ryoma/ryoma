from abc import abstractmethod

from aita.datasource.catalog import Catalog
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List


class DataSource(BaseModel):
    type: str = Field(..., description="Type of the data source")

    @abstractmethod
    def get_metadata(self, **kwargs) -> List[Catalog]:
        pass
