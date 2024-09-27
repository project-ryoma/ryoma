from typing import Optional

import reflex as rx
from sqlmodel import Field


class PromptTemplate(rx.Model, table=True):
    prompt_repr: str = Field(
        ..., description="The prompt representation, e.g. SQL, TEXT, etc."
    )
    k_shot: int = Field(..., description="The number of examples to use in the prompt.")
    example_format: str
    selector_type: str = Field(
        ...,
        description="The type of selector to use for the prompt. e.g. COSSIMILAR, RANDOM, etc.",
    )
    prompt_template_name: str = Field(
        ..., description="The name of the prompt template."
    )
    prompt_lines: str = Field(..., description="The prompt template lines.")
    prompt_template_type: Optional[str] = Field(
        default="custom", description="The type of prompt template."
    )
