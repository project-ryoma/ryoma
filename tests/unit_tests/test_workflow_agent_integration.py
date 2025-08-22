#!/usr/bin/env python3
"""
Integration tests for WorkflowAgent with InjectedStore implementation.
Tests complete workflow functionality including store management, tool execution, 
and state handling across multiple workflow iterations.
"""

import uuid
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch

import pytest
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.store.memory import InMemoryStore
from ryoma_ai.agent.workflow import ToolMode, WorkflowAgent
from ryoma_ai.datasource.sql import SqlDataSource
from ryoma_ai.states import MessageState
from ryoma_ai.tool.sql_tool import (
    Column,
    CreateTableTool,
    QueryPlanTool,
    SchemaAnalysisTool,
    SqlQueryTool,
)


class MockChatModel(BaseChatModel):
    """Mock chat model for testing."""

    def __init__(self, responses: List[str] = None):
        super().__init__()
        self.responses = responses or ["Test response"]
        self.response_index = 0
        self.call_count = 0

    def _generate(self, messages, stop=None, **kwargs):
        self.call_count += 1
        if self.response_index < len(self.responses):
            response = self.responses[self.response_index]
            self.response_index += 1
        else:
            response = self.responses[-1]

        # Create a mock response that mimics langchain's ChatGeneration
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
    """Integration tests for WorkflowAgent with complete workflow scenarios."""

    @pytest.fixture
    def mock_datasource(self):
        """Create a mock SQL datasource with various method responses."""
        datasource = Mock(spec=SqlDataSource)
        datasource.query.return_value = "Query executed successfully"
        datasource.get_query_plan.return_value = "Execution plan details"
        datasource.get_query_profile.return_value = "Performance profile"

        # Mock catalog structure
        mock_catalog = Mock()
        mock_catalog.catalog_name = "test_catalog"
        mock_catalog.schemas = []
        datasource.get_catalog.return_value = mock_catalog

        return datasource

    @pytest.fixture
    def sql_tools(self):
        """Create a list of SQL tools for testing."""
        return [
            SqlQueryTool(),
            CreateTableTool(),
            QueryPlanTool(),
            SchemaAnalysisTool(),
        ]

    @pytest.fixture
    def workflow_agent(self, mock_datasource, sql_tools):
        """Create a WorkflowAgent with mock dependencies."""
        mock_model = MockChatModel(
            [
                "I'll help you with your SQL query.",
                "Let me analyze the database schema first.",
                "Based on the analysis, here's the result.",
            ]
        )

        agent = WorkflowAgent(
            tools=sql_tools,
            model=mock_model,
            datasource=mock_datasource,
            user_id="test_user",
            thread_id="test_thread",
        )

        return agent

    def test_agent_initialization_with_store(self, workflow_agent, mock_datasource):
        """Test that WorkflowAgent properly initializes with store containing datasource."""
        # Verify store is initialized
        assert workflow_agent.store is not None
        assert isinstance(workflow_agent.store, InMemoryStore)

        # Verify datasource is in store
        datasource_result = workflow_agent.store.get(("datasource",), "main")
        assert datasource_result is not None
        assert datasource_result.value is mock_datasource

        # Verify tools are bound
        assert len(workflow_agent.tools) == 4
        assert workflow_agent.model is not None

    def test_workflow_compilation_with_store(self, workflow_agent):
        """Test that workflow compiles correctly with store parameter."""
        workflow = workflow_agent.workflow
        assert workflow is not None

        # Verify workflow has necessary components
        graph = workflow.get_graph()
        assert "agent" in [node.id for node in graph.nodes]
        assert "tools" in [node.id for node in graph.nodes]

    def test_single_tool_execution_workflow(self, workflow_agent, mock_datasource):
        """Test complete workflow with single tool execution."""
        # Create a mock model that will trigger tool calls
        mock_model = Mock()
        mock_response = Mock()
        mock_response.content = "I'll execute the SQL query for you."
        mock_response.tool_calls = [
            {
                "id": "test_call_1",
                "name": "sql_database_query",
                "args": {"query": "SELECT * FROM users"},
            }
        ]
        mock_model.invoke.return_value = mock_response
        workflow_agent.model = mock_model

        # Mock the tool node to return successful execution
        with patch.object(workflow_agent, "build_tool_node") as mock_tool_node:
            mock_tool_response = Mock()
            mock_tool_response.content = "Query executed successfully"
            mock_tool_node.return_value.invoke.return_value = {
                "messages": [
                    ToolMessage(
                        content="Query executed successfully",
                        tool_call_id="test_call_1",
                    )
                ]
            }

            # Execute workflow
            result = workflow_agent.invoke(
                question="Execute a query to get all users",
                tool_mode=ToolMode.CONTINUOUS,
                display=False,
            )

            assert result is not None
            assert "messages" in result

    def test_multiple_tool_execution_workflow(self, workflow_agent, mock_datasource):
        """Test workflow with multiple sequential tool executions."""
        # Setup mock responses for multiple tool calls
        mock_model = Mock()

        # First response: schema analysis
        schema_response = Mock()
        schema_response.content = "Let me analyze the schema first."
        schema_response.tool_calls = [
            {"id": "schema_call_1", "name": "schema_analysis", "args": {}}
        ]

        # Second response: query execution
        query_response = Mock()
        query_response.content = "Now I'll execute the query."
        query_response.tool_calls = [
            {
                "id": "query_call_1",
                "name": "sql_database_query",
                "args": {"query": "SELECT * FROM analyzed_table"},
            }
        ]

        # Final response: no more tools
        final_response = Mock()
        final_response.content = "Task completed successfully."
        final_response.tool_calls = []

        mock_model.invoke.side_effect = [
            schema_response,
            query_response,
            final_response,
        ]
        workflow_agent.model = mock_model

        # Mock tool executions
        with patch.object(workflow_agent, "build_tool_node") as mock_tool_node:

            def mock_tool_execution(state):
                messages = state.get("messages", [])
                last_message = messages[-1] if messages else None

                if last_message and hasattr(last_message, "tool_calls"):
                    tool_call = last_message.tool_calls[0]
                    if tool_call["name"] == "schema_analysis":
                        return {
                            "messages": [
                                ToolMessage(
                                    content="Schema analysis completed",
                                    tool_call_id=tool_call["id"],
                                )
                            ]
                        }
                    elif tool_call["name"] == "sql_database_query":
                        return {
                            "messages": [
                                ToolMessage(
                                    content="Query executed successfully",
                                    tool_call_id=tool_call["id"],
                                )
                            ]
                        }

                return {"messages": []}

            mock_tool_node.return_value.invoke.side_effect = mock_tool_execution

            # Execute workflow with continuous mode
            result = workflow_agent.invoke(
                question="Analyze schema and execute query",
                tool_mode=ToolMode.CONTINUOUS,
                max_iterations=3,
                display=False,
            )

            assert result is not None
            # Verify multiple tool calls were made
            assert mock_model.invoke.call_count >= 2

    def test_store_persistence_across_calls(self, workflow_agent, mock_datasource):
        """Test that store maintains datasource across multiple workflow calls."""
        # First call
        result1 = workflow_agent.invoke("First query", display=False)

        # Verify datasource is still in store
        datasource_result = workflow_agent.store.get(("datasource",), "main")
        assert datasource_result is not None
        assert datasource_result.value is mock_datasource

        # Second call
        result2 = workflow_agent.invoke("Second query", display=False)

        # Verify datasource is still accessible
        datasource_result = workflow_agent.store.get(("datasource",), "main")
        assert datasource_result is not None
        assert datasource_result.value is mock_datasource

    def test_tool_error_handling_in_workflow(self, workflow_agent, mock_datasource):
        """Test error handling when tools fail during workflow execution."""
        # Configure datasource to throw an error
        mock_datasource.query.side_effect = Exception("Database connection failed")

        # Create a model that will call the failing tool
        mock_model = Mock()
        mock_response = Mock()
        mock_response.content = "I'll execute the query."
        mock_response.tool_calls = [
            {
                "id": "failing_call_1",
                "name": "sql_database_query",
                "args": {"query": "SELECT * FROM users"},
            }
        ]
        mock_model.invoke.return_value = mock_response
        workflow_agent.model = mock_model

        # Execute workflow - should handle error gracefully
        result = workflow_agent.invoke(question="Execute a query", display=False)

        assert result is not None
        # The workflow should continue despite tool failure
        assert "messages" in result

    def test_state_management_during_interruption(self, workflow_agent):
        """Test state management when workflow is interrupted."""
        # Create a model that will trigger tool calls
        mock_model = Mock()
        mock_response = Mock()
        mock_response.content = "I need to use a tool."
        mock_response.tool_calls = [
            {
                "id": "interrupt_call_1",
                "name": "sql_database_query",
                "args": {"query": "SELECT 1"},
            }
        ]
        mock_model.invoke.return_value = mock_response
        workflow_agent.model = mock_model

        # Execute workflow (will be interrupted before tools)
        result = workflow_agent.invoke("Test query", display=False)

        # Check current state
        current_state = workflow_agent.get_current_state()
        assert current_state is not None

        # Should be interrupted at tools node
        if current_state.next:
            assert "tools" in current_state.next

        # Verify we can get current tool calls
        tool_calls = workflow_agent.get_current_tool_calls()
        assert len(tool_calls) > 0
        assert tool_calls[0]["name"] == "sql_database_query"

    def test_concurrent_workflow_execution(self, mock_datasource, sql_tools):
        """Test concurrent execution of multiple workflow instances."""
        import threading
        import time

        results = []
        errors = []

        def run_workflow(thread_id):
            try:
                mock_model = MockChatModel([f"Response from thread {thread_id}"])
                agent = WorkflowAgent(
                    tools=sql_tools,
                    model=mock_model,
                    datasource=mock_datasource,
                    thread_id=f"thread_{thread_id}",
                )

                result = agent.invoke(f"Query from thread {thread_id}", display=False)
                results.append((thread_id, result))
            except Exception as e:
                errors.append((thread_id, e))

        # Create multiple threads
        threads = [threading.Thread(target=run_workflow, args=(i,)) for i in range(3)]

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # Verify results
        assert len(results) == 3
        assert len(errors) == 0

        # Each thread should have its own result
        thread_ids = [result[0] for result in results]
        assert len(set(thread_ids)) == 3

    def test_workflow_with_custom_graph(self, mock_datasource, sql_tools):
        """Test WorkflowAgent with custom workflow graph."""
        from langgraph.graph import StateGraph

        # Create custom graph
        custom_graph = StateGraph(MessageState)

        mock_model = MockChatModel(["Custom workflow response"])
        agent = WorkflowAgent(
            tools=sql_tools, model=mock_model, datasource=mock_datasource
        )

        # Build workflow with custom graph
        agent.build_workflow(custom_graph)

        # Verify workflow was rebuilt
        assert agent._workflow is not None

        # Test execution
        result = agent.invoke("Test custom workflow", display=False)
        assert result is not None

    def test_tool_parameter_updates(self, workflow_agent):
        """Test updating tool parameters during workflow execution."""
        # Setup workflow with tool call
        mock_model = Mock()
        mock_response = Mock()
        mock_response.content = "I'll execute the query."
        mock_response.tool_calls = [
            {
                "id": "update_call_1",
                "name": "sql_database_query",
                "args": {"query": "SELECT * FROM old_table"},
            }
        ]
        mock_model.invoke.return_value = mock_response
        workflow_agent.model = mock_model

        # Execute to get to tool state
        workflow_agent.invoke("Execute query", display=False)

        # Update tool parameters
        new_args = {"query": "SELECT * FROM new_table"}
        workflow_agent.update_tool("update_call_1", new_args)

        # Verify tool was updated
        current_tool_calls = workflow_agent.get_current_tool_calls()
        assert len(current_tool_calls) > 0
        assert current_tool_calls[0]["args"]["query"] == "SELECT * FROM new_table"

    def test_workflow_memory_persistence(self, workflow_agent):
        """Test that workflow memory persists conversation history."""
        # First interaction
        result1 = workflow_agent.invoke("First question", display=False)

        # Second interaction - should have memory of first
        result2 = workflow_agent.invoke("Follow-up question", display=False)

        # Check that state contains messages from both interactions
        current_state = workflow_agent.get_current_state()
        assert current_state is not None

        messages = current_state.values.get("messages", [])
        assert len(messages) >= 2  # At least one from each interaction

        # Verify message types
        human_messages = [msg for msg in messages if isinstance(msg, HumanMessage)]
        assert len(human_messages) >= 2


