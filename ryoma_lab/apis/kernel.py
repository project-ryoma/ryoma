from typing import List, Optional

import reflex as rx
from sqlmodel import delete, select, update

from ryoma_lab.models.kernel import Kernel
from ryoma_lab.models.tool import ToolOutput


class KernelAPI:
    @staticmethod
    def add_kernel_run(tool_id: str, tool_output: ToolOutput) -> bool:
        try:
            with rx.session() as session:
                kernel = Kernel(tool_id=tool_id, output=tool_output.json())
                session.add(kernel)
                session.commit()
                session.refresh(kernel)
            return True
        except Exception as e:
            print(f"Error adding kernel run: {e}")
            return False

    @staticmethod
    def get_kernel_run(kernel_id: int) -> Optional[Kernel]:
        try:
            with rx.session() as session:
                return session.get(Kernel, kernel_id)
        except Exception as e:
            print(f"Error getting kernel run: {e}")
            return None

    @staticmethod
    def get_kernel_runs_by_tool(tool_id: str) -> List[Kernel]:
        try:
            with rx.session() as session:
                return session.exec(
                    select(Kernel).where(Kernel.tool_id == tool_id)
                ).all()
        except Exception as e:
            print(f"Error getting kernel runs by tool: {e}")
            return []

    @staticmethod
    def update_kernel_run(kernel_id: int, tool_output: ToolOutput) -> bool:
        try:
            with rx.session() as session:
                stmt = (
                    update(Kernel)
                    .where(Kernel.id == kernel_id)
                    .values(output=tool_output.json())
                )
                session.exec(stmt)
                session.commit()
            return True
        except Exception as e:
            print(f"Error updating kernel run: {e}")
            return False

    @staticmethod
    def delete_kernel_run(kernel_id: int) -> bool:
        try:
            with rx.session() as session:
                kernel = session.get(Kernel, kernel_id)
                if kernel:
                    session.delete(kernel)
                    session.commit()
                    return True
                return False
        except Exception as e:
            print(f"Error deleting kernel run: {e}")
            return False

    @staticmethod
    def clear_kernels() -> bool:
        try:
            with rx.session() as session:
                session.exec(delete(Kernel))
                session.commit()
            return True
        except Exception as e:
            print(f"Error clearing kernels: {e}")
            return False

    @staticmethod
    def get_latest_kernel_run() -> Optional[Kernel]:
        try:
            with rx.session() as session:
                return session.exec(select(Kernel).order_by(Kernel.id.desc())).first()
        except Exception as e:
            print(f"Error getting latest kernel run: {e}")
            return None


kernel_api = KernelAPI()
