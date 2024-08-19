import json

import pandas as pd
import reflex as rx
from sqlmodel import delete, select

from aita_lab.states.tool import Tool, ToolOutput


class Kernel(rx.Model, table=True):
    tool: str = None
    output: str = None


class ToolKernel(rx.Base):
    tool: Tool
    output: ToolOutput


class KernelState(rx.State):
    kernels: list[Kernel] = []

    @rx.var
    def tool_kernels(self) -> list[ToolKernel]:
        tool_kernels = []
        for kernel in self.kernels:
            tool = Tool.parse_raw(kernel.tool)
            output = json.loads(kernel.output)
            df = pd.DataFrame(output["data"]["data"], columns=output["data"]["columns"])
            tool_kernels.append(
                ToolKernel(tool=tool, output=ToolOutput(data=df, show=output["show"]))
            )
        return tool_kernels

    @staticmethod
    def add_tool_run(tool: Tool, output: ToolOutput):
        with rx.session() as session:
            session.add(
                Kernel(
                    tool=tool.json(),
                    output=output.json(),
                )
            )
            session.commit()

    def load_kernels(self):
        with rx.session() as session:
            self.kernels = session.exec(select(Kernel)).all()

    def clear_kernels(self):
        with rx.session() as session:
            session.exec(delete(Kernel))
            session.commit()
        self.kernels = []
        self.load_kernel_history()

    def on_load(self):
        self.load_kernels()
