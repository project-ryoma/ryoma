import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import reflex as rx

from ryoma.datasource.base import DataSource


class BaseKernel(rx.Base):
    datasources: dict[str, DataSource] = {}

    def set_datasources(self, datasources: Dict[str, DataSource]):
        self.datasources = datasources

    def get_datasource(self, datasource_name: str) -> Optional[Any]:
        return self.datasources.get(datasource_name)

    def add_datasource(self, datasource: DataSource):
        self.datasources[datasource.name] = datasource

    async def execute_code(self, code: str) -> Dict[str, Any]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.execute, code)

    @abstractmethod
    def execute(self, code: str) -> Dict[str, Any]:
        pass

    def _create_error_response(self, error: Exception) -> Dict[str, Any]:
        return {
            "output_type": "error",
            "ename": type(error).__name__,
            "evalue": str(error),
        }

    def _create_success_response(self, result: Any) -> Dict[str, Any]:
        return {
            "output_type": "execute_result",
            "data": {"text/plain": str(result)},
        }
