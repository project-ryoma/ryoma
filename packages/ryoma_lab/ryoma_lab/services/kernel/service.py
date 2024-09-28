from typing import Optional

from ryoma_ai.datasource.base import DataSource
from ryoma_lab.services.kernel.base import BaseKernel
from ryoma_lab.services.kernel.pythonkernel import PythonKernel
from ryoma_lab.services.kernel.sqlkernel import SqlKernel


class KernelService:
    def __init__(self, datasource: Optional[DataSource] = None):
        self.datasource = datasource

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def create_kernel(self, kernel_type: str, **kwargs) -> BaseKernel:
        if kernel_type == "sql":
            kernel = SqlKernel(datasource=self.datasource, **kwargs)
            return kernel
        elif kernel_type == "python":
            return PythonKernel(datasource=self.datasource, **kwargs)
        else:
            raise ValueError(f"Unsupported kernel type: {kernel_type}")

    def set_datasource(self, datasource: DataSource):
        self.datasource = datasource

    def get_datasource(self) -> Optional[DataSource]:
        return self.datasource
