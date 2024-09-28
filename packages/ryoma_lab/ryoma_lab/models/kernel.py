from typing import Optional

import reflex as rx
from pydantic import Field
from ryoma_lab.models.tool import Tool, ToolOutput


class Kernel(rx.Model, table=True):
    datasource: Optional[str] = Field(None, description="Name of the datasource")
    type: str
    tool: Optional[str] = Field(None, description="Name of the tool")
    output: Optional[str] = Field(None, description="Output of the tool")


class ToolKernel(rx.Base):
    tool: Tool
    output: ToolOutput
