from typing import Optional

import reflex as rx

from aita.tool.factory import get_tool_classes


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
            name=tool[0],
            description=tool[1].__fields__["description"].default,
        ) for tool in get_tool_classes()]
        self.tool_names = [tool.name for tool in self.tools]

    def on_load(self):
        self.load_tools()


class ToolOutput(rx.Base):
    pass

