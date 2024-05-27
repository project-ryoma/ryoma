from typing import Any, Dict, Sequence, Type, Union

import logging

from IPython import get_ipython
from IPython.core.interactiveshell import ExecutionResult, InteractiveShell
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

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

    script_context: Dict[str, Any]

    def _run(
        self,
        script,
    ) -> Union[str, Sequence[Dict[str, Any]], ExecutionResult]:
        """Execute the script, return the result or an error message."""
        try:
            ipython = get_ipython()
            if not ipython:
                ipython = InteractiveShell()

            if self.script_context:
                ipython.user_ns.update(self.script_context)

            result = ipython.run_cell(script)
            return result
        except Exception as e:
            return str(e)
