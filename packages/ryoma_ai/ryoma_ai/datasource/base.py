from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from databuilder.loader.base_loader import Loader
from pydantic import BaseModel
from ryoma_ai.datasource.metadata import Catalog


class DataSource(BaseModel, ABC):

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

    @abstractmethod
    def crawl_catalog(self, loader: Loader, **kwargs: Dict[str, Any]) -> Optional[Catalog]:
        raise NotImplementedError(
            "crawl_catalog is not implemented for this data source."
        )

    @abstractmethod
    def prompt(self, schema: Optional[str] = None, table: Optional[str] = None) -> str:
        raise NotImplementedError(
            "prompt is not implemented for this data source."
        )

    @abstractmethod
    def profile_table(self, table_name: str, **kwargs: Dict[str, Any]) -> dict:
        """
        Profile a table and return its metadata.

        Args:
            table_name (str): The name of the table to profile.
            **kwargs: Additional parameters for profiling.

        Returns:
            dict: A dictionary containing the table's metadata.
        """
        raise NotImplementedError("profile_table is not implemented for this data source.")
