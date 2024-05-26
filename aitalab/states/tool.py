from typing import Optional

import reflex as rx


class Tool(rx.Model):
    id: Optional[str]
    name: str
    args: dict[str, str]
    desciption: Optional[str]


class ToolState(rx.State):
    tools: list[Tool]
    tool_names: list[str]
