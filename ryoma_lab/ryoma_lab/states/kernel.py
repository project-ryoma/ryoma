import asyncio
import json
from typing import Any, Dict

import pandas as pd
import reflex as rx
from sqlmodel import select

from ryoma_lab.models.kernel import Kernel, ToolKernel
from ryoma_lab.models.tool import Tool, ToolOutput
from ryoma_lab.states.base import BaseState


class KernelState(BaseState):
    kernels: list[Kernel] = []

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
