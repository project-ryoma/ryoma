#!/usr/bin/env python3
"""
Simplified integration tests for WorkflowAgent with InjectedStore.
"""

from unittest.mock import Mock, patch

import pytest
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.store.memory import InMemoryStore
from ryoma_ai.agent.workflow import WorkflowAgent
from ryoma_ai.datasource.sql import SqlDataSource
from ryoma_ai.tool.sql_tool import SchemaAnalysisTool, SqlQueryTool


class MockChatModel(BaseChatModel):
    """Simple mock chat model for testing."""

    def __init__(self, responses: list = None):
        super().__init__()
        self.responses = responses or ["Test response"]
        self.response_index = 0

    def _generate(self, messages, stop=None, **kwargs):
        if self.response_index < len(self.responses):
            response = self.responses[self.response_index]
            self.response_index += 1
        else:
            response = self.responses[-1]

        mock_generation = Mock()
        mock_generation.message = AIMessage(content=response)
        mock_result = Mock()
        mock_result.generations = [[mock_generation]]
        return mock_result

    def _llm_type(self):
        return "mock_chat_model"

    @property
    def _identifying_params(self):
        return {"model": "mock"}


class TestWorkflowAgentIntegration:
    """Integration tests for WorkflowAgent."""

    @pytest.fixture
    def mock_datasource(self):
        """Create a mock SQL datasource."""
        datasource = Mock(spec=SqlDataSource)
        datasource.query.return_value = "Query executed successfully"
        datasource.get_catalog.return_value = Mock(
            catalog_name="test_catalog", schemas=[]
        )
        return datasource

    @pytest.fixture
    def sql_tools(self):
        """Create SQL tools for testing."""
        return [SqlQueryTool(), SchemaAnalysisTool()]

    @pytest.fixture
    def workflow_agent(self, mock_datasource, sql_tools):
        """Create a WorkflowAgent with mock dependencies."""
        mock_model = MockChatModel(["I'll help you with your query."])

        return WorkflowAgent(
            tools=sql_tools,
            model=mock_model,
            datasource=mock_datasource,
            user_id="test_user",
            thread_id="test_thread",
        )

    def test_agent_initialization_with_store(self, workflow_agent, mock_datasource):
        """Test WorkflowAgent properly initializes with store."""
        assert workflow_agent.store is not None
        assert isinstance(workflow_agent.store, InMemoryStore)

        # Verify datasource is in store
        datasource_result = workflow_agent.store.get(("datasource",), "main")
        assert datasource_result is not None
        assert datasource_result.value is mock_datasource

    def test_workflow_compilation(self, workflow_agent):
        """Test workflow compiles correctly."""
        workflow = workflow_agent.workflow
        assert workflow is not None

        graph = workflow.get_graph()
        node_ids = [node.id for node in graph.nodes]
        assert "agent" in node_ids
        assert "tools" in node_ids

    def test_basic_workflow_execution(self, workflow_agent):
        """Test basic workflow execution."""
        result = workflow_agent.invoke("Test query", display=False)
        assert result is not None
        assert "messages" in result

    def test_tool_execution_workflow(self, workflow_agent):
        """Test workflow with tool execution."""
        # Mock model to return tool calls
        mock_model = Mock()
        mock_response = Mock()
        mock_response.content = "I'll execute the query."
        mock_response.tool_calls = [
            {
                "id": "test_call_1",
                "name": "sql_database_query",
                "args": {"query": "SELECT * FROM users"},
            }
        ]
        mock_model.invoke.return_value = mock_response
        workflow_agent.model = mock_model

        with patch.object(workflow_agent, "build_tool_node") as mock_tool_node:
            mock_tool_node.return_value.invoke.return_value = {
                "messages": [
                    ToolMessage(
                        content="Query executed",
                        tool_call_id="test_call_1",
                    )
                ]
            }

            result = workflow_agent.invoke("Execute query", display=False)
            assert result is not None
            assert "messages" in result

    def test_store_persistence(self, workflow_agent, mock_datasource):
        """Test store maintains datasource across calls."""
        # First call
        workflow_agent.invoke("First query", display=False)

        # Verify datasource persists
        datasource_result = workflow_agent.store.get(("datasource",), "main")
        assert datasource_result is not None
        assert datasource_result.value is mock_datasource

        # Second call
        workflow_agent.invoke("Second query", display=False)

        # Still persists
        datasource_result = workflow_agent.store.get(("datasource",), "main")
        assert datasource_result is not None

    def test_error_handling(self, workflow_agent, mock_datasource):
        """Test error handling when tools fail."""
        mock_datasource.query.side_effect = Exception("Database error")

        result = workflow_agent.invoke("Execute query", display=False)
        assert result is not None
        assert "messages" in result

    def test_workflow_state_management(self, workflow_agent):
        """Test workflow state is managed correctly."""
        # Execute workflow
        workflow_agent.invoke("Test query", display=False)

        # Check state
        current_state = workflow_agent.get_current_state()
        assert current_state is not None

    def test_workflow_without_datasource(self, sql_tools):
        """Test workflow without datasource."""
        mock_model = MockChatModel(["I'll help without datasource"])

        agent = WorkflowAgent(tools=sql_tools, model=mock_model)

        # Store should be empty for datasource
        datasource_result = agent.store.get(("datasource",), "main")
        assert datasource_result is None

        # Should still work
        result = agent.invoke("Test without datasource", display=False)
        assert result is not None


class TestWorkflowErrorScenarios:
    """Test error scenarios in WorkflowAgent."""

    def test_failing_datasource(self):
        """Test with completely failing datasource."""
        failing_ds = Mock(spec=SqlDataSource)
        failing_ds.query.side_effect = Exception("Connection failed")

        mock_model = MockChatModel(["I'll try to help"])
        agent = WorkflowAgent(
            tools=[SqlQueryTool()], model=mock_model, datasource=failing_ds
        )

        result = agent.invoke("Test failing datasource", display=False)
        assert result is not None

    def test_corrupted_store(self):
        """Test with corrupted store data."""
        mock_model = MockChatModel(["Test response"])
        agent = WorkflowAgent(tools=[SqlQueryTool()], model=mock_model)

        # Corrupt store
        agent.store.put(("datasource",), "main", "invalid_data")

        result = agent.invoke("Test corrupted store", display=False)
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
