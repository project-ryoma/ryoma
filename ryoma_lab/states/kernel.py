import json

import pandas as pd
import reflex as rx
from sqlmodel import select

from ryoma_lab.models.kernel import Kernel, ToolKernel
from ryoma_lab.models.tool import Tool, ToolOutput


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

    def on_load(self):
        self.load_kernels()
