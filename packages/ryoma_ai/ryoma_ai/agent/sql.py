import logging
from typing import Dict, Optional, Union

from langchain_core.embeddings import Embeddings
from langgraph.graph import StateGraph
from langgraph.graph.graph import CompiledGraph
from ryoma_ai.agent.internals.enhanced_sql_agent import (
    EnhancedSqlAgent as InternalEnhancedSqlAgent,
)
from ryoma_ai.agent.internals.reforce_sql_agent import (
    ReFoRCESqlAgent as InternalReFoRCESqlAgent,
)
from ryoma_ai.agent.workflow import WorkflowAgent
from ryoma_data.base import DataSource
from ryoma_ai.models.agent import SqlAgentMode
from ryoma_ai.tool.sql_tool import (
    CreateTableTool,
    QueryExplanationTool,
    QueryOptimizationTool,
    QueryProfileTool,
    QueryValidationTool,
    SchemaAnalysisTool,
    SqlQueryTool,
)
from ryoma_ai.vector_store.base import VectorStore


class SqlAgent(WorkflowAgent):
    """
    A SQL agent that can use SQL Tools to interact with SQL schemas.
    Enhanced with multi-step reasoning, safety validation, and intelligent schema linking.

    This class uses a factory pattern internally to create the appropriate agent
    implementation based on the mode parameter.
    """

    description: str = (
        "A SQL agent that can use SQL Tools to interact with SQL schemas. "
        "Enhanced with multi-step reasoning, safety validation, and intelligent schema linking."
    )

    def __new__(
        cls,
        model: str,
        model_parameters: Optional[Dict] = None,
        datasource: Optional[DataSource] = None,
        embedding: Optional[Union[dict, Embeddings]] = None,
        vector_store: Optional[Union[dict, VectorStore]] = None,
        mode: Union[SqlAgentMode, str] = SqlAgentMode.basic,
        safety_config: Optional[Dict] = None,
        **kwargs,
    ):
        """
        Factory method that creates the appropriate SQL agent based on mode.

        Args:
            model: The language model to use
            model_parameters: Optional model parameters
            datasource: Optional datasource for SQL operations
            embedding: Optional embedding configuration
            vector_store: Optional vector store configuration
            mode: The SQL agent mode (basic, enhanced, reforce)
            safety_config: Optional safety configuration
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
                datasource=datasource,
                embedding=embedding,
                vector_store=vector_store,
                safety_config=safety_config,
                **kwargs,
            )
        elif mode == SqlAgentMode.enhanced:
            return EnhancedSqlAgentImpl(
                model=model,
                model_parameters=model_parameters,
                datasource=datasource,
                embedding=embedding,
                vector_store=vector_store,
                safety_config=safety_config,
                **kwargs,
            )
        else:  # basic mode
            return BasicSqlAgent(
                model=model,
                model_parameters=model_parameters,
                datasource=datasource,
                embedding=embedding,
                vector_store=vector_store,
                **kwargs,
            )


class BasicSqlAgent(WorkflowAgent):
    """Basic SQL agent with core functionality."""

    description: str = (
        "A basic SQL agent that provides core SQL query functionality "
        "with essential tools for database interaction."
    )

    def __init__(
        self,
        model: str,
        model_parameters: Optional[Dict] = None,
        datasource: Optional[DataSource] = None,
        embedding: Optional[Union[dict, Embeddings]] = None,
        vector_store: Optional[Union[dict, VectorStore]] = None,
        **kwargs,
    ):
        # Basic tools for core functionality
        tools = [SqlQueryTool(), CreateTableTool(), QueryProfileTool()]

        super().__init__(
            tools,
            model,
            model_parameters,
            datasource=datasource,
            embedding=embedding,
            vector_store=vector_store,
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
    """Enhanced SQL agent with advanced capabilities."""

    description: str = (
        "An enhanced SQL agent with advanced capabilities including "
        "safety validation, schema analysis, and query optimization."
    )

    def __init__(
        self,
        model: str,
        model_parameters: Optional[Dict] = None,
        datasource: Optional[DataSource] = None,
        embedding: Optional[Union[dict, Embeddings]] = None,
        vector_store: Optional[Union[dict, VectorStore]] = None,
        safety_config: Optional[Dict] = None,
        **kwargs,
    ):
        # Enhanced tools with all capabilities
        tools = [
            SqlQueryTool(),
            CreateTableTool(),
            QueryProfileTool(),
            SchemaAnalysisTool(),
            QueryValidationTool(),
            QueryOptimizationTool(),
            QueryExplanationTool(),
        ]

        super().__init__(
            tools,
            model,
            model_parameters,
            datasource=datasource,
            embedding=embedding,
            vector_store=vector_store,
            **kwargs,
        )

        self.mode = SqlAgentMode.enhanced

        # Initialize internal enhanced agent for advanced capabilities
        try:
            # Remove store from kwargs to avoid duplicate parameter
            internal_kwargs = {k: v for k, v in kwargs.items() if k != "store"}
            self._internal_agent = InternalEnhancedSqlAgent(
                model=model,
                model_parameters=model_parameters,
                datasource=datasource,
                safety_config=safety_config,
                store=self.store,  # Pass the store instance to share datasource
                **internal_kwargs,
            )
        except Exception as e:
            # Log the error for debugging but continue with basic functionality
            logging.warning(f"Failed to initialize internal enhanced agent: {e}")
            self._internal_agent = None

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
        model: str,
        model_parameters: Optional[Dict] = None,
        datasource: Optional[DataSource] = None,
        embedding: Optional[Union[dict, Embeddings]] = None,
        vector_store: Optional[Union[dict, VectorStore]] = None,
        safety_config: Optional[Dict] = None,
        **kwargs,
    ):
        # ReFoRCE tools with all capabilities
        tools = [
            SqlQueryTool(),
            CreateTableTool(),
            QueryProfileTool(),
            SchemaAnalysisTool(),
            QueryValidationTool(),
            QueryOptimizationTool(),
            QueryExplanationTool(),
        ]

        super().__init__(
            tools,
            model,
            model_parameters,
            datasource=datasource,
            embedding=embedding,
            vector_store=vector_store,
            **kwargs,
        )

        self.mode = SqlAgentMode.reforce

        # Initialize internal ReFoRCE agent for advanced capabilities
        try:
            # Remove store from kwargs to avoid duplicate parameter
            internal_kwargs = {k: v for k, v in kwargs.items() if k != "store"}
            self._internal_agent = InternalReFoRCESqlAgent(
                model=model,
                model_parameters=model_parameters,
                datasource=datasource,
                safety_config=safety_config,
                store=self.store,  # Pass the store instance to share datasource
                **internal_kwargs,
            )
        except Exception as e:
            # Log the error for debugging but continue with basic functionality
            logging.warning(f"Failed to initialize internal ReFoRCE agent: {e}")
            self._internal_agent = None

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
