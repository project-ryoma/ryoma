from typing import Optional

import pandas as pd
import reflex as rx


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
