from typing import Optional, Union

from langchain_core.prompts import ChatPromptTemplate, FewShotPromptTemplate, PromptTemplate

from aita.prompt.base import BasePromptTemplate, BasicContextPromptTemplate


class PromptTemplateFactory:
    base_prompt_template: ChatPromptTemplate
    context_prompt_templates: list[ChatPromptTemplate]
    output_prompt_template: Optional[PromptTemplate]

    def __init__(
        self,
        base_prompt_template: Optional[ChatPromptTemplate] = None,
        context_prompt_templates: Optional[list[ChatPromptTemplate]] = None,
        output_prompt_template: Optional[PromptTemplate] = None,
    ):
        if base_prompt_template is None:
            self.base_prompt_template = BasePromptTemplate
        else:
            self.base_prompt_template = base_prompt_template
        if context_prompt_templates is None:
            self.context_prompt_templates = []
        else:
            self.context_prompt_templates = context_prompt_templates
        self.output_prompt_template = output_prompt_template

    def set_base_prompt(self, base_prompt_template: Union[str, ChatPromptTemplate]):
        if isinstance(base_prompt_template, str):
            self.base_prompt_template = ChatPromptTemplate.from_messages(
                [("system", base_prompt_template)]
            )
        else:
            self.base_prompt_template = base_prompt_template

    def add_context_prompt(self, context_prompt_template: Union[str, ChatPromptTemplate]):
        if isinstance(context_prompt_template, str):
            context_prompt_template = ChatPromptTemplate.from_messages(
                [("system", context_prompt_template)]
            )
        self.context_prompt_templates.append(context_prompt_template)

    def build_prompt(self) -> ChatPromptTemplate:
        # Combine all prompt templates and return
        res = [self.base_prompt_template]
        if self.context_prompt_templates:
            res.extend(self.context_prompt_templates)
        if self.output_prompt_template:
            res.append(self.output_prompt_template)
        return ChatPromptTemplate.from_messages(res)
