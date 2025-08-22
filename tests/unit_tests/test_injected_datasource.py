#!/usr/bin/env python3
"""
Simplified tests for LangGraph injected store functionality.
"""

from unittest.mock import Mock

import pytest
from ryoma_ai.agent.sql import SqlAgent
from ryoma_ai.agent.workflow import WorkflowAgent
from ryoma_ai.datasource.sql import SqlDataSource
from ryoma_ai.models.agent import SqlAgentMode
from ryoma_ai.tool.sql_tool import SchemaAnalysisTool, SqlQueryTool


class TestInjectedDatasource:
    """Test cases for LangGraph injected datasource functionality."""

    @pytest.fixture
    def mock_datasource(self):
        """Create a mock datasource for testing."""
        mock_datasource = Mock(spec=SqlDataSource)
        mock_datasource.query.return_value = "Mock query result"
        mock_datasource.get_catalog.return_value = Mock()
        return mock_datasource

    @pytest.fixture
    def sql_tools(self):
        """Create SQL tools that expect injected datasource."""
        return [SqlQueryTool(), SchemaAnalysisTool()]

    @pytest.fixture
    def workflow_agent(self, mock_datasource, sql_tools):
        """Create a WorkflowAgent with mock datasource and SQL tools."""
        return WorkflowAgent(
            tools=sql_tools, model="gpt-3.5-turbo", datasource=mock_datasource
        )

    def test_agent_has_datasource(self, workflow_agent, mock_datasource):
        """Test that the agent properly stores the datasource."""
        assert workflow_agent.get_datasource() is mock_datasource

    def test_workflow_creation(self, workflow_agent):
        """Test that workflow can be created successfully."""
        workflow = workflow_agent.workflow
        assert workflow is not None

    def test_store_configuration(self, workflow_agent, mock_datasource):
        """Test that store is configured correctly in agent config."""
        # The store is accessible through the workflow agent's store attribute
        assert workflow_agent.store is not None
        # Check that datasource is in the store
        datasource_result = workflow_agent.store.get(("datasource",), "main")
        assert datasource_result is not None
        assert datasource_result.value is mock_datasource

    def test_sql_tools_store_annotation(self):
        """Test that SQL tools have correct store annotation."""
        sql_query_tool = SqlQueryTool()
        schema_analysis_tool = SchemaAnalysisTool()

        # Verify that the args_schema includes store field
        query_schema = sql_query_tool.args_schema
        analysis_schema = schema_analysis_tool.args_schema

        assert "store" in query_schema.model_fields
        assert "store" in analysis_schema.model_fields

    def test_message_state_structure(self):
        """Test that MessageState has correct structure for InjectedStore."""
        from ryoma_ai.states import MessageState

        assert hasattr(MessageState, "__annotations__")
        assert "messages" in MessageState.__annotations__
        # datasource should not be in state since we use InjectedStore
        assert "datasource" not in MessageState.__annotations__

    def test_sql_agent_modes(self, mock_datasource):
        """Test SqlAgent mode selection."""
        # Test basic mode (default)
        basic_agent = SqlAgent(model="gpt-3.5-turbo", datasource=mock_datasource)
        assert basic_agent.mode == SqlAgentMode.basic
        assert len(basic_agent.tools) == 3

        # Test enhanced mode
        enhanced_agent = SqlAgent(
            model="gpt-3.5-turbo",
            datasource=mock_datasource,
            mode=SqlAgentMode.enhanced,
        )
        assert enhanced_agent.mode == SqlAgentMode.enhanced
        assert len(enhanced_agent.tools) == 7

    def test_format_messages_structure(self, workflow_agent):
        """Test _format_messages returns correct structure."""
        formatted_state = workflow_agent._format_messages("Test question")

        assert isinstance(formatted_state, dict)
        assert "messages" in formatted_state
        # datasource should not be in formatted state
        assert "datasource" not in formatted_state
