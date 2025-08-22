"""
Modern Prompt System - Core Components

This module provides a clean, modular approach to prompt management with:
- Clear separation of concerns
- Registry-based pattern for extensibility  
- Type safety and modern Python practices
- Easy testing and maintenance
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol

from langchain_core.prompts import ChatPromptTemplate


class PromptType(Enum):
    """Standard prompt types for different use cases."""

    # Basic types
    SQL_GENERATION = "sql"
    TEXT_ANALYSIS = "text"
    CHAT = "chat"

    # Specialized types
    INSTRUCTION_FOLLOWING = "instruction"
    CHAIN_OF_THOUGHT = "cot"
    FEW_SHOT = "few_shot"
    ZERO_SHOT = "zero_shot"


class ExampleFormat(Enum):
    """How examples should be formatted in prompts."""

    QUESTION_ANSWER = "qa"
    SQL_ONLY = "sql_only"
    COMPLETE_CONTEXT = "complete"
    NUMBERED = "numbered"


class SelectorStrategy(Enum):
    """How to select examples for few-shot prompts."""

    RANDOM = "random"
    SIMILARITY = "similarity"
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"


@dataclass
class PromptConfig:
    """Configuration for prompt generation."""

    prompt_type: PromptType
    example_format: Optional[ExampleFormat] = None
    selector_strategy: Optional[SelectorStrategy] = None
    num_examples: int = 0
    max_tokens: int = 2048
    temperature: float = 0.0
    custom_params: Dict[str, Any] = field(default_factory=dict)


class PromptBuilder(Protocol):
    """Protocol for prompt builders."""

    def build(
        self, config: PromptConfig, context: Dict[str, Any]
    ) -> ChatPromptTemplate:
        """Build a prompt template with the given config and context."""
        ...


class ExampleSelector(ABC):
    """Abstract base class for example selection strategies."""

    @abstractmethod
    def select_examples(
        self, query: str, examples: List[Dict[str, Any]], num_examples: int
    ) -> List[Dict[str, Any]]:
        """Select the most relevant examples for the query."""
        pass


class ExampleFormatter(ABC):
    """Abstract base class for example formatting."""

    @abstractmethod
    def format_examples(self, examples: List[Dict[str, Any]]) -> str:
        """Format examples into a string for inclusion in prompts."""
        pass


@dataclass
class PromptTemplate:
    """A complete prompt template with metadata."""

    name: str
    template: ChatPromptTemplate
    config: PromptConfig
    description: str = ""
    tags: List[str] = field(default_factory=list)
    version: str = "1.0.0"


class PromptRegistry:
    """Registry for managing prompt templates and builders."""

    def __init__(self):
        self._builders: Dict[PromptType, PromptBuilder] = {}
        self._selectors: Dict[SelectorStrategy, ExampleSelector] = {}
        self._formatters: Dict[ExampleFormat, ExampleFormatter] = {}
        self._templates: Dict[str, PromptTemplate] = {}

    def register_builder(self, prompt_type: PromptType, builder: PromptBuilder) -> None:
        """Register a prompt builder for a specific type."""
        self._builders[prompt_type] = builder

    def register_selector(
        self, strategy: SelectorStrategy, selector: ExampleSelector
    ) -> None:
        """Register an example selector for a specific strategy."""
        self._selectors[strategy] = selector

    def register_formatter(
        self, format_type: ExampleFormat, formatter: ExampleFormatter
    ) -> None:
        """Register an example formatter for a specific format."""
        self._formatters[format_type] = formatter

    def register_template(self, template: PromptTemplate) -> None:
        """Register a named prompt template."""
        self._templates[template.name] = template

    def get_builder(self, prompt_type: PromptType) -> Optional[PromptBuilder]:
        """Get a prompt builder for the specified type."""
        return self._builders.get(prompt_type)

    def get_selector(self, strategy: SelectorStrategy) -> Optional[ExampleSelector]:
        """Get an example selector for the specified strategy."""
        return self._selectors.get(strategy)

    def get_formatter(self, format_type: ExampleFormat) -> Optional[ExampleFormatter]:
        """Get an example formatter for the specified format."""
        return self._formatters.get(format_type)

    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get a registered template by name."""
        return self._templates.get(name)

    def list_templates(self, tag: Optional[str] = None) -> List[str]:
        """List all registered template names, optionally filtered by tag."""
        if tag is None:
            return list(self._templates.keys())
        return [
            name for name, template in self._templates.items() if tag in template.tags
        ]


# Global registry instance
prompt_registry = PromptRegistry()
