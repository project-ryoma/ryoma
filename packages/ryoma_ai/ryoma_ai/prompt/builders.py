"""
Prompt Builders - Concrete implementations for different prompt types

This module contains specific builders for various prompt types,
replacing the complex factory pattern with clean, focused builders.
"""

import random
from typing import Any, Dict, List

from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from ryoma_ai.prompt.core import (
    ExampleFormat,
    ExampleFormatter,
    ExampleSelector,
    PromptConfig,
    PromptType,
    SelectorStrategy,
)


class SQLPromptBuilder:
    """Builder for SQL generation prompts."""

    def build(
        self, config: PromptConfig, context: Dict[str, Any]
    ) -> ChatPromptTemplate:
        """Build a SQL generation prompt."""

        system_prompt = """You are an expert SQL analyst. Generate accurate SQL queries based on the given database schema and user questions.

Database Schema:
{schema}

Guidelines:
- Write clean, efficient SQL
- Use proper JOIN syntax
- Handle NULL values appropriately
- Return only the SQL query without explanation unless requested"""

        if config.num_examples > 0:
            system_prompt += "\n\nExamples:\n{examples}"

        human_prompt = "Question: {question}\n\nSQL Query:"

        messages = [
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template(human_prompt),
        ]

        return ChatPromptTemplate.from_messages(messages)


class ChatPromptBuilder:
    """Builder for general chat prompts."""

    def build(
        self, config: PromptConfig, context: Dict[str, Any]
    ) -> ChatPromptTemplate:
        """Build a general chat prompt."""

        system_prompt = """You are a helpful AI assistant specializing in data analysis and engineering.
        
Context:
{context}

Respond helpfully and accurately to user questions."""

        human_prompt = "{user_input}"

        messages = [
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template(human_prompt),
        ]

        return ChatPromptTemplate.from_messages(messages)


class InstructionPromptBuilder:
    """Builder for instruction-following prompts."""

    def build(
        self, config: PromptConfig, context: Dict[str, Any]
    ) -> ChatPromptTemplate:
        """Build an instruction-following prompt."""

        system_prompt = """You are an AI assistant that follows instructions precisely.

Instructions:
{instructions}

Additional Context:
{context}"""

        if config.num_examples > 0:
            system_prompt += "\n\nExamples:\n{examples}"

        human_prompt = "{user_input}"

        messages = [
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template(human_prompt),
        ]

        return ChatPromptTemplate.from_messages(messages)


class ChainOfThoughtPromptBuilder:
    """Builder for chain-of-thought reasoning prompts."""

    def build(
        self, config: PromptConfig, context: Dict[str, Any]
    ) -> ChatPromptTemplate:
        """Build a chain-of-thought prompt."""

        system_prompt = """You are an AI assistant that thinks step by step to solve complex problems.

For each question:
1. Break down the problem
2. Think through each step
3. Show your reasoning 
4. Provide the final answer

Context:
{context}"""

        if config.num_examples > 0:
            system_prompt += "\n\nExamples of step-by-step reasoning:\n{examples}"

        human_prompt = "Question: {question}\n\nThink step by step:"

        messages = [
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template(human_prompt),
        ]

        return ChatPromptTemplate.from_messages(messages)


# Example Selectors
class RandomExampleSelector(ExampleSelector):
    """Randomly select examples."""

    def select_examples(
        self, query: str, examples: List[Dict[str, Any]], num_examples: int
    ) -> List[Dict[str, Any]]:
        """Randomly select examples."""
        if not examples or num_examples <= 0:
            return []

        return random.sample(examples, min(num_examples, len(examples)))


class SimilarityExampleSelector(ExampleSelector):
    """Select examples based on similarity (placeholder implementation)."""

    def select_examples(
        self, query: str, examples: List[Dict[str, Any]], num_examples: int
    ) -> List[Dict[str, Any]]:
        """Select examples based on similarity."""
        # For now, just return the first N examples
        # In a real implementation, this would use embeddings to find similar examples
        return examples[:num_examples]


# Example Formatters
class QuestionAnswerFormatter(ExampleFormatter):
    """Format examples as question-answer pairs."""

    def format_examples(self, examples: List[Dict[str, Any]]) -> str:
        """Format examples as Q&A pairs."""
        formatted = []
        for i, example in enumerate(examples, 1):
            q = example.get("question", "")
            a = example.get("answer", example.get("query", ""))
            formatted.append(f"Example {i}:\nQ: {q}\nA: {a}")

        return "\n\n".join(formatted)


class SQLOnlyFormatter(ExampleFormatter):
    """Format examples showing only SQL queries."""

    def format_examples(self, examples: List[Dict[str, Any]]) -> str:
        """Format examples as SQL queries only."""
        queries = []
        for i, example in enumerate(examples, 1):
            query = example.get("query", example.get("sql", ""))
            if query:
                queries.append(f"-- Example {i}\n{query}")

        return "\n\n".join(queries)


class CompleteContextFormatter(ExampleFormatter):
    """Format examples with complete context."""

    def format_examples(self, examples: List[Dict[str, Any]]) -> str:
        """Format examples with full context."""
        formatted = []
        for i, example in enumerate(examples, 1):
            parts = [f"Example {i}:"]

            if "question" in example:
                parts.append(f"Question: {example['question']}")
            if "context" in example:
                parts.append(f"Context: {example['context']}")
            if "query" in example:
                parts.append(f"SQL: {example['query']}")
            elif "answer" in example:
                parts.append(f"Answer: {example['answer']}")

            formatted.append("\n".join(parts))

        return "\n\n".join(formatted)


class NumberedFormatter(ExampleFormatter):
    """Format examples with simple numbering."""

    def format_examples(self, examples: List[Dict[str, Any]]) -> str:
        """Format examples with numbering."""
        formatted = []
        for i, example in enumerate(examples, 1):
            content = example.get("content", str(example))
            formatted.append(f"{i}. {content}")

        return "\n".join(formatted)


def register_default_components():
    """Register all default builders, selectors, and formatters."""
    from ryoma_ai.prompt.core import prompt_registry

    # Register builders
    prompt_registry.register_builder(PromptType.SQL_GENERATION, SQLPromptBuilder())
    prompt_registry.register_builder(PromptType.CHAT, ChatPromptBuilder())
    prompt_registry.register_builder(
        PromptType.INSTRUCTION_FOLLOWING, InstructionPromptBuilder()
    )
    prompt_registry.register_builder(
        PromptType.CHAIN_OF_THOUGHT, ChainOfThoughtPromptBuilder()
    )

    # Register selectors
    prompt_registry.register_selector(SelectorStrategy.RANDOM, RandomExampleSelector())
    prompt_registry.register_selector(
        SelectorStrategy.SIMILARITY, SimilarityExampleSelector()
    )
    prompt_registry.register_selector(
        SelectorStrategy.COSINE, SimilarityExampleSelector()
    )  # alias

    # Register formatters
    prompt_registry.register_formatter(
        ExampleFormat.QUESTION_ANSWER, QuestionAnswerFormatter()
    )
    prompt_registry.register_formatter(ExampleFormat.SQL_ONLY, SQLOnlyFormatter())
    prompt_registry.register_formatter(
        ExampleFormat.COMPLETE_CONTEXT, CompleteContextFormatter()
    )
    prompt_registry.register_formatter(ExampleFormat.NUMBERED, NumberedFormatter())


# Auto-register when module is imported
register_default_components()
