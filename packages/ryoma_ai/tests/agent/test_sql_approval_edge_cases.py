#!/usr/bin/env python3
"""
Edge cases and error scenario tests for SQL approval workflow.

Tests unusual inputs, error conditions, and boundary cases that could
occur during human-in-the-loop SQL execution approval.
"""

from unittest.mock import Mock, patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.errors import GraphInterrupt
from langgraph.types import Command
from ryoma_ai.agent.internals.enhanced_sql_agent import EnhancedSqlAgent
from ryoma_ai.agent.workflow import WorkflowAgent
from ryoma_ai.models.sql import QueryStatus, SqlQueryResult


class TestSqlApprovalEdgeCases:
    """Test edge cases for SQL approval workflow."""

    @pytest.fixture
    def enhanced_sql_agent(self):
        """Create an Enhanced SQL Agent for testing."""
        with patch("ryoma_ai.agent.internals.enhanced_sql_agent.SqlErrorHandler"):
            with patch(
                "ryoma_ai.agent.internals.enhanced_sql_agent.SqlSafetyValidator"
            ):
                datasource = Mock()
                agent = EnhancedSqlAgent(model="gpt-4", datasource=datasource)
                return agent

    def test_empty_sql_query_handling(self, enhanced_sql_agent):
        """Test handling of empty or None SQL queries."""

        state = {"messages": [], "generated_sql": ""}  # Empty SQL

        result_state = enhanced_sql_agent._execute_query(state)

        # Should return early with no execution message
        assert result_state["execution_result"] == "No SQL query to execute"

    def test_none_sql_query_handling(self, enhanced_sql_agent):
        """Test handling of None SQL queries."""

        state = {"messages": [], "generated_sql": None}  # None SQL

        with patch(
            "ryoma_ai.agent.internals.enhanced_sql_agent.interrupt"
        ) as mock_interrupt:
            # Should not reach interrupt due to early return
            result_state = enhanced_sql_agent._execute_query(state)

            # Interrupt should not be called
            mock_interrupt.assert_not_called()
            assert result_state["execution_result"] == "No SQL query to execute"

    def test_malformed_approval_response(self, enhanced_sql_agent):
        """Test handling of malformed approval responses."""

        # Mock interrupt to return unexpected data types
        malformed_responses = [
            None,  # None response
            123,  # Integer response
            [],  # Empty list
            {"invalid": "structure"},  # Dict without expected keys
        ]

        for response in malformed_responses:
            with patch(
                "ryoma_ai.agent.internals.enhanced_sql_agent.interrupt"
            ) as mock_interrupt:
                mock_interrupt.return_value = response

                # Mock SQL execution
                mock_tool = Mock()
                mock_result = SqlQueryResult(
                    status=QueryStatus.SUCCESS, data=[{"id": 1}], row_count=1
                )
                mock_tool._run.return_value = mock_result

                with patch(
                    "ryoma_ai.agent.internals.enhanced_sql_agent.SqlQueryTool",
                    return_value=mock_tool,
                ):
                    state = {"messages": [], "generated_sql": "SELECT * FROM users"}

                    # Should not crash - should treat as approval and execute
                    result_state = enhanced_sql_agent._execute_query(state)

                    # Verify it executed (since malformed responses default to approval)
                    assert "execution_result" in result_state

    def test_empty_string_approval_response(self, enhanced_sql_agent):
        """Test handling of empty string approval response."""

        with patch(
            "ryoma_ai.agent.internals.enhanced_sql_agent.interrupt"
        ) as mock_interrupt:
            mock_interrupt.return_value = ""  # Empty string

            mock_tool = Mock()
            mock_result = SqlQueryResult(
                status=QueryStatus.SUCCESS, data=[{"id": 1}], row_count=1
            )
            mock_tool._run.return_value = mock_result

            with patch(
                "ryoma_ai.agent.internals.enhanced_sql_agent.SqlQueryTool",
                return_value=mock_tool,
            ):
                state = {"messages": [], "generated_sql": "SELECT * FROM users"}

                result_state = enhanced_sql_agent._execute_query(state)

                # Empty string should be treated as edited SQL (empty query)
                assert result_state["generated_sql"] == ""

    def test_whitespace_only_approval_response(self, enhanced_sql_agent):
        """Test handling of whitespace-only approval response."""

        with patch(
            "ryoma_ai.agent.internals.enhanced_sql_agent.interrupt"
        ) as mock_interrupt:
            mock_interrupt.return_value = "   \n\t   "  # Whitespace only

            mock_tool = Mock()
            mock_result = SqlQueryResult(
                status=QueryStatus.SUCCESS, data=[], row_count=0
            )
            mock_tool._run.return_value = mock_result

            with patch(
                "ryoma_ai.agent.internals.enhanced_sql_agent.SqlQueryTool",
                return_value=mock_tool,
            ):
                state = {"messages": [], "generated_sql": "SELECT * FROM users"}

                result_state = enhanced_sql_agent._execute_query(state)

                # Whitespace should be stripped and treated as empty
                assert result_state["generated_sql"] == ""

    def test_case_insensitive_approval_responses(self, enhanced_sql_agent):
        """Test that approval responses are case insensitive."""

        approval_variants = ["YES", "Yes", "APPROVE", "Approve", "OK", "Ok"]
        denial_variants = ["NO", "No", "DENY", "Deny", "REJECT", "Reject"]

        # Test approval variants
        for approval in approval_variants:
            with patch(
                "ryoma_ai.agent.internals.enhanced_sql_agent.interrupt"
            ) as mock_interrupt:
                mock_interrupt.return_value = approval

                mock_tool = Mock()
                mock_result = SqlQueryResult(
                    status=QueryStatus.SUCCESS, data=[{"id": 1}], row_count=1
                )
                mock_tool._run.return_value = mock_result

                with patch(
                    "ryoma_ai.agent.internals.enhanced_sql_agent.SqlQueryTool",
                    return_value=mock_tool,
                ):
                    state = {"messages": [], "generated_sql": "SELECT * FROM users"}

                    result_state = enhanced_sql_agent._execute_query(state)

                    # Should execute successfully
                    assert "execution_result" in result_state
                    assert result_state["execution_result"] == [{"id": 1}]

        # Test denial variants
        for denial in denial_variants:
            with patch(
                "ryoma_ai.agent.internals.enhanced_sql_agent.interrupt"
            ) as mock_interrupt:
                mock_interrupt.return_value = denial

                state = {"messages": [], "generated_sql": "SELECT * FROM users"}

                result_state = enhanced_sql_agent._execute_query(state)

                # Should be denied
                assert (
                    result_state["execution_result"] == "Query execution denied by user"
                )

    def test_sql_execution_exception_during_approval(self, enhanced_sql_agent):
        """Test handling of exceptions during SQL execution after approval."""

        with patch(
            "ryoma_ai.agent.internals.enhanced_sql_agent.interrupt"
        ) as mock_interrupt:
            mock_interrupt.return_value = "yes"  # User approves

            # Mock SQL tool to raise exception
            mock_tool = Mock()
            mock_tool._run.side_effect = Exception("Database connection failed")

            with patch(
                "ryoma_ai.agent.internals.enhanced_sql_agent.SqlQueryTool",
                return_value=mock_tool,
            ):
                state = {"messages": [], "generated_sql": "SELECT * FROM users"}

                result_state = enhanced_sql_agent._execute_query(state)

                # Should handle exception gracefully
                assert "error_info" in result_state
                assert (
                    "Database connection failed"
                    in result_state["error_info"]["error_message"]
                )

    def test_very_long_sql_query(self, enhanced_sql_agent):
        """Test handling of very long SQL queries in approval."""

        # Create a very long SQL query
        long_sql = (
            "SELECT " + ", ".join([f"col_{i}" for i in range(1000)]) + " FROM users"
        )

        with patch(
            "ryoma_ai.agent.internals.enhanced_sql_agent.interrupt"
        ) as mock_interrupt:
            mock_interrupt.return_value = "yes"

            mock_tool = Mock()
            mock_result = SqlQueryResult(
                status=QueryStatus.SUCCESS, data=[{"result": "success"}], row_count=1
            )
            mock_tool._run.return_value = mock_result

            with patch(
                "ryoma_ai.agent.internals.enhanced_sql_agent.SqlQueryTool",
                return_value=mock_tool,
            ):
                state = {"messages": [], "generated_sql": long_sql}

                result_state = enhanced_sql_agent._execute_query(state)

                # Should handle long query correctly
                assert "execution_result" in result_state

                # Verify the interrupt was called with the long query
                call_args = mock_interrupt.call_args[0][0]
                assert call_args["sql_query"] == long_sql

    def test_sql_query_with_special_characters(self, enhanced_sql_agent):
        """Test handling of SQL queries with special characters."""

        special_sql = (
            "SELECT name FROM users WHERE comment LIKE '%test \\\"data\\\" \\n\\t%'"
        )

        with patch(
            "ryoma_ai.agent.internals.enhanced_sql_agent.interrupt"
        ) as mock_interrupt:
            mock_interrupt.return_value = "approve"

            mock_tool = Mock()
            mock_result = SqlQueryResult(
                status=QueryStatus.SUCCESS, data=[{"name": "test"}], row_count=1
            )
            mock_tool._run.return_value = mock_result

            with patch(
                "ryoma_ai.agent.internals.enhanced_sql_agent.SqlQueryTool",
                return_value=mock_tool,
            ):
                state = {"messages": [], "generated_sql": special_sql}

                result_state = enhanced_sql_agent._execute_query(state)

                # Should handle special characters correctly
                assert "execution_result" in result_state


