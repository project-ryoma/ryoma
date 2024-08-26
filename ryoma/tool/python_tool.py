import logging
from typing import Any, Dict, Sequence, Type, Union

from IPython import get_ipython
from IPython.core.interactiveshell import ExecutionResult, InteractiveShell
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool

log = logging.getLogger(__name__)


class PythonInput(BaseModel):
    script: str = Field(description="python script")


class PythonTool(BaseTool):
    """Tool for running python script in an IPython environment."""

    name: str = "run_ipython_script_tool"
    description: str = """
    Execute a python script in an IPython environment and return the result of the last expression.
    If the script is not correct, an error message will be returned.
    """
    args_schema: Type[BaseModel] = PythonInput

    ipython: InteractiveShell = None

    def __init__(self, /, **data: Any):
        super().__init__(**data)
        self.ipython = get_ipython()
        if not self.ipython:
            self.ipython = InteractiveShell()

    def _run(
        self,
        script,
    ) -> Union[str, Sequence[Dict[str, Any]], ExecutionResult]:
        """Execute the script, return the result or an error message."""
        try:
            result = self.ipython.run_cell(script)
            return result
        except Exception as e:
            return str(e)

    def update_script_context(self, script_context: Any):
        try:
            self.ipython.user_ns.update(script_context)
        except Exception as e:
            return str(e)
