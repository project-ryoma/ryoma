import asyncio
import traceback
from abc import abstractmethod
from typing import Any, Dict, Optional

from ryoma_ai.datasource.base import DataSource


class BaseKernel:
    datasource: DataSource

    def __init__(self, datasource: Optional[DataSource] = None, **kwargs):
        self.datasource = datasource

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
            "traceback": self._format_traceback(error),
        }

    def _create_success_response(self, result: Any) -> Dict[str, Any]:
        return {
            "output_type": "execute_result",
            "data": {"text/plain": str(result)} if result is not None else None,
        }

    def _format_traceback(self, error: Exception) -> str:
        return "".join(
            traceback.format_exception(type(error), error, error.__traceback__)
        )

    def set_datasource(self, datasource: DataSource):
        self.datasource = datasource
