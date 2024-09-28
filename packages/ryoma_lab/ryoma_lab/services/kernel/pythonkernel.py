from typing import Any, Dict

from IPython.core.interactiveshell import InteractiveShell
from ryoma_lab.services.kernel.base import BaseKernel


class PythonKernel(BaseKernel):
    def execute(self, code: str) -> Dict[str, Any]:
        shell = InteractiveShell.instance()
        result = shell.run_cell(code, store_history=False)

        if result.success:
            return self._create_success_response(result.result)
        elif result.error_before_exec:
            return self._create_error_response(result.error_before_exec)
        elif result.error_in_exec:
            return self._create_error_response(result.error_in_exec)
        else:
            return self._create_error_response(Exception("An unknown error occurred"))
