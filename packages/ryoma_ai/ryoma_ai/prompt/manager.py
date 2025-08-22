"""
Prompt Manager - High-level interface for prompt generation

This module provides a clean, simple interface for creating prompts,
replacing the complex factory pattern with an intuitive manager.
"""

from typing import Any, Dict, List, Optional
from langchain_core.prompts import ChatPromptTemplate

from ryoma_ai.prompt.core import (
    ExampleFormat, PromptConfig, PromptTemplate, PromptType, 
    SelectorStrategy, prompt_registry
)


class PromptManager:
    """High-level manager for prompt generation and management."""
    
    def __init__(self):
        # Import builders to ensure registration
        from ryoma_ai.prompt import builders  # This triggers registration
        # Reference to avoid unused import warning
        _ = builders
    
    def create_prompt(
        self,
        prompt_type: PromptType,
        context: Dict[str, Any],
        examples: Optional[List[Dict[str, Any]]] = None,
        num_examples: int = 0,
        example_format: ExampleFormat = ExampleFormat.QUESTION_ANSWER,
        selector_strategy: SelectorStrategy = SelectorStrategy.RANDOM,
        **kwargs
    ) -> ChatPromptTemplate:
        """
        Create a prompt template with the specified configuration.
        
        Args:
            prompt_type: Type of prompt to create
            context: Context data for the prompt
            examples: Available examples for few-shot prompts
            num_examples: Number of examples to include
            example_format: How to format examples
            selector_strategy: How to select examples
            **kwargs: Additional configuration parameters
            
        Returns:
            ChatPromptTemplate ready for use
            
        Raises:
            ValueError: If prompt type is not supported
        """
        # Get the appropriate builder
        builder = prompt_registry.get_builder(prompt_type)
        if not builder:
            raise ValueError(f"No builder registered for prompt type: {prompt_type}")
        
        # Create configuration
        config = PromptConfig(
            prompt_type=prompt_type,
            example_format=example_format if num_examples > 0 else None,
            selector_strategy=selector_strategy if num_examples > 0 else None,
            num_examples=num_examples,
            **kwargs
        )
        
        # Handle examples if provided
        final_context = context.copy()
        if examples and num_examples > 0:
            selected_examples = self._select_examples(
                context.get("query", ""),
                examples,
                num_examples,
                selector_strategy
            )
            
            formatted_examples = self._format_examples(
                selected_examples,
                example_format
            )
            
            final_context["examples"] = formatted_examples
        
        # Build the prompt
        return builder.build(config, final_context)
    
    def create_sql_prompt(
        self,
        schema: str,
        question: str,
        examples: Optional[List[Dict[str, Any]]] = None,
        num_examples: int = 0,
        **kwargs
    ) -> ChatPromptTemplate:
        """
        Convenience method for creating SQL generation prompts.
        
        Args:
            schema: Database schema description
            question: User's question
            examples: SQL examples
            num_examples: Number of examples to include
            **kwargs: Additional parameters
            
        Returns:
            ChatPromptTemplate for SQL generation
        """
        context = {
            "schema": schema,
            "question": question
        }
        
        return self.create_prompt(
            prompt_type=PromptType.SQL_GENERATION,
            context=context,
            examples=examples,
            num_examples=num_examples,
            example_format=ExampleFormat.SQL_ONLY,
            **kwargs
        )
    
    def create_chat_prompt(
        self,
        user_input: str,
        context: Optional[str] = None,
        **kwargs
    ) -> ChatPromptTemplate:
        """
        Convenience method for creating chat prompts.
        
        Args:
            user_input: User's message
            context: Additional context
            **kwargs: Additional parameters
            
        Returns:
            ChatPromptTemplate for chat
        """
        prompt_context = {
            "user_input": user_input,
            "context": context or ""
        }
        
        return self.create_prompt(
            prompt_type=PromptType.CHAT,
            context=prompt_context,
            **kwargs
        )
    
    def register_template(
        self,
        name: str,
        prompt_type: PromptType,
        template_string: str,
        description: str = "",
        tags: Optional[List[str]] = None
    ) -> None:
        """
        Register a custom prompt template.
        
        Args:
            name: Template name
            prompt_type: Type of prompt
            template_string: Template content
            description: Template description
            tags: Optional tags for categorization
        """
        template = ChatPromptTemplate.from_template(template_string)
        config = PromptConfig(prompt_type=prompt_type)
        
        prompt_template = PromptTemplate(
            name=name,
            template=template,
            config=config,
            description=description,
            tags=tags or []
        )
        
        prompt_registry.register_template(prompt_template)
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get a registered template by name."""
        return prompt_registry.get_template(name)
    
    def list_templates(self, tag: Optional[str] = None) -> List[str]:
        """List all available templates."""
        return prompt_registry.list_templates(tag=tag)
    
    def _select_examples(
        self,
        query: str,
        examples: List[Dict[str, Any]],
        num_examples: int,
        strategy: SelectorStrategy
    ) -> List[Dict[str, Any]]:
        """Select examples using the specified strategy."""
        selector = prompt_registry.get_selector(strategy)
        if not selector:
            # Fallback to first N examples
            return examples[:num_examples]
        
        return selector.select_examples(query, examples, num_examples)
    
    def _format_examples(
        self,
        examples: List[Dict[str, Any]],
        format_type: ExampleFormat
    ) -> str:
        """Format examples using the specified formatter."""
        formatter = prompt_registry.get_formatter(format_type)
        if not formatter:
            # Fallback to simple string representation
            return "\n".join(str(ex) for ex in examples)
        
        return formatter.format_examples(examples)


# Convenience instance for easy imports
prompt_manager = PromptManager()


# Backward compatibility function to replace the old prompt_factory
def create_prompt(
    prompt_type: str,
    schema: Optional[str] = None,
    question: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    examples: Optional[List[Dict[str, Any]]] = None,
    num_examples: int = 0,
    example_format: str = "qa",
    selector_strategy: str = "random",
    **kwargs
) -> ChatPromptTemplate:
    """
    Backward-compatible function to replace the old prompt_factory.
    
    This provides a migration path from the old complex system.
    """
    # Map old string types to new enums
    type_mapping = {
        "SQL": PromptType.SQL_GENERATION,
        "TEXT": PromptType.CHAT,
        "INSTRUCTION": PromptType.INSTRUCTION_FOLLOWING,
        "CHAT": PromptType.CHAT,
        "COT": PromptType.CHAIN_OF_THOUGHT
    }
    
    format_mapping = {
        "qa": ExampleFormat.QUESTION_ANSWER,
        "sql_only": ExampleFormat.SQL_ONLY,
        "complete": ExampleFormat.COMPLETE_CONTEXT,
        "numbered": ExampleFormat.NUMBERED
    }
    
    strategy_mapping = {
        "random": SelectorStrategy.RANDOM,
        "similarity": SelectorStrategy.SIMILARITY,
        "cosine": SelectorStrategy.COSINE
    }
    
    # Convert to new types
    new_prompt_type = type_mapping.get(prompt_type.upper(), PromptType.CHAT)
    new_format = format_mapping.get(example_format.lower(), ExampleFormat.QUESTION_ANSWER)
    new_strategy = strategy_mapping.get(selector_strategy.lower(), SelectorStrategy.RANDOM)
    
    # Build context
    prompt_context = context or {}
    if schema:
        prompt_context["schema"] = schema
    if question:
        prompt_context["question"] = question
    
    return prompt_manager.create_prompt(
        prompt_type=new_prompt_type,
        context=prompt_context,
        examples=examples,
        num_examples=num_examples,
        example_format=new_format,
        selector_strategy=new_strategy,
        **kwargs
    )