class TestWorkflowAgentEdgeCases:
    """Test edge cases for WorkflowAgent Command handling."""

    @pytest.fixture
    def workflow_agent(self):
        """Create a workflow agent for testing."""
        agent = WorkflowAgent(tools=[], model="gpt-4")
        return agent

    def test_invalid_command_object(self, workflow_agent):
        """Test handling of invalid Command objects."""

        # Mock workflow
        mock_workflow = Mock()
        mock_workflow.invoke.return_value = {"messages": [AIMessage(content="Success")]}
        workflow_agent._workflow = mock_workflow

        # Create invalid command (no resume value)
        invalid_command = Mock(spec=Command)

        # Should still pass to workflow and let it handle
        workflow_agent.invoke(invalid_command)

        mock_workflow.invoke.assert_called_once_with(
            invalid_command, config=workflow_agent.config
        )

    def test_command_with_complex_resume_value(self, workflow_agent):
        """Test Command with complex resume values."""

        mock_workflow = Mock()
        mock_workflow.invoke.return_value = {
            "messages": [AIMessage(content="Complex handled")]
        }
        workflow_agent._workflow = mock_workflow

        # Complex resume value
        complex_resume = {
            "action": "edit",
            "edited_sql": "SELECT id, name FROM users WHERE active = true",
            "reason": "Security - avoid selecting all columns",
        }

        command = Command(resume=complex_resume)
        result = workflow_agent.invoke(command)

        # Should pass complex object correctly
        mock_workflow.invoke.assert_called_once_with(
            command, config=workflow_agent.config
        )
        assert result["messages"][0].content == "Complex handled"

    def test_none_input_handling(self, workflow_agent):
        """Test handling of None input."""

        mock_workflow = Mock()
        mock_workflow.invoke.return_value = {
            "messages": [AIMessage(content="None handled")]
        }
        workflow_agent._workflow = mock_workflow

        # Mock get_current_tool_calls to return empty list
        with patch.object(workflow_agent, "get_current_tool_calls", return_value=[]):
            with patch.object(workflow_agent, "_format_messages") as mock_format:
                mock_format.return_value = {"messages": [HumanMessage(content="")]}

                workflow_agent.invoke(None)

                # Should format as empty message
                mock_format.assert_called_once_with(None)

    def test_concurrent_interrupts(self, enhanced_sql_agent):
        """Test handling of multiple concurrent interrupts (edge case)."""

        # This tests the theoretical case where interrupt might be called multiple times
        with patch(
            "ryoma_ai.agent.internals.enhanced_sql_agent.interrupt"
        ) as mock_interrupt:
            # First call raises GraphInterrupt, second call returns approval
            mock_interrupt.side_effect = [GraphInterrupt("First interrupt"), "yes"]

            state = {"messages": [], "generated_sql": "SELECT * FROM users"}

            # First call should raise GraphInterrupt
            with pytest.raises(GraphInterrupt, match="First interrupt"):
                enhanced_sql_agent._execute_query(state)

    def test_message_state_without_messages_key(self, workflow_agent):
        """Test handling of dict input without 'messages' key."""

        mock_workflow = Mock()
        mock_workflow.invoke.return_value = {
            "messages": [AIMessage(content="Dict handled")]
        }
        workflow_agent._workflow = mock_workflow

        # Dict that looks like MessageState but missing messages
        fake_state = {"question": "test", "other_data": "value"}

        with patch.object(workflow_agent, "_format_messages") as mock_format:
            mock_format.return_value = {"messages": [HumanMessage(content="test")]}

            workflow_agent.invoke(fake_state)

            # Should be treated as string question and formatted
            mock_format.assert_called_once_with(fake_state)

    def test_extremely_large_approval_data(self, enhanced_sql_agent):
        """Test handling of extremely large approval request data."""

        # Create large SQL query (simulating edge case)
        large_query = (
            "SELECT * FROM users WHERE id IN ("
            + ",".join(str(i) for i in range(10000))
            + ")"
        )

        with patch(
            "ryoma_ai.agent.internals.enhanced_sql_agent.interrupt"
        ) as mock_interrupt:
            mock_interrupt.return_value = "yes"

            mock_tool = Mock()
            mock_result = SqlQueryResult(
                status=QueryStatus.SUCCESS, data=[{"id": 1}], row_count=1
            )
            mock_tool._run.return_value = mock_result

            with patch(
                "ryoma_ai.agent.internals.enhanced_sql_agent.SqlQueryTool",
                return_value=mock_tool,
            ):
                state = {"messages": [], "generated_sql": large_query}

                # Should handle large query without issues
                result_state = enhanced_sql_agent._execute_query(state)
                assert "execution_result" in result_state


