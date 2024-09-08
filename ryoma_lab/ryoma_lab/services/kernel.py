from typing import List, Optional

import reflex as rx
from sqlmodel import delete, select, update

from ryoma_lab.models.kernel import BaseKernel, Kernel
from ryoma_lab.models.pythonkernel import PythonKernel
from ryoma_lab.models.sqlkernel import SqlKernel
from ryoma_lab.models.tool import ToolOutput


class KernelService:
    def __init__(self):
        self.session = rx.session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def add_kernel_run(self, tool_id: str, tool_output: ToolOutput) -> bool:
        try:
            kernel = Kernel(tool_id=tool_id, output=tool_output.json())
            self.session.add(kernel)
            self.session.commit()
            self.session.refresh(kernel)
            return True
        except Exception as e:
            print(f"Error adding kernel run: {e}")
            return False

    def get_kernel_run(self, kernel_id: int) -> Optional[Kernel]:
        try:
            return self.session.get(Kernel, kernel_id)
        except Exception as e:
            print(f"Error getting kernel run: {e}")
            return None

    def get_kernel_runs_by_tool(self, tool_id: str) -> List[Kernel]:
        try:
            return self.session.exec(
                select(Kernel).where(Kernel.tool_id == tool_id)
            ).all()
        except Exception as e:
            print(f"Error getting kernel runs by tool: {e}")
            return []

    def update_kernel_run(self, kernel_id: int, tool_output: ToolOutput) -> bool:
        try:
            stmt = (
                update(Kernel)
                .where(Kernel.id == kernel_id)
                .values(output=tool_output.json())
            )
            self.session.exec(stmt)
            self.session.commit()
            return True
        except Exception as e:
            print(f"Error updating kernel run: {e}")
            return False

    def delete_kernel_run(self, kernel_id: int) -> bool:
        try:
            kernel = self.session.get(Kernel, kernel_id)
            if kernel:
                self.session.delete(kernel)
                self.session.commit()
                return True
            return False
        except Exception as e:
            print(f"Error deleting kernel run: {e}")
            return False

    def clear_kernels(self) -> bool:
        try:
            self.session.exec(delete(Kernel))
            self.session.commit()
            return True
        except Exception as e:
            print(f"Error clearing kernels: {e}")
            return False

    def get_latest_kernel_run(self) -> Optional[Kernel]:
        try:
            return self.session.exec(select(Kernel).order_by(Kernel.id.desc())).first()
        except Exception as e:
            print(f"Error getting latest kernel run: {e}")
            return None


class KernelFactory:
    @staticmethod
    def create_kernel(kernel_type: str) -> BaseKernel:
        if kernel_type == "python":
            return PythonKernel()
        elif kernel_type == "sql":
            return SqlKernel()
        else:
            raise ValueError(f"Unsupported kernel type: {kernel_type}")
