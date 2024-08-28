import asyncio
from typing import Any, Dict

import reflex as rx

from ryoma.datasource.base import DataSource
from ryoma_lab.services.kernel import BaseKernel
from ryoma_lab.services.pythonkernel import PythonKernel
from ryoma_lab.services.sqlkernel import SqlKernel


class KernelFactory:
    @staticmethod
    def create_kernel(kernel_type: str) -> BaseKernel:
        if kernel_type == "python":
            return PythonKernel()
        elif kernel_type == "sql":
            return SqlKernel()
        else:
            raise ValueError(f"Unsupported kernel type: {kernel_type}")
