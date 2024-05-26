from abc import abstractmethod
from aita.datasource.catalog import Catalog
from typing import List
from pydantic import BaseModel


class DataSource(BaseModel):
    type: str

    @abstractmethod
    def get_metadata(self, **kwargs) -> List[Catalog]:
        pass
