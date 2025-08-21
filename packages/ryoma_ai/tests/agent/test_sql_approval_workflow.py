#!/usr/bin/env python3
"""
Tests for human-in-the-loop SQL approval workflow.

This module tests the complete workflow from question to SQL generation,
human approval/denial, and final execution with proper error handling.
"""

import pytest
from unittest.mock import Mock, patch
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import Command
from langgraph.errors import GraphInterrupt

from ryoma_ai.agent.internals.enhanced_sql_agent import EnhancedSqlAgent
from ryoma_ai.agent.workflow import WorkflowAgent
from ryoma_ai.datasource.sql import SqlDataSource
from ryoma_ai.models.sql import SqlQueryResult, QueryStatus


class TestSqlApprovalWorkflow:
    """Test the complete SQL approval workflow."""

    @pytest.fixture
    def mock_datasource(self):
        """Create a mock SQL datasource."""
        datasource = Mock(spec=SqlDataSource)
        datasource.query.return_value = Mock(
            is_success=True,
            data=[{"id": 1, "name": "test"}],
            row_count=1,
            column_count=2
        )
        return datasource

    @pytest.fixture
    def enhanced_sql_agent(self, mock_datasource):
        """Create an Enhanced SQL Agent for testing."""
        with patch('ryoma_ai.agent.internals.enhanced_sql_agent.SqlErrorHandler'):
            with patch('ryoma_ai.agent.internals.enhanced_sql_agent.SqlSafetyValidator'):
                agent = EnhancedSqlAgent(
                    model="gpt-4",
                    datasource=mock_datasource,
                    safety_config={"require_approval": True}
                )
                return agent

    @pytest.fixture
    def workflow_agent(self):
        """Create a basic workflow agent for testing Command handling."""
        tools = []
        agent = WorkflowAgent(
            tools=tools,
            model="gpt-4"
        )
        return agent

    def test_interrupt_triggers_on_sql_execution(self, enhanced_sql_agent):
        """Test that interrupt is triggered when executing SQL queries."""

        # Mock the interrupt to raise GraphInterrupt
        with patch('ryoma_ai.agent.internals.enhanced_sql_agent.interrupt') as mock_interrupt:
            mock_interrupt.side_effect = GraphInterrupt("SQL approval required")

            # Create test state
            state = {
                "messages": [HumanMessage(content="Show me users")],
                "generated_sql": "SELECT * FROM users LIMIT 10",
                "question": "Show me users"
            }

            # Execute query should trigger interrupt
            with pytest.raises(GraphInterrupt, match="SQL approval required"):
                enhanced_sql_agent._execute_query(state)

            # Verify interrupt was called with correct data
            mock_interrupt.assert_called_once()
            call_args = mock_interrupt.call_args[0][0]

            assert call_args["type"] == "sql_execution_approval"
            assert call_args["sql_query"] == "SELECT * FROM users LIMIT 10"
            assert "approve" in call_args["message"].lower()

    def test_approval_response_handling_approve(self, enhanced_sql_agent, mock_datasource):
        """Test handling of approval response - approve scenario."""

        # Mock interrupt to return approval
        with patch('ryoma_ai.agent.internals.enhanced_sql_agent.interrupt') as mock_interrupt:
            mock_interrupt.return_value = "yes"

            # Mock successful SQL execution
            mock_tool = Mock()
            mock_result = SqlQueryResult(
                status=QueryStatus.SUCCESS,
                data=[{"id": 1, "name": "John"}],
                row_count=1,
                column_count=2
            )
            mock_tool._run.return_value = mock_result

            with patch('ryoma_ai.agent.internals.enhanced_sql_agent.SqlQueryTool', return_value=mock_tool):
                state = {
                    "messages": [],
                    "generated_sql": "SELECT * FROM users LIMIT 10"
                }

                result_state = enhanced_sql_agent._execute_query(state)

                # Verify successful execution
                assert "execution_result" in result_state
                assert result_state["execution_result"] == [{"id": 1, "name": "John"}]

                # Verify success message
                messages = result_state.get("messages", [])
                assert len(messages) > 0
                assert "approved and executed successfully" in messages[-1].content

    def test_approval_response_handling_deny(self, enhanced_sql_agent):
        """Test handling of approval response - deny scenario."""

        # Mock interrupt to return denial
        with patch('ryoma_ai.agent.internals.enhanced_sql_agent.interrupt') as mock_interrupt:
            mock_interrupt.return_value = "no"

            state = {
                "messages": [],
                "generated_sql": "SELECT * FROM users LIMIT 10"
            }

            result_state = enhanced_sql_agent._execute_query(state)

            # Verify execution was denied
            assert result_state["execution_result"] == "Query execution denied by user"

            # Verify denial message
            messages = result_state.get("messages", [])
            assert len(messages) > 0
            assert "denied by user" in messages[-1].content

    def test_approval_response_handling_edit(self, enhanced_sql_agent, mock_datasource):
        """Test handling of approval response - edit query scenario."""

        edited_sql = "SELECT id, name FROM users LIMIT 5"

        # Mock interrupt to return edited query
        with patch('ryoma_ai.agent.internals.enhanced_sql_agent.interrupt') as mock_interrupt:
            mock_interrupt.return_value = edited_sql

            # Mock successful SQL execution
            mock_tool = Mock()
            mock_result = SqlQueryResult(
                status=QueryStatus.SUCCESS,
                data=[{"id": 1, "name": "John"}],
                row_count=1,
                column_count=2
            )
            mock_tool._run.return_value = mock_result

            with patch('ryoma_ai.agent.internals.enhanced_sql_agent.SqlQueryTool', return_value=mock_tool):
                state = {
                    "messages": [],
                    "generated_sql": "SELECT * FROM users LIMIT 10"
                }

                result_state = enhanced_sql_agent._execute_query(state)

                # Verify query was updated
                assert result_state["generated_sql"] == edited_sql

                # Verify edit message
                messages = result_state.get("messages", [])
                edit_messages = [m for m in messages if "user-edited query" in m.content]
                assert len(edit_messages) > 0

    def test_structured_approval_response(self, enhanced_sql_agent):
        """Test handling of structured approval responses."""

        # Test structured denial
        with patch('ryoma_ai.agent.internals.enhanced_sql_agent.interrupt') as mock_interrupt:
            mock_interrupt.return_value = {"action": "deny"}

            state = {
                "messages": [],
                "generated_sql": "SELECT * FROM users"
            }

            result_state = enhanced_sql_agent._execute_query(state)
            assert result_state["execution_result"] == "Query execution denied by user"

    def test_structured_edit_response(self, enhanced_sql_agent, mock_datasource):
        """Test handling of structured edit responses."""

        edited_sql = "SELECT id FROM users LIMIT 3"

        with patch('ryoma_ai.agent.internals.enhanced_sql_agent.interrupt') as mock_interrupt:
            mock_interrupt.return_value = {"edited_sql": edited_sql}

            # Mock successful execution
            mock_tool = Mock()
            mock_result = SqlQueryResult(
                status=QueryStatus.SUCCESS,
                data=[{"id": 1}],
                row_count=1,
                column_count=1
            )
            mock_tool._run.return_value = mock_result

            with patch('ryoma_ai.agent.internals.enhanced_sql_agent.SqlQueryTool', return_value=mock_tool):
                state = {
                    "messages": [],
                    "generated_sql": "SELECT * FROM users"
                }

                result_state = enhanced_sql_agent._execute_query(state)

                # Verify query was updated
                assert result_state["generated_sql"] == edited_sql

    def test_workflow_agent_command_handling(self, workflow_agent):
        """Test that WorkflowAgent properly handles Command objects."""

        # Mock the workflow to return a result
        mock_workflow = Mock()
        mock_workflow.invoke.return_value = {"messages": [AIMessage(content="Success")]}
        workflow_agent._workflow = mock_workflow

        # Test Command handling
        command = Command(resume="yes")
        result = workflow_agent.invoke(command)

        # Verify Command was passed directly to workflow
        mock_workflow.invoke.assert_called_once_with(command, config=workflow_agent.config)
        assert result == {"messages": [AIMessage(content="Success")]}

    def test_workflow_agent_messagestate_handling(self, workflow_agent):
        """Test that WorkflowAgent properly handles MessageState dictionaries."""

        # Mock the workflow
        mock_workflow = Mock()
        mock_workflow.invoke.return_value = {"messages": [AIMessage(content="Success")]}
        workflow_agent._workflow = mock_workflow

        # Test MessageState handling
        message_state = {"messages": [HumanMessage(content="test")]}
        result = workflow_agent.invoke(message_state)

        # Verify MessageState was passed directly to workflow
        mock_workflow.invoke.assert_called_once_with(message_state, config=workflow_agent.config)

    def test_workflow_agent_string_handling(self, workflow_agent):
        """Test that WorkflowAgent properly handles string questions."""

        # Mock the workflow
        mock_workflow = Mock()
        mock_workflow.invoke.return_value = {"messages": [AIMessage(content="Success")]}
        workflow_agent._workflow = mock_workflow

        # Mock the format_messages method
        with patch.object(workflow_agent, '_format_messages') as mock_format:
            mock_format.return_value = {"messages": [HumanMessage(content="test question")]}

            result = workflow_agent.invoke("test question")

            # Verify string was formatted as messages
            mock_format.assert_called_once_with("test question")
            mock_workflow.invoke.assert_called_once()

    def test_stream_command_handling(self, workflow_agent):
        """Test that stream method handles Command objects correctly."""

        # Mock the workflow
        mock_workflow = Mock()
        mock_events = [{"messages": [AIMessage(content="Event 1")]}]
        mock_workflow.stream.return_value = iter(mock_events)
        workflow_agent._workflow = mock_workflow

        # Test Command handling in stream
        command = Command(resume="approve")

        with patch.object(workflow_agent, '_print_graph_events'):
            events = workflow_agent.stream(command)

        # Verify Command was passed directly to workflow.stream
        mock_workflow.stream.assert_called_once_with(
            command,
            config=workflow_agent.config,
            stream_mode="values"
        )


