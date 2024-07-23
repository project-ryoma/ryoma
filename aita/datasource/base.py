from typing import Union

from abc import abstractmethod

from langchain_core.pydantic_v1 import BaseModel, Field

from aita.datasource.catalog import Catalog, Schema, Table


class DataSource(BaseModel):
    type: str = Field(..., description="Type of the data source")

    @abstractmethod
    def get_metadata(self, **kwargs) -> Union[Catalog, Schema, Table]:
        pass
