import importlib
from typing import Optional

import reflex as rx

from aita.tool.factory import ToolFactory, get_supported_tools
from aita import tool


class Tool(rx.Model):
    id: Optional[str]
    name: str
    args: Optional[dict[str, str]] = {}
    description: Optional[str]


class ToolState(rx.State):
    tools: list[Tool]
    tool_names: list[str]

    def load_tools(self):
        self.tools = [Tool(
            name=tool.name,
            description=tool.value.__fields__["description"].default,
        ) for tool in get_supported_tools()]

    def on_load(self):
        self.load_tools()


class ToolOutput(rx.Base):
    pass
