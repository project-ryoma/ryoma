from typing import Optional, Union

from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotPromptTemplate,
    PromptTemplate,
)
from ryoma_ai.prompt.base import BasePromptTemplate, BasicContextPromptTemplate


class PromptTemplateFactory:
    prompt_templates: list[ChatPromptTemplate]

    def __init__(
        self,
        base_prompt_template: Optional[ChatPromptTemplate] = None,
        context_prompt_templates: Optional[list[ChatPromptTemplate]] = None,
        output_prompt_template: Optional[ChatPromptTemplate] = None,
    ):
        if base_prompt_template is None:
            self.prompt_templates = [BasePromptTemplate]
        else:
            self.prompt_templates = [base_prompt_template]
        if context_prompt_templates:
            self.prompt_templates.extend(context_prompt_templates)
        if output_prompt_template:
            self.prompt_templates.append(output_prompt_template)

    def set_base_prompt(self, base_prompt_template: Union[str, ChatPromptTemplate]):
        if isinstance(base_prompt_template, str):
            base_prompt_template = ChatPromptTemplate.from_messages(
                [("system", base_prompt_template)]
            )
        self.prompt_templates[0] = base_prompt_template

    def add_context_prompt(
        self, context_prompt_template: Union[str, ChatPromptTemplate]
    ):
        if isinstance(context_prompt_template, str):
            context_prompt_template = ChatPromptTemplate.from_messages(
                [("system", context_prompt_template)]
            )
        self.prompt_templates.append(context_prompt_template)

    def build_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(self.prompt_templates)
