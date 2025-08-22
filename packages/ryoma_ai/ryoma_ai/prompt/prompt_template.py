"""
Modern Prompt Template Factory

Simplified interface for building prompt templates with composition.
"""

from typing import List, Optional, Union

from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from ryoma_ai.prompt.base import BasePromptTemplate


class PromptTemplateFactory:
    """Factory for composing prompt templates from multiple parts."""

    def __init__(
        self,
        base_template: Optional[ChatPromptTemplate] = None,
        context_templates: Optional[List[ChatPromptTemplate]] = None,
        output_template: Optional[ChatPromptTemplate] = None,
    ):
        """
        Initialize with optional template components.

        Args:
            base_template: Base system prompt template
            context_templates: Additional context templates
            output_template: Output formatting template
        """
        self.templates: List[ChatPromptTemplate] = []

        # Add base template
        if base_template is None:
            self.templates = [BasePromptTemplate]
        else:
            self.templates = [base_template]

        # Add context templates
        if context_templates:
            self.templates.extend(context_templates)

        # Add output template
        if output_template:
            self.templates.append(output_template)

    def set_base_template(self, template: Union[str, ChatPromptTemplate]) -> None:
        """Set the base system template."""
        if isinstance(template, str):
            template = ChatPromptTemplate.from_messages(
                [SystemMessagePromptTemplate.from_template(template)]
            )
        self.templates[0] = template

    def add_context_template(self, template: Union[str, ChatPromptTemplate]) -> None:
        """Add a context template."""
        if isinstance(template, str):
            template = ChatPromptTemplate.from_messages(
                [SystemMessagePromptTemplate.from_template(template)]
            )
        self.templates.append(template)

    def add_human_template(self, template: Union[str, ChatPromptTemplate]) -> None:
        """Add a human message template."""
        if isinstance(template, str):
            template = ChatPromptTemplate.from_messages(
                [HumanMessagePromptTemplate.from_template(template)]
            )
        self.templates.append(template)

    def build(self) -> ChatPromptTemplate:
        """Build the final composed prompt template."""
        if not self.templates:
            return BasePromptTemplate

        # Flatten all message templates into a single template
        all_messages = []
        for template in self.templates:
            if hasattr(template, "messages"):
                all_messages.extend(template.messages)
            else:
                all_messages.append(template)

        return ChatPromptTemplate.from_messages(all_messages)

    # Alias for backward compatibility
    def build_prompt(self) -> ChatPromptTemplate:
        """Alias for build() method."""
        return self.build()
