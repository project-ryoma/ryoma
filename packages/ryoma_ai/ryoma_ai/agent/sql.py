"""
SQL agent implementations for Ryoma AI.

This module provides SQL agents with varying levels of capabilities:
- BasicSqlAgent: Core SQL functionality
- EnhancedSqlAgent: Advanced features with safety and optimization
- ReFoRCESqlAgent: ReFlect-Force-Correct approach

The SqlAgent class provides a factory to create the appropriate agent type.
"""

import logging
from typing import Dict, Optional, Union

from langchain_core.language_models import BaseChatModel
from langgraph.graph import StateGraph
from langgraph.graph.graph import CompiledGraph

from ryoma_ai.agent.internals.enhanced_sql_agent import (
    EnhancedSqlAgent as InternalEnhancedSqlAgent,
)
from ryoma_ai.agent.internals.reforce_sql_agent import (
    ReFoRCESqlAgent as InternalReFoRCESqlAgent,
)
from ryoma_ai.agent.workflow import WorkflowAgent
from ryoma_ai.agent.sql_tools import (
    get_basic_sql_tools,
    get_enhanced_sql_tools,
    get_reforce_sql_tools,
)
from ryoma_ai.models.agent import SqlAgentMode


class SqlAgent(WorkflowAgent):
    """
    A SQL agent that can use SQL Tools to interact with SQL schemas.
    Enhanced with multi-step reasoning, safety validation, and intelligent schema linking.

    This class uses a factory pattern internally to create the appropriate agent
    implementation based on the mode parameter.

    **Note:** This factory is deprecated. Use AgentBuilder.build_sql_agent() instead
    for a simpler API.

    Example:
        >>> # Deprecated way (still works but not recommended)
        >>> agent = SqlAgent(model="gpt-4", mode="enhanced", store=store)
        >>>
        >>> # Recommended way
        >>> from ryoma_ai.services import AgentBuilder
        >>> agent = builder.build_sql_agent(model="gpt-4", mode="enhanced")
    """

    description: str = (
        "A SQL agent that can use SQL Tools to interact with SQL schemas. "
        "Enhanced with multi-step reasoning, safety validation, and intelligent schema linking."
    )

    def __new__(
        cls,
        model: Union[str, BaseChatModel],
        model_parameters: Optional[Dict] = None,
        mode: Union[SqlAgentMode, str] = SqlAgentMode.basic,
        safety_config: Optional[Dict] = None,
        store=None,
        **kwargs,
    ):
        """
        Factory method that creates the appropriate SQL agent based on mode.

        Args:
            model: The language model to use (string ID or instance)
            model_parameters: Optional model parameters
            mode: The SQL agent mode (basic, enhanced, reforce)
            safety_config: Optional safety configuration
            store: Optional BaseStore for InjectedStore pattern (datasource access)
            **kwargs: Additional arguments

        Returns:
            SqlAgent instance configured for the specified mode
        """
        # Normalize mode to enum if it's a string
        if isinstance(mode, str):
            mode = SqlAgentMode(mode)

        if mode == SqlAgentMode.reforce:
            return ReFoRCESqlAgentImpl(
                model=model,
                model_parameters=model_parameters,
                safety_config=safety_config,
                store=store,
                **kwargs,
            )
        elif mode == SqlAgentMode.enhanced:
            return EnhancedSqlAgentImpl(
                model=model,
                model_parameters=model_parameters,
                safety_config=safety_config,
                store=store,
                **kwargs,
            )
        else:  # basic mode
            return BasicSqlAgent(
                model=model,
                model_parameters=model_parameters,
                store=store,
                **kwargs,
            )


