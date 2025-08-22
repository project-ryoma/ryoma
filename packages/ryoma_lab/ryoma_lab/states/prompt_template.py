from typing import List, Optional

import reflex as rx
from ryoma_ai.prompt import PromptType, prompt_manager
from ryoma_lab.models.prompt import PromptTemplate
from ryoma_lab.services.prompt_template import PromptTemplateService
from ryoma_lab.states.ai import AIState

QUESTION = "What are the average and minimum price (in Euro) of all products?"


class PromptTemplateState(AIState):
    question: str = QUESTION
    prompt_templates: List[PromptTemplate] = []

    prompt_repr: str = ""
    k_shot: Optional[int] = 0
    example_format: str = ""
    selector_type: str = ""
    prompt_template_name: str = ""
    prompt_template_lines: str = ""
    create_prompt_template_dialog_open: bool = False

    @rx.var
    def get_language_extensions(self) -> str:
        return ""

    def copy_to_current_prompt_template(self, prompt_template_name: str):
        pt = next(
            (
                pt
                for pt in self.prompt_templates
                if pt.prompt_template_name == prompt_template_name
            ),
            None,
        )
        self.prompt_repr = pt.prompt_repr
        self.k_shot = pt.k_shot
        self.example_format = pt.example_format
        self.selector_type = pt.selector_type
        self.prompt_template_name = pt.prompt_template_name
        self.prompt_template_lines = pt.prompt_lines

    def toggle_create_prompt_template_dialog(self):
        self.create_prompt_template_dialog_open = (
            not self.create_prompt_template_dialog_open
        )

    @rx.var
    def prompt_template_names(self) -> List[str]:
        return [pt.prompt_template_name for pt in self.prompt_templates]

    def load_prompt_templates(self):
        with PromptTemplateService() as prompt_template_service:
            self.prompt_templates = prompt_template_service.load_prompt_templates()

    @staticmethod
    def build_prompt(prompt_template: PromptTemplate, embedding_model: str, target):
        """Build a prompt using the new prompt manager system."""

        # Map old prompt repr types to new PromptType
        type_mapping = {
            "SQL": PromptType.SQL_GENERATION,
            "TEXT": PromptType.CHAT,
            "INSTRUCTION": PromptType.INSTRUCTION_FOLLOWING,
            "COT": PromptType.CHAIN_OF_THOUGHT,
        }

        prompt_type = type_mapping.get(
            prompt_template.prompt_repr.upper(), PromptType.CHAT
        )

        # Create context from target
        context = {
            "schema": target.get("schema", ""),
            "question": target.get("question", ""),
            "user_input": target.get("user_input", target.get("question", "")),
            "context": target.get("context", ""),
        }

        # Build prompt template
        chat_prompt = prompt_manager.create_prompt(
            prompt_type=prompt_type,
            context=context,
            num_examples=0,  # k_shot is always 0 in the old code
        )

        # Format with target data and return as string
        try:
            formatted_messages = chat_prompt.format_messages(**target)
            # Convert messages to string format
            prompt_str = ""
            for message in formatted_messages:
                if hasattr(message, "content"):
                    prompt_str += message.content + "\n"
                else:
                    prompt_str += str(message) + "\n"
            return prompt_str.strip()
        except Exception:
            # Fallback to simple template
            return f"Context: {context.get('schema', '')}\n\nQuestion: {context.get('question', '')}\n\nAnswer:"

    def create_prompt_template(self):
        with PromptTemplateService() as prompt_template_service:
            prompt_template_service.save_prompt_template(
                prompt_repr=self.prompt_repr,
                k_shot=self.k_shot,
                example_format=self.example_format,
                selector_type=self.selector_type,
                prompt_template_name=self.prompt_template_name,
                prompt_template_lines=self.prompt_template_lines,
            )

        self.load_prompt_templates()
        self.create_prompt_template_dialog_open = (
            not self.create_prompt_template_dialog_open
        )
        return

    def on_load(self):
        self.load_prompt_templates()
