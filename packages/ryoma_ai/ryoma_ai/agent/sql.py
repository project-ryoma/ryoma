from typing import Dict, Optional, Union

from langchain_core.embeddings import Embeddings
from ryoma_ai.agent.workflow import WorkflowAgent
from ryoma_ai.agent.internals.enhanced_sql_agent import EnhancedSqlAgent
from ryoma_ai.agent.internals.reforce_sql_agent import ReFoRCESqlAgent
from ryoma_ai.datasource.base import DataSource
from ryoma_ai.tool.sql_tool import (
    CreateTableTool, QueryProfileTool, SqlQueryTool,
    SchemaAnalysisTool, QueryValidationTool, TableSelectionTool,
    QueryOptimizationTool, QueryExplanationTool
)
from ryoma_ai.vector_store.base import VectorStore


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
        use_enhanced_mode: bool = True,
        use_reforce_mode: bool = False,
        safety_config: Optional[Dict] = None,
        **kwargs,
    ):
        if use_reforce_mode:
            # Use the ReFoRCE SQL agent with state-of-the-art capabilities
            self._enhanced_agent = ReFoRCESqlAgent(
                model=model,
                model_parameters=model_parameters,
                datasource=datasource,
                safety_config=safety_config,
                **kwargs
            )
            # Initialize with enhanced tools
            tools = [
                SqlQueryTool(), CreateTableTool(), QueryProfileTool(),
                SchemaAnalysisTool(), QueryValidationTool(), TableSelectionTool(),
                QueryOptimizationTool(), QueryExplanationTool()
            ]
        elif use_enhanced_mode:
            # Use the enhanced SQL agent with advanced capabilities
            self._enhanced_agent = EnhancedSqlAgent(
                model=model,
                model_parameters=model_parameters,
                datasource=datasource,
                safety_config=safety_config,
                **kwargs
            )
            # Initialize with enhanced tools
            tools = [
                SqlQueryTool(), CreateTableTool(), QueryProfileTool(),
                SchemaAnalysisTool(), QueryValidationTool(), TableSelectionTool(),
                QueryOptimizationTool(), QueryExplanationTool()
            ]
        else:
            # Use basic tools for backward compatibility
            self._enhanced_agent = None
            tools = [SqlQueryTool(), CreateTableTool(), QueryProfileTool()]

        super().__init__(
            tools,
            model,
            model_parameters,
            datasource=datasource,
            embedding=embedding,
            vector_store=vector_store,
        )

        self.use_enhanced_mode = use_enhanced_mode
        self.use_reforce_mode = use_reforce_mode

    def invoke(self, input_data, **kwargs):
        """Override invoke to use enhanced agent when available."""
        if (self.use_reforce_mode or self.use_enhanced_mode) and self._enhanced_agent:
            return self._enhanced_agent.invoke(input_data, **kwargs)
        else:
            return super().invoke(input_data, **kwargs)

    def stream(self, input_data, **kwargs):
        """Override stream to use enhanced agent when available."""
        if (self.use_reforce_mode or self.use_enhanced_mode) and self._enhanced_agent:
            return self._enhanced_agent.stream(input_data, **kwargs)
        else:
            return super().stream(input_data, **kwargs)

    def enable_safety_rule(self, rule):
        """Enable a specific safety validation rule."""
        if self._enhanced_agent and hasattr(self._enhanced_agent, 'safety_validator'):
            self._enhanced_agent.safety_validator.enable_rule(rule)

    def disable_safety_rule(self, rule):
        """Disable a specific safety validation rule."""
        if self._enhanced_agent and hasattr(self._enhanced_agent, 'safety_validator'):
            self._enhanced_agent.safety_validator.disable_rule(rule)

    def set_safety_config(self, config: Dict):
        """Update safety configuration."""
        if self._enhanced_agent and hasattr(self._enhanced_agent, 'safety_validator'):
            self._enhanced_agent.safety_validator.set_safety_config(config)

    def analyze_schema(self, question: str):
        """Analyze schema relationships for a question."""
        if self._enhanced_agent and hasattr(self._enhanced_agent, 'schema_agent'):
            return self._enhanced_agent.schema_agent.analyze_schema_relationships(question)
        else:
            raise NotImplementedError("Schema analysis requires enhanced mode")

    def create_query_plan(self, question: str, context: Optional[Dict] = None):
        """Create a query execution plan."""
        if self._enhanced_agent and hasattr(self._enhanced_agent, 'query_planner'):
            return self._enhanced_agent.query_planner.create_query_plan(question, context)
        else:
            raise NotImplementedError("Query planning requires enhanced mode")
