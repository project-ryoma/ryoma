from typing import Optional

import reflex as rx
from sqlmodel import Field


class PromptTemplate(rx.Model, table=True):
    prompt_repr: str
    k_shot: int
    example_format: str
    selector_type: str
    prompt_template_name: str
    prompt_lines: str
    prompt_template_type: Optional[str] = Field(default="custom")
