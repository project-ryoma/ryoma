from typing import Optional

import reflex as rx

from aita.tool.factory import ToolFactory, get_supported_tools


class Tool(rx.Model):
    id: Optional[str]
    name: str
    args: dict[str, str]
    desciption: Optional[str]


class ToolState(rx.State):
    tools: list[Tool]
    tool_names: list[str]

    def load_tools(self):
        tools, tool_names = [], []
        self.tools = tools
        self.tool_names = tool_names

    def on_load(self):
        self.load_tools()
