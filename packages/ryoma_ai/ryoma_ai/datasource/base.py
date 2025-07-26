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
    def crawl_catalog(self, loader: Any, **kwargs) -> Optional[Catalog]:
        raise NotImplementedError(
            "crawl_metadata is not implemented for this data source."
        )

    @abstractmethod
    def prompt(self):
        raise NotImplementedError(
            "crawl_metadata is not implemented for this data source."
        )

    @abstractmethod
    def profile_table(self, table_name: str, **kwargs) -> dict:
        """
        Profile a table and return its metadata.

        Args:
            table_name (str): The name of the table to profile.
            **kwargs: Additional parameters for profiling.

        Returns:
            dict: A dictionary containing the table's metadata.
        """
        raise NotImplementedError("profile_table is not implemented for this data source.")
