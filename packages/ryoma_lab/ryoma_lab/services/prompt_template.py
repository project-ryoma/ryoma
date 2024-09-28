import json
import os
from typing import Optional

import reflex as rx
from ryoma_lab.models.prompt import PromptTemplate
from sqlmodel import select

path = os.path.dirname(__file__)
f = open(f"{path}/formatted_prompt_examples.json")
data = json.load(f)


class PromptTemplateService:
    def __init__(self):
        self.session = rx.session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def load_prompt_templates(self) -> list[PromptTemplate]:
        prompt_templates = self.load_builtin_prompt_templates()
        custom_prompt_templates = self.session.exec(select(PromptTemplate)).all()
        if custom_prompt_templates:
            prompt_templates.extend(custom_prompt_templates)
        return prompt_templates

    @staticmethod
    def load_builtin_prompt_templates() -> list[PromptTemplate]:
        prompt_templates = []
        for template in data["templates"]:
            prompt_template_name = template["name"]
            prompt_repr = template["args"]["prompt_repr"]
            k_shot = template["args"]["k_shot"]
            example_format = template["args"]["example_format"]
            selector_type = template["args"]["selector_type"]
            prompt_lines = template["formatted_question"]["prompt"]
            prompt_template = PromptTemplate(
                prompt_repr=prompt_repr,
                k_shot=k_shot,
                example_format=example_format,
                selector_type=selector_type,
                prompt_template_name=prompt_template_name,
                prompt_lines=prompt_lines,
                prompt_template_type="builtin",
            )
            prompt_templates.append(prompt_template)
        return prompt_templates

    def save_prompt_template(
        self,
        prompt_repr: str,
        k_shot: int,
        example_format: str,
        selector_type: str,
        prompt_template_name: str,
        prompt_template_lines: str,
    ):
        prompt_template = PromptTemplate(
            prompt_repr=prompt_repr,
            k_shot=k_shot,
            example_format=example_format,
            selector_type=selector_type,
            prompt_template_name=prompt_template_name,
            prompt_lines=prompt_template_lines,
            prompt_template_type="custom",
        )
        self.session.add(prompt_template)
        self.session.commit()

    def get_prompt_template_by_name(
        self, prompt_template_name: str
    ) -> Optional[PromptTemplate]:
        prompt_templates = self.load_prompt_templates()
        return next(
            (
                pt
                for pt in prompt_templates
                if pt.prompt_template_name == prompt_template_name
            ),
            None,
        )