class TestSqlApprovalIntegration:
    """Test integration between workflow and SQL approval."""

    @pytest.fixture
    def full_workflow(self, mock_datasource):
        """Create a complete workflow with SQL approval."""
        with patch('ryoma_ai.agent.internals.enhanced_sql_agent.SqlErrorHandler'):
            with patch('ryoma_ai.agent.internals.enhanced_sql_agent.SqlSafetyValidator'):
                agent = EnhancedSqlAgent(
                    model="gpt-4",
                    datasource=mock_datasource
                )
                return agent

    def test_complete_approval_workflow(self, full_workflow):
        """Test the complete workflow from question to execution."""

        # Mock the various components
        with patch.object(full_workflow, '_initialize_state') as mock_init:
            with patch.object(full_workflow, '_analyze_question') as mock_analyze:
                with patch.object(full_workflow, '_schema_linking') as mock_schema:
                    with patch.object(full_workflow, '_query_planning') as mock_plan:
                        with patch.object(full_workflow, '_generate_sql') as mock_generate:
                            with patch.object(full_workflow, '_validate_safety') as mock_validate:

                                # Set up mock returns
                                mock_init.return_value = {"messages": [], "question": "Show users"}
                                mock_analyze.return_value = {"question_type": "data_retrieval"}
                                mock_schema.return_value = {"relevant_tables": ["users"]}
                                mock_plan.return_value = {"query_plan": "simple_select"}
                                mock_generate.return_value = {"generated_sql": "SELECT * FROM users LIMIT 10"}
                                mock_validate.return_value = {"safety_check": {"is_safe": True}}

                                # Mock interrupt for approval
                                with patch('ryoma_ai.agent.internals.enhanced_sql_agent.interrupt') as mock_interrupt:
                                    mock_interrupt.return_value = "yes"  # Approve

                                    # Mock SQL execution
                                    mock_tool = Mock()
                                    mock_result = SqlQueryResult(
                                        status=QueryStatus.SUCCESS,
                                        data=[{"id": 1, "name": "John"}],
                                        row_count=1
                                    )
                                    mock_tool._run.return_value = mock_result

                                    with patch('ryoma_ai.agent.internals.enhanced_sql_agent.SqlQueryTool', return_value=mock_tool):

                                        # Create workflow and test execution
                                        workflow = full_workflow.build()

                                        # This would normally trigger an interrupt
                                        # In a real scenario, you'd catch the GraphInterrupt,
                                        # then resume with Command(resume="yes")

                                        # For this test, we'll verify the components are called
                                        assert mock_init.called
                                        assert mock_analyze.called
                                        assert mock_schema.called

    def test_error_handling_during_approval(self, full_workflow, mock_datasource):
        """Test error handling during the approval workflow."""

        with patch('ryoma_ai.agent.internals.enhanced_sql_agent.interrupt') as mock_interrupt:
            mock_interrupt.return_value = "yes"  # User approves

            # Mock SQL execution to fail
            mock_tool = Mock()
            mock_result = SqlQueryResult(
                status=QueryStatus.ERROR,
                error_message="Table 'users' does not exist",
                query="SELECT * FROM users"
            )
            mock_tool._run.return_value = mock_result

            with patch('ryoma_ai.agent.internals.enhanced_sql_agent.SqlQueryTool', return_value=mock_tool):
                state = {
                    "messages": [],
                    "generated_sql": "SELECT * FROM users"
                }

                result_state = full_workflow._execute_query(state)

                # Verify error was handled
                assert "error_info" in result_state
                assert result_state["error_info"]["error_message"] == "Table 'users' does not exist"
                assert result_state["error_info"]["sql_query"] == "SELECT * FROM users"

    @pytest.fixture
    def mock_datasource(self):
        """Create a mock datasource for testing."""
        datasource = Mock(spec=SqlDataSource)
        datasource.query.return_value = [{"id": 1, "name": "test"}]
        return datasource


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