class TestWorkflowAgentErrorScenarios:
    """Test error scenarios and edge cases in WorkflowAgent integration."""

    @pytest.fixture
    def failing_datasource(self):
        """Create a datasource that fails in various ways."""
        datasource = Mock(spec=SqlDataSource)
        datasource.query.side_effect = Exception("Connection timeout")
        datasource.get_catalog.side_effect = Exception("Catalog access denied")
        return datasource

    def test_workflow_with_no_datasource(self, sql_tools):
        """Test workflow behavior when no datasource is provided."""
        mock_model = MockChatModel(["I'll try to help without datasource"])

        agent = WorkflowAgent(
            tools=sql_tools,
            model=mock_model,
            # No datasource provided
        )

        # Store should be empty
        datasource_result = agent.store.get(("datasource",), "main")
        assert datasource_result is None

        # Workflow should still execute
        result = agent.invoke("Test without datasource", display=False)
        assert result is not None

    def test_workflow_with_corrupted_store(self, workflow_agent):
        """Test workflow behavior when store becomes corrupted."""
        # Corrupt the store by putting invalid data
        workflow_agent.store.put(("datasource",), "main", "invalid_datasource")

        # Create model that will try to use tools
        mock_model = Mock()
        mock_response = Mock()
        mock_response.content = "I'll use a tool."
        mock_response.tool_calls = [
            {
                "id": "corrupt_call_1",
                "name": "sql_database_query",
                "args": {"query": "SELECT 1"},
            }
        ]
        mock_model.invoke.return_value = mock_response
        workflow_agent.model = mock_model

        # Workflow should handle corrupted store gracefully
        result = workflow_agent.invoke("Test with corrupted store", display=False)
        assert result is not None

    def test_workflow_with_failing_tools(self, failing_datasource, sql_tools):
        """Test workflow behavior when all tools fail."""
        mock_model = MockChatModel(["I'll try to use tools"])

        agent = WorkflowAgent(
            tools=sql_tools, model=mock_model, datasource=failing_datasource
        )

        # Execute workflow - tools will fail but workflow should continue
        result = agent.invoke("Execute failing operations", display=False)
        assert result is not None

        # Workflow should have error handling
        assert "messages" in result

    def test_workflow_max_iterations_exceeded(self, workflow_agent):
        """Test workflow behavior when max iterations are exceeded."""
        # Create model that always wants to call tools
        mock_model = Mock()
        mock_response = Mock()
        mock_response.content = "I need more tools."
        mock_response.tool_calls = [
            {
                "id": f"loop_call_{i}",
                "name": "sql_database_query",
                "args": {"query": f"SELECT {i}"},
            }
            for i in range(5)
        ]  # Multiple tool calls
        mock_model.invoke.return_value = mock_response
        workflow_agent.model = mock_model

        # Execute with low max iterations
        result = workflow_agent.invoke(
            "Start infinite loop",
            tool_mode=ToolMode.CONTINUOUS,
            max_iterations=2,  # Low limit
            display=False,
        )

        assert result is not None
        # Should stop after max iterations


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
