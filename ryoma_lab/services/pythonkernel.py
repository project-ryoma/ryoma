from typing import Any, Dict

from IPython.core.interactiveshell import InteractiveShell

from ryoma_lab.services.kernel import BaseKernel


class PythonKernel(BaseKernel):
    def execute(self, code: str) -> Dict[str, Any]:
        shell = InteractiveShell.instance()
        result = shell.run_cell(code, store_history=False)
        return {
            "output_type": "execute_result" if result.success else "error",
            "data": {"text/plain": str(result.result)}
            if result.result is not None
            else None,
            "ename": type(result.error_in_exec).__name__
            if result.error_in_exec
            else None,
            "evalue": str(result.error_in_exec) if result.error_in_exec else None,
        }
