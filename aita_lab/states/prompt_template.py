from typing import List, Optional

import json
import os

import reflex as rx
from sqlmodel import select, Field

from aita.prompt.prompt_builder import prompt_factory

path = os.path.dirname(__file__)
f = open(f"{path}/formatted_prompt_examples.json")
data = json.load(f)


class PromptTemplate(rx.Model, table=True):
    prompt_repr: str
    k_shot: int
    example_format: str
    selector_type: str
    prompt_template_name: str
    prompt_lines: str
    prompt_template_type: Optional[str] = Field(default="custom")


class PromptTemplateState(rx.State):
    question: str
    prompt_templates: List[PromptTemplate] = []

    prompt_repr: str = ""
    k_shot: Optional[int] = 0
    example_format: str = ""
    selector_type: str = ""
    prompt_template_name: str = ""
    prompt_template_lines: str = ""
    create_prompt_template_dialog_open: bool = False

    @rx.var
    def get_language_extensions(self) -> List[str]:
        return ["loadLanguage('sql')"]

    def copy_to_current_prompt_template(self, prompt_template_name: str):
        pt = self.get_prompt_template(prompt_template_name)
        self.prompt_repr = pt.prompt_repr
        self.k_shot = pt.k_shot
        self.example_format = pt.example_format
        self.selector_type = pt.selector_type
        self.prompt_template_name = pt.prompt_template_name
        self.prompt_template_lines = pt.prompt_lines

    def toggle_create_prompt_template_dialog(self):
        self.create_prompt_template_dialog_open = not self.create_prompt_template_dialog_open

    @rx.var
    def prompt_template_names(self) -> List[str]:
        return [pt.prompt_template_name for pt in self.prompt_templates]

    @staticmethod
    def load_builtin_prompt_templates():
        question = data["question"]
        prompt_templates = []
        for template in data["templates"]:
            prompt_repr = template["args"]["prompt_repr"]
            k_shot = template["args"]["k_shot"]
            example_format = template["args"]["example_type"]
            selector_type = template["args"]["selector_type"]
            prompt_template_name = f"{prompt_repr}_{k_shot}-SHOT_{selector_type}_{example_format}"
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
        return question, prompt_templates

    def load_prompt_templates(self):
        self.question, self.prompt_templates = self.load_builtin_prompt_templates()
        with rx.session() as session:
            custom_prompt_templates = session.exec(select(PromptTemplate)).all()
            if custom_prompt_templates:
                self.prompt_templates.extend(custom_prompt_templates)
        return self.prompt_templates

    @staticmethod
    def get_prompt_template(prompt_template_name: str) -> Optional[PromptTemplate]:
        _, prompt_templates = PromptTemplateState.load_builtin_prompt_templates()
        return next(
            (pt for pt in prompt_templates if pt.prompt_template_name == prompt_template_name), None
        )

    @staticmethod
    def build_prompt(prompt_template: PromptTemplate, embedding_model: str, target):
        prompt = prompt_factory(
            repr_type=prompt_template.prompt_repr,
            k_shot=0,
            example_format=prompt_template.example_format,
            selector_type=prompt_template.selector_type,
        )(tokenizer=embedding_model)
        target_prompt = prompt.format(target, 2048, 200, 100, cross_domain=False)
        return target_prompt["prompt"]

    def create_prompt_template(self):
        with rx.session() as session:
            prompt_template = PromptTemplate(
                prompt_repr=self.prompt_repr,
                k_shot=self.k_shot,
                example_format=self.example_format,
                selector_type=self.selector_type,
                prompt_template_name=self.prompt_template_name,
                prompt_lines=self.prompt_template_lines,
                prompt_template_type="custom",
            )
            session.add(prompt_template)
            session.commit()

        self.load_prompt_templates()
        self.create_prompt_template_dialog_open = not self.create_prompt_template_dialog_open
        return

    def on_load(self):
        self.load_prompt_templates()
