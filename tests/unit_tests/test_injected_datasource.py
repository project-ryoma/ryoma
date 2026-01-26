#!/usr/bin/env python3
"""
Simplified tests for LangGraph injected store functionality.
"""

from unittest.mock import Mock

import pytest
from langchain_core.stores import InMemoryStore
from ryoma_ai.agent.sql import SqlAgent
from ryoma_ai.agent.workflow import WorkflowAgent
from ryoma_ai.domain.constants import StoreKeys
from ryoma_ai.models.agent import SqlAgentMode
from ryoma_ai.tool.sql_tool import SchemaAnalysisTool, SqlQueryTool
from ryoma_data.sql import SqlDataSource


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
    def mock_store(self, mock_datasource):
        """Create a store with mock datasource."""
        store = InMemoryStore()
        store.mset([(StoreKeys.ACTIVE_DATASOURCE, mock_datasource)])
        return store

    @pytest.fixture
    def sql_tools(self):
        """Create SQL tools that expect injected datasource."""
        return [SqlQueryTool(), SchemaAnalysisTool()]

    @pytest.fixture
    def workflow_agent(self, mock_store, sql_tools):
        """Create a WorkflowAgent with mock datasource and SQL tools."""
        return WorkflowAgent(model="gpt-3.5-turbo", tools=sql_tools, store=mock_store)

    def test_agent_has_store(self, workflow_agent, mock_store):
        """Test that the agent properly has access to the store."""
        assert workflow_agent.store is mock_store

    def test_workflow_creation(self, workflow_agent):
        """Test that workflow can be created successfully."""
        workflow = workflow_agent.workflow
        assert workflow is not None

    def test_store_configuration(self, workflow_agent, mock_datasource):
        """Test that store is configured correctly in agent config."""
        # The store is accessible through the workflow agent's store attribute
        assert workflow_agent.store is not None
        # Check that datasource is in the store
        datasource_result = workflow_agent.store.mget([StoreKeys.ACTIVE_DATASOURCE])
        assert datasource_result is not None
        assert len(datasource_result) > 0
        assert datasource_result[0] is mock_datasource

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

    def test_sql_agent_modes(self, mock_store):
        """Test SqlAgent mode selection."""
        # Test basic mode (default)
        basic_agent = SqlAgent(model="gpt-3.5-turbo", mode="basic", store=mock_store)
        assert basic_agent.mode == SqlAgentMode.basic
        assert len(basic_agent.tools) == 3

        # Test enhanced mode
        enhanced_agent = SqlAgent(
            model="gpt-3.5-turbo", mode="enhanced", store=mock_store
        )
        assert enhanced_agent.mode == SqlAgentMode.enhanced
        assert len(enhanced_agent.tools) == 5  # Updated count: basic(3) + enhanced(2) = 5

    def test_format_messages_structure(self, workflow_agent):
        """Test _format_messages returns correct structure."""
        formatted_state = workflow_agent._format_messages("Test question")

        assert isinstance(formatted_state, dict)
        assert "messages" in formatted_state
        # datasource should not be in formatted state
        assert "datasource" not in formatted_state
