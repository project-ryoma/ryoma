"""
Ryoma AI Prompt System

A modern, modular prompt management system for AI applications.

Key Components:
- PromptManager: High-level interface for prompt creation
- PromptType, ExampleFormat, SelectorStrategy: Configuration enums
- prompt_registry: Global registry for custom components

Basic Usage:
    from ryoma_ai.prompt import prompt_manager, PromptType
    
    # Create a SQL prompt
    prompt = prompt_manager.create_sql_prompt(
        schema="CREATE TABLE users (id INT, name VARCHAR(100))",
        question="What are all the user names?"
    )
    
    # Create a chat prompt
    prompt = prompt_manager.create_chat_prompt(
        user_input="Hello, how can you help me?",
        context="You are a data analyst assistant"
    )

Advanced Usage:
    # Register custom templates
    prompt_manager.register_template(
        name="analysis_template",
        prompt_type=PromptType.INSTRUCTION_FOLLOWING,
        template_string="Analyze this data: {data}",
        description="Template for data analysis tasks"
    )
"""

# Core components
from ryoma_ai.prompt.core import (
    ExampleFormat,
    PromptConfig,
    PromptTemplate,
    PromptType,
    SelectorStrategy,
    prompt_registry,
)

# Main interface
from ryoma_ai.prompt.manager import prompt_manager

# Base classes for extensions
from ryoma_ai.prompt.core import (
    ExampleFormatter,
    ExampleSelector,
    PromptBuilder,
)

# Backward compatibility
from ryoma_ai.prompt.base import BasePromptTemplate, BasicContextPromptTemplate

__all__ = [
    # Main interface
    "prompt_manager",
    
    # Configuration enums
    "PromptType",
    "ExampleFormat", 
    "SelectorStrategy",
    
    # Core classes
    "PromptConfig",
    "PromptTemplate",
    "prompt_registry",
    
    # Extension points
    "PromptBuilder",
    "ExampleSelector",
    "ExampleFormatter",
    
    # Backward compatibility
    "BasePromptTemplate",
    "BasicContextPromptTemplate",
]