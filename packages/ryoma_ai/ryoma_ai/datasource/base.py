from abc import ABC, abstractmethod
from typing import Any, Optional

from pydantic import BaseModel
from ryoma_ai.datasource.metadata import Catalog


class DataSource(BaseModel, ABC):

    model_config = {
        "arbitrary_types_allowed": True,
        "extra": "allow",
    }

    def __init__(self, type: str, **kwargs):
        super().__init__(**kwargs)
        self.type = type

    @abstractmethod
    def get_catalog(self, **kwargs) -> Catalog:
        raise NotImplementedError("get_catalog is not implemented for this data source")

    @abstractmethod
    def crawl_catalogs(self, loader: Any, **kwargs) -> Optional[Catalog]:
        raise NotImplementedError(
            "crawl_metadata is not implemented for this data source."
        )
