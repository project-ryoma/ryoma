from typing import Dict, Optional, Union

from langchain_core.embeddings import Embeddings
from langgraph.graph import StateGraph
from langgraph.graph.graph import CompiledGraph

from ryoma_ai.agent.workflow import WorkflowAgent
from ryoma_ai.agent.internals.enhanced_sql_agent import EnhancedSqlAgent
from ryoma_ai.agent.internals.reforce_sql_agent import ReFoRCESqlAgent
from ryoma_ai.datasource.base import DataSource
from ryoma_ai.tool.sql_tool import (
    CreateTableTool, QueryProfileTool, SqlQueryTool,
    SchemaAnalysisTool, QueryValidationTool,
    QueryOptimizationTool, QueryExplanationTool
)
from ryoma_ai.vector_store.base import VectorStore
from ryoma_ai.models.agent import SqlAgentMode


class SqlAgent(WorkflowAgent):
    description: str = (
        "A SQL agent that can use SQL Tools to interact with SQL schemas. "
        "Enhanced with multi-step reasoning, safety validation, and intelligent schema linking."
    )

    def __init__(
        self,
        model: str,
        model_parameters: Optional[Dict] = None,
        datasource: Optional[DataSource] = None,
        embedding: Optional[Union[dict, Embeddings]] = None,
        vector_store: Optional[Union[dict, VectorStore]] = None,
        mode: Union[SqlAgentMode, str] = SqlAgentMode.basic,
        safety_config: Optional[Dict] = None,
        **kwargs,
    ):
        if mode == "reforce" or mode == SqlAgentMode.reforce:
            # Use the ReFoRCE SQL agent with state-of-the-art capabilities
            self._agent = ReFoRCESqlAgent(
                model=model,
                model_parameters=model_parameters,
                datasource=datasource,
                safety_config=safety_config,
                **kwargs
            )
            # Initialize with enhanced tools
            tools = [
                SqlQueryTool(), CreateTableTool(), QueryProfileTool(),
                SchemaAnalysisTool(), QueryValidationTool(),
                QueryOptimizationTool(), QueryExplanationTool()
            ]
        elif mode == "enhanced" or mode == SqlAgentMode.enhanced:
            # Use the enhanced SQL agent with advanced capabilities
            self._agent = EnhancedSqlAgent(
                model=model,
                model_parameters=model_parameters,
                datasource=datasource,
                safety_config=safety_config,
                **kwargs
            )
            # Initialize with enhanced tools
            tools = [
                SqlQueryTool(), CreateTableTool(), QueryProfileTool(),
                SchemaAnalysisTool(), QueryValidationTool(),
                QueryOptimizationTool(), QueryExplanationTool()
            ]
        else:
            # Use basic tools for backward compatibility
            self._agent = None
            tools = [SqlQueryTool(), CreateTableTool(), QueryProfileTool()]

        super().__init__(
            tools,
            model,
            model_parameters,
            datasource=datasource,
            embedding=embedding,
            vector_store=vector_store,
        )

        self.mode = mode

    def _build_workflow(self, graph: StateGraph) -> CompiledGraph:
        """Build the workflow graph for the SQL agent."""
        if self.mode == SqlAgentMode.reforce:
            return self._agent.build_workflow(graph)
        elif self.mode == SqlAgentMode.enhanced:
            return self._agent.build_workflow(graph)
        else:
            return super()._build_workflow(graph)


    def enable_safety_rule(self, rule):
        """Enable a specific safety validation rule."""
        if self._agent and hasattr(self._agent, 'safety_validator'):
            self._agent.safety_validator.enable_rule(rule)

    def disable_safety_rule(self, rule):
        """Disable a specific safety validation rule."""
        if self._agent and hasattr(self._agent, 'safety_validator'):
            self._agent.safety_validator.disable_rule(rule)

    def set_safety_config(self, config: Dict):
        """Update safety configuration."""
        if self._agent and hasattr(self._agent, 'safety_validator'):
            self._agent.safety_validator.set_safety_config(config)

    def analyze_schema(self, question: str):
        """Analyze schema relationships for a question."""
        if self._agent and hasattr(self._agent, 'schema_agent'):
            return self._agent.schema_agent.analyze_schema_relationships(question)
        else:
            raise NotImplementedError("Schema analysis requires enhanced mode")

    def create_query_plan(self, question: str, context: Optional[Dict] = None):
        """Create a query execution plan."""
        if self._agent and hasattr(self._agent, 'query_planner'):
            return self._agent.query_planner.create_query_plan(question, context)
        else:
            raise NotImplementedError("Query planning requires enhanced mode")
