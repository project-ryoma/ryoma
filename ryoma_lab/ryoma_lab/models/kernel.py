import reflex as rx
from ryoma_lab.models.tool import Tool, ToolOutput


class Kernel(rx.Model, table=True):
    tool: str = None
    output: str = None


class ToolKernel(rx.Base):
    tool: Tool
    output: ToolOutput
