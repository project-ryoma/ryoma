from ryoma_lab.services.kernel.base import BaseKernel
from ryoma_lab.services.kernel.pythonkernel import PythonKernel
from ryoma_lab.services.kernel.sqlkernel import SqlKernel


class KernelFactory:
    @staticmethod
    def create_kernel(kernel_type: str, *args, **kwargs) -> BaseKernel:
        if kernel_type == "python":
            return PythonKernel(*args, **kwargs)
        elif kernel_type == "sql":
            return SqlKernel(*args, **kwargs)
        else:
            raise ValueError(f"Unsupported kernel type: {kernel_type}")
