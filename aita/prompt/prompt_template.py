from typing import Optional

from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from aita.prompt.base import BasePromptTemplate, BasicContextPromptTemplate


class AitaPromptTemplate:
    base_prompt_template: PromptTemplate
    context_prompt_template: list[PromptTemplate]
    output_prompt_template: Optional[PromptTemplate]
    prompt_templates: Optional[list[PromptTemplate]] = None

    def __init__(
        self,
        base_prompt_template: Optional[PromptTemplate] = None,
        context_prompt_template: Optional[list[PromptTemplate]] = None,
        output_prompt_template: Optional[PromptTemplate] = None,
    ):
        if base_prompt_template is None:
            self.base_prompt_template = BasePromptTemplate
        else:
            self.base_prompt_template = base_prompt_template
        if context_prompt_template is None:
            self.context_prompt_template = []
        else:
            self.context_prompt_template = context_prompt_template
        self.output_prompt_template = output_prompt_template

    def set_base_prompt(self, base_prompt_template: PromptTemplate):
        self.base_prompt_template = base_prompt_template
        self.prompt_templates = None  # Invalidate the current prompt templates
        return self

    def add_context_prompt(self, context_prompt_template: PromptTemplate):
        self.context_prompt_template.append(context_prompt_template)
        self.prompt_templates = None  # Invalidate the current prompt templates
        return self

    def build_prompt(self) -> list[PromptTemplate]:
        # Combine all prompt templates and return
        res = [self.base_prompt_template]
        if self.context_prompt_template:
            res.extend(self.context_prompt_template)
        if self.output_prompt_template:
            res.append(self.output_prompt_template)
        self.prompt_templates = res
        return res

    def get_prompt_templates(self):
        if self.prompt_templates is None:
            raise Exception("Prompt templates are not built yet. Please call build_prompt first.")
        return self.prompt_templates


# Example usage:
aita_prompt = AitaPromptTemplate()

# Ensure build_prompt is called before accessing the templates
aita_prompt.build_prompt()
print(aita_prompt.get_prompt_templates())
