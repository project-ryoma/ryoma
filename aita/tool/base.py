from abc import ABC
from typing import Optional

from langchain_core.tools import BaseTool
from langchain_core.pydantic_v1 import Field

from aita.datasource.base import DataSource


class DataSourceTool(BaseTool, ABC):
    datasource: Optional[DataSource] = Field(None, exclude=True)

    class Config(BaseTool.Config):
        pass
