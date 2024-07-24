from typing import Union

from abc import ABC, abstractmethod

from langchain_core.pydantic_v1 import BaseModel, Field

from aita.datasource.catalog import Catalog, Database, Table


class DataSource(BaseModel, ABC):
    type: str = Field(..., description="Type of the data source")

    @abstractmethod
    def get_metadata(self, **kwargs) -> Union[Catalog, Database, Table]:
        pass