class BasicSqlAgent(WorkflowAgent):
    """
    Basic SQL agent with core functionality.

    Provides essential SQL capabilities including query execution,
    table creation, and query profiling.
    """

    description: str = (
        "A basic SQL agent that provides core SQL query functionality "
        "with essential tools for database interaction."
    )

    def __init__(
        self,
        model: Union[str, BaseChatModel],
        model_parameters: Optional[Dict] = None,
        store=None,
        **kwargs,
    ):
        """
        Initialize basic SQL agent.

        Args:
            model: Language model (string ID or instance)
            model_parameters: Optional model parameters
            store: Optional BaseStore for datasource access via InjectedStore
            **kwargs: Additional arguments
        """
        # Get basic SQL tools from centralized definition
        tools = get_basic_sql_tools()

        super().__init__(
            model=model,
            tools=tools,
            model_parameters=model_parameters,
            system_prompt="You are a SQL expert. Write SQL queries to answer questions.",
            store=store,
            **kwargs,
        )

        self.mode = SqlAgentMode.basic

    def enable_safety_rule(self, rule):
        """Basic mode doesn't support safety rules."""
        raise NotImplementedError("Safety rules require enhanced or reforce mode")

    def disable_safety_rule(self, rule):
        """Basic mode doesn't support safety rules."""
        raise NotImplementedError("Safety rules require enhanced or reforce mode")

    def set_safety_config(self, config: Dict):
        """Basic mode doesn't support safety configuration."""
        raise NotImplementedError(
            "Safety configuration requires enhanced or reforce mode"
        )

    def analyze_schema(self, question: str):
        """Basic mode doesn't support advanced schema analysis."""
        raise NotImplementedError("Schema analysis requires enhanced or reforce mode")

    def create_query_plan(self, question: str, context: Optional[Dict] = None):
        """Basic mode doesn't support query planning."""
        raise NotImplementedError("Query planning requires enhanced or reforce mode")


class EnhancedSqlAgentImpl(WorkflowAgent):
    """
    Enhanced SQL agent with advanced capabilities.

    Provides advanced features including safety validation,
    schema analysis, query optimization, and query explanation.
    """

    description: str = (
        "An enhanced SQL agent with advanced capabilities including "
        "safety validation, schema analysis, and query optimization."
    )

    def __init__(
        self,
        model: Union[str, BaseChatModel],
        model_parameters: Optional[Dict] = None,
        safety_config: Optional[Dict] = None,
        store=None,
        **kwargs,
    ):
        """
        Initialize enhanced SQL agent.

        Args:
            model: Language model (string ID or instance)
            model_parameters: Optional model parameters
            safety_config: Optional safety validation configuration
            store: Optional BaseStore for datasource access via InjectedStore
            **kwargs: Additional arguments
        """
        # Get enhanced SQL tools from centralized definition
        tools = get_enhanced_sql_tools()

        super().__init__(
            model=model,
            tools=tools,
            model_parameters=model_parameters,
            system_prompt=(
                "You are an advanced SQL expert. Use schema analysis and "
                "query planning for complex queries. Validate and optimize "
                "important queries."
            ),
            store=store,
            **kwargs,
        )

        self.mode = SqlAgentMode.enhanced
        self.safety_config = safety_config

        # Note: Internal agent initialization removed for now
        # Advanced features will be implemented differently in refactored version
        self._internal_agent = None
        logging.info("Enhanced SQL agent initialized with centralized tools")

    def _build_workflow(self, graph: StateGraph) -> CompiledGraph:
        """Build the workflow graph using enhanced capabilities."""
        if not self._internal_agent:
            raise RuntimeError("Internal enhanced agent failed to initialize properly")
        return self._internal_agent._build_workflow(graph)

    def enable_safety_rule(self, rule):
        """Enable a specific safety validation rule."""
        if self._internal_agent and hasattr(self._internal_agent, "safety_validator"):
            self._internal_agent.safety_validator.enable_rule(rule)

    def disable_safety_rule(self, rule):
        """Disable a specific safety validation rule."""
        if self._internal_agent and hasattr(self._internal_agent, "safety_validator"):
            self._internal_agent.safety_validator.disable_rule(rule)

    def set_safety_config(self, config: Dict):
        """Update safety configuration."""
        if self._internal_agent and hasattr(self._internal_agent, "safety_validator"):
            self._internal_agent.safety_validator.set_safety_config(config)

    def analyze_schema(self, question: str):
        """Analyze schema relationships for a question."""
        if self._internal_agent and hasattr(self._internal_agent, "schema_agent"):
            return self._internal_agent.schema_agent.analyze_schema_relationships(
                question
            )
        else:
            raise NotImplementedError(
                "Schema analysis not available in this enhanced agent"
            )

    def create_query_plan(self, question: str, context: Optional[Dict] = None):
        """Create a query execution plan."""
        if self._internal_agent and hasattr(self._internal_agent, "query_planner"):
            return self._internal_agent.query_planner.create_query_plan(
                question, context
            )
        else:
            raise NotImplementedError(
                "Query planning not available in this enhanced agent"
            )


