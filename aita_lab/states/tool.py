from typing import Optional

import inspect

import reflex as rx
from pydantic import BaseModel

from aita import tool


def get_tool_classes() -> list:
    res = inspect.getmembers(tool, inspect.isclass)
    return res


def get_model_fields(model: BaseModel, field_name: str) -> BaseModel:
    return model.__fields__[field_name].default


def get_model_fields_as_dict(model: BaseModel) -> dict:
    d = {}
    for field, value in model.__fields__.items():
        d[field] = {
            "name": field,
            "required": value.required,
            "description": value.field_info.description,
        }
    return d


class Tool(rx.Model):
    id: Optional[str]
    name: str
    args: Optional[dict[str, str]] = {}
    description: Optional[str]


class ToolState(rx.State):
    tools: list[Tool]
    tool_names: list[str]

    def load_tools(self):
        self.tools = []
        for tool in get_tool_classes():
            description = get_model_fields(tool[1], "description")
            args = get_model_fields_as_dict(get_model_fields(tool[1], "args_schema"))
            tool = Tool(
                name=tool[0],
                description=description,
            )
            self.tools.append(tool)
        self.tool_names = [tool.name for tool in self.tools]

    def on_load(self):
        self.load_tools()


class ToolOutput(rx.Base):
    pass
