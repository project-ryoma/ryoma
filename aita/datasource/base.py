from abc import ABC, abstractmethod
from aita.datasource.catalog import Catalog
from typing import List


class DataSource(ABC):

    @abstractmethod
    def get_metadata(self, **kwargs) -> List[Catalog]:
        pass