class TestErrorRecoveryDuringApproval:
    """Test error recovery scenarios during approval workflow."""

    @pytest.fixture
    def enhanced_sql_agent_with_error_handler(self):
        """Create agent with mocked error handler."""
        with patch("ryoma_ai.agent.internals.enhanced_sql_agent.SqlSafetyValidator"):
            datasource = Mock()
            agent = EnhancedSqlAgent(model="gpt-4", datasource=datasource)

            # Mock error handler
            mock_error_handler = Mock()
            agent.error_handler = mock_error_handler

            return agent, mock_error_handler

    def test_error_analysis_during_execution(
        self, enhanced_sql_agent_with_error_handler
    ):
        """Test that error analysis is triggered when SQL execution fails."""

        agent, mock_error_handler = enhanced_sql_agent_with_error_handler

        with patch(
            "ryoma_ai.agent.internals.enhanced_sql_agent.interrupt"
        ) as mock_interrupt:
            mock_interrupt.return_value = "yes"  # User approves

            # Mock failed SQL execution
            mock_tool = Mock()
            failed_result = SqlQueryResult(
                status=QueryStatus.ERROR,
                error_message="Table 'nonexistent' doesn't exist",
                query="SELECT * FROM nonexistent",
                data={"raw_exception": Exception("Table error")},
            )
            mock_tool._run.return_value = failed_result

            # Mock enhanced error analysis
            mock_error_handler.analyze_query_result.return_value = failed_result

            with patch(
                "ryoma_ai.agent.internals.enhanced_sql_agent.SqlQueryTool",
                return_value=mock_tool,
            ):
                state = {"messages": [], "generated_sql": "SELECT * FROM nonexistent"}

                result_state = agent._execute_query(state)

                # Verify error info includes enhanced analysis
                assert "error_info" in result_state
                assert "sql_query_result" in result_state["error_info"]
                assert result_state["error_info"]["sql_query_result"] == failed_result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