class ReFoRCESqlAgentImpl(WorkflowAgent):
    """ReFoRCE SQL agent with state-of-the-art capabilities."""

    description: str = (
        "A ReFoRCE SQL agent with state-of-the-art capabilities including "
        "advanced reasoning, comprehensive safety validation, and intelligent query planning."
    )

    def __init__(
        self,
        model: Union[str, BaseChatModel],
        model_parameters: Optional[Dict] = None,
        safety_config: Optional[Dict] = None,
        store=None,
        **kwargs,
    ):
        """
        Initialize ReFoRCE SQL agent.

        Args:
            model: Language model (string ID or instance)
            model_parameters: Optional model parameters
            safety_config: Optional safety validation configuration
            store: Optional BaseStore for datasource access via InjectedStore
            **kwargs: Additional arguments
        """
        # Get ReFoRCE SQL tools from centralized definition
        tools = get_reforce_sql_tools()

        super().__init__(
            model=model,
            tools=tools,
            model_parameters=model_parameters,
            system_prompt=(
                "You are a SQL expert using the ReFoRCE (Reflect, Force, Correct) approach. "
                "For each query:\n"
                "1. Reflect: Think about what the query should do\n"
                "2. Force: Generate and execute the query\n"
                "3. Correct: If results don't match expectations, revise and retry\n"
                "Use all available tools to ensure query accuracy."
            ),
            store=store,
            **kwargs,
        )

        self.mode = SqlAgentMode.reforce
        self.safety_config = safety_config

        # Note: Internal agent initialization removed for now
        # Advanced features will be implemented differently in refactored version
        self._internal_agent = None
        logging.info("ReFoRCE SQL agent initialized with centralized tools")

    def _build_workflow(self, graph: StateGraph) -> CompiledGraph:
        """Build the workflow graph using ReFoRCE capabilities."""
        if not self._internal_agent:
            raise RuntimeError("Internal ReFoRCE agent failed to initialize properly")
        return self._internal_agent._build_workflow(graph)

    def enable_safety_rule(self, rule):
        """Enable a specific safety validation rule."""
        if self._internal_agent and hasattr(self._internal_agent, "safety_validator"):
            self._internal_agent.safety_validator.enable_rule(rule)

    def disable_safety_rule(self, rule):
        """Disable a specific safety validation rule."""
        if self._internal_agent and hasattr(self._internal_agent, "safety_validator"):
            self._internal_agent.safety_validator.disable_rule(rule)

    def set_safety_config(self, config: Dict):
        """Update safety configuration."""
        if self._internal_agent and hasattr(self._internal_agent, "safety_validator"):
            self._internal_agent.safety_validator.set_safety_config(config)

    def analyze_schema(self, question: str):
        """Analyze schema relationships for a question."""
        if self._internal_agent and hasattr(self._internal_agent, "schema_agent"):
            return self._internal_agent.schema_agent.analyze_schema_relationships(
                question
            )
        else:
            raise NotImplementedError(
                "Schema analysis not available in this ReFoRCE agent"
            )

    def create_query_plan(self, question: str, context: Optional[Dict] = None):
        """Create a query execution plan."""
        if self._internal_agent and hasattr(self._internal_agent, "query_planner"):
            return self._internal_agent.query_planner.create_query_plan(
                question, context
            )
        else:
            raise NotImplementedError(
                "Query planning not available in this ReFoRCE agent"
            )
