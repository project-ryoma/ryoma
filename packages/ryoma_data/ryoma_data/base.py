from abc import ABC, abstractmethod
from typing import Any, Dict

from pydantic import BaseModel
from ryoma_data.metadata import Catalog


class BaseDataSource(BaseModel, ABC):
    model_config = {
        "arbitrary_types_allowed": True,
        "extra": "allow",
    }

    def __init__(self, type: str, **kwargs: Any):
        super().__init__(**kwargs)
        self.type = type

    @abstractmethod
    def get_catalog(self, **kwargs: Dict[str, Any]) -> Catalog:
        raise NotImplementedError("get_catalog is not implemented for this data source")
