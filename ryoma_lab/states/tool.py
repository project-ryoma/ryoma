from typing import Optional

import pandas as pd
import reflex as rx

from ryoma import tool
from ryoma_lab.states.utils import get_model_classes, get_model_fields, get_model_fields_as_dict


class ToolArg(rx.Base):
    name: str
    required: Optional[bool]
    description: Optional[str]
    value: Optional[str] = ""


class Tool(rx.Base):
    id: Optional[str]
    name: str
    args: list[ToolArg] = []
    description: Optional[str]


class ToolOutput(rx.Base):
    data: pd.DataFrame
    show: bool = False


class ToolState(rx.State):
    tools: list[Tool]

    @rx.var
    def tool_names(self) -> list[str]:
        return [t.name for t in self.tools]

    def load_tools(self):
        self.tools = []
        for t in get_model_classes(tool):
            name, cls = t
            description = get_model_fields(cls, "description")
            args_schema = get_model_fields(cls, "args_schema")
            args = get_model_fields_as_dict(args_schema)
            self.tools.append(
                Tool(
                    name=name,
                    description=description,
                    args=[
                        ToolArg(
                            name=arg["name"],
                            required=arg["required"],
                            description=arg["description"],
                        )
                        for arg in args.values()
                    ],
                )
            )

    def on_load(self):
        self.load_tools()
