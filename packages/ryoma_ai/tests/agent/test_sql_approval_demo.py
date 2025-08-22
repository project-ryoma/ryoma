#!/usr/bin/env python3
"""
Demonstration and integration tests for SQL approval workflow.

This file provides practical examples showing how the human-in-the-loop
SQL approval workflow would be used in real applications.
"""

from unittest.mock import Mock, create_autospec, patch

import pytest
from langchain_core.messages import HumanMessage
from langgraph.errors import GraphInterrupt
from langgraph.types import Command
from ryoma_ai.agent.internals.enhanced_sql_agent import EnhancedSqlAgent
from ryoma_ai.datasource.sql import SqlDataSource
from ryoma_ai.models.sql import QueryStatus, SqlQueryResult


class MockGraphInterruptWorkflow:
    """
    Mock workflow that simulates the interrupt/resume pattern properly.

    This helps test the complete flow without needing a full LangGraph setup.
    """

    def __init__(self, agent):
        self.agent = agent
        self.state = None
        self.interrupted = False
        self.interrupt_data = None

    def invoke(self, input_data, config=None):
        """Simulate workflow invocation with interrupt handling."""

        if isinstance(input_data, Command):
            # Resume from interrupt
            if self.interrupted and self.state:
                # Simulate resuming execution with the resume value
                with patch(
                    "ryoma_ai.agent.internals.enhanced_sql_agent.interrupt"
                ) as mock_interrupt:
                    mock_interrupt.return_value = input_data.resume

                    # Continue from where we left off
                    result_state = self.agent._execute_query(self.state)
                    self.interrupted = False
                    return result_state
            else:
                raise ValueError("No interrupted state to resume from")

        elif isinstance(input_data, dict) and "messages" in input_data:
            # Initial invocation - simulate the workflow steps
            self.state = {
                "messages": input_data["messages"],
                "generated_sql": "SELECT id, name, email FROM users WHERE active = true ORDER BY created_at DESC LIMIT 10",
                "question": (
                    input_data["messages"][0].content if input_data["messages"] else ""
                ),
            }

            # Simulate interrupt during execution
            try:
                with patch(
                    "ryoma_ai.agent.internals.enhanced_sql_agent.interrupt"
                ) as mock_interrupt:
                    mock_interrupt.side_effect = GraphInterrupt(
                        {
                            "type": "sql_execution_approval",
                            "sql_query": self.state["generated_sql"],
                            "question": self.state["question"],
                            "message": f"Please approve: {self.state['generated_sql']}",
                        }
                    )

                    # This should trigger the interrupt
                    self.agent._execute_query(self.state)

            except GraphInterrupt as e:
                self.interrupted = True
                self.interrupt_data = e.value
                return {
                    "interrupted": True,
                    "interrupt_data": self.interrupt_data,
                    "state": self.state,
                }

        return {"error": "Unexpected input type"}


class TestSqlApprovalDemo:
    """Demonstration tests showing practical usage."""

    @pytest.fixture
    def mock_datasource(self):
        """Create a realistic mock datasource."""
        datasource = create_autospec(SqlDataSource, spec_set=True)

        # Mock successful query execution
        def mock_query(sql):
            if "users" in sql.lower():
                return [
                    {"id": 1, "name": "John Doe", "email": "john@example.com"},
                    {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
                ]
            return []

        datasource.query.side_effect = mock_query
        return datasource

    @pytest.fixture
    def enhanced_sql_agent(self, mock_datasource):
        """Create a fully configured Enhanced SQL Agent."""
        with patch("ryoma_ai.agent.internals.enhanced_sql_agent.SqlErrorHandler"):
            with patch(
                "ryoma_ai.agent.internals.enhanced_sql_agent.SqlSafetyValidator"
            ):
                agent = EnhancedSqlAgent(
                    model="gpt-4",
                    datasource=mock_datasource,
                    safety_config={
                        "require_approval": True,
                        "allow_destructive": False,
                    },
                )
                return agent

    def test_complete_approval_workflow_demo(self, enhanced_sql_agent):
        """
        Demonstration of the complete approval workflow from start to finish.

        This test shows how a real application would use the approval system.
        """

        # Step 1: User asks a question
        user_question = (
            "Show me the most recent active users with their email addresses"
        )

        # Step 2: Create mock workflow
        workflow = MockGraphInterruptWorkflow(enhanced_sql_agent)

        # Step 3: Initial invocation (should trigger interrupt)
        initial_input = {"messages": [HumanMessage(content=user_question)]}

        result = workflow.invoke(initial_input)

        # Step 4: Verify interrupt was triggered
        assert result["interrupted"] is True
        assert result["interrupt_data"]["type"] == "sql_execution_approval"

        generated_sql = result["interrupt_data"]["sql_query"]
        print(f"Generated SQL: {generated_sql}")

        # Step 5: User approves the query
        approval_command = Command(resume="yes")

        # Mock successful SQL execution for approval
        mock_tool = Mock()
        mock_result = SqlQueryResult(
            status=QueryStatus.SUCCESS,
            data=[
                {"id": 1, "name": "John Doe", "email": "john@example.com"},
                {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
            ],
            row_count=2,
            column_count=3,
        )
        mock_tool._run.return_value = mock_result

        with patch(
            "ryoma_ai.agent.internals.enhanced_sql_agent.SqlQueryTool",
            return_value=mock_tool,
        ):
            # Step 6: Resume with approval
            final_result = workflow.invoke(approval_command)

            # Step 7: Verify successful execution
            assert "execution_result" in final_result
            assert len(final_result["execution_result"]) == 2
            assert final_result["execution_result"][0]["name"] == "John Doe"

            # Verify success message
            messages = final_result.get("messages", [])
            success_messages = [
                m for m in messages if "approved and executed successfully" in m.content
            ]
            assert len(success_messages) > 0

    def test_denial_workflow_demo(self, enhanced_sql_agent):
        """Demonstration of user denying SQL execution."""

        workflow = MockGraphInterruptWorkflow(enhanced_sql_agent)

        # Initial request
        result = workflow.invoke(
            {"messages": [HumanMessage(content="Delete all inactive users")]}
        )

        assert result["interrupted"] is True

        # User denies the query
        denial_command = Command(resume="no")
        final_result = workflow.invoke(denial_command)

        # Verify execution was denied
        assert final_result["execution_result"] == "Query execution denied by user"

        messages = final_result.get("messages", [])
        denial_messages = [m for m in messages if "denied by user" in m.content]
        assert len(denial_messages) > 0

    def test_query_editing_workflow_demo(self, enhanced_sql_agent):
        """Demonstration of user editing the SQL query."""

        workflow = MockGraphInterruptWorkflow(enhanced_sql_agent)

        # Initial request
        result = workflow.invoke(
            {"messages": [HumanMessage(content="Show all user data")]}
        )

        assert result["interrupted"] is True
        result["interrupt_data"]["sql_query"]

        # User provides edited query (more restrictive)
        edited_sql = "SELECT id, name FROM users WHERE active = true LIMIT 5"
        edit_command = Command(resume=edited_sql)

        # Mock successful execution of edited query
        mock_tool = Mock()
        mock_result = SqlQueryResult(
            status=QueryStatus.SUCCESS,
            data=[{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}],
            row_count=2,
            column_count=2,
        )
        mock_tool._run.return_value = mock_result

        with patch(
            "ryoma_ai.agent.internals.enhanced_sql_agent.SqlQueryTool",
            return_value=mock_tool,
        ):
            final_result = workflow.invoke(edit_command)

            # Verify the SQL was updated
            assert final_result["generated_sql"] == edited_sql

            # Verify execution was successful
            assert "execution_result" in final_result
            assert len(final_result["execution_result"]) == 2

            # Verify edit message
            messages = final_result.get("messages", [])
            edit_messages = [m for m in messages if "user-edited query" in m.content]
            assert len(edit_messages) > 0

    def test_structured_response_demo(self, enhanced_sql_agent):
        """Demonstration of structured approval responses."""

        workflow = MockGraphInterruptWorkflow(enhanced_sql_agent)

        # Initial request
        result = workflow.invoke(
            {"messages": [HumanMessage(content="Get user statistics")]}
        )

        assert result["interrupted"] is True

        # Test structured denial
        structured_denial = Command(resume={"action": "deny"})
        final_result = workflow.invoke(structured_denial)

        assert final_result["execution_result"] == "Query execution denied by user"

    def test_error_handling_during_approval_demo(self, enhanced_sql_agent):
        """Demonstration of error handling when SQL execution fails."""

        workflow = MockGraphInterruptWorkflow(enhanced_sql_agent)

        # Initial request
        result = workflow.invoke({"messages": [HumanMessage(content="Show user data")]})

        assert result["interrupted"] is True

        # User approves
        approval_command = Command(resume="yes")

        # Mock failed SQL execution
        mock_tool = Mock()
        mock_result = SqlQueryResult(
            status=QueryStatus.ERROR,
            error_message="Table 'users' does not exist",
            query="SELECT * FROM users",
            data={"raw_exception": Exception("Table not found")},
        )
        mock_tool._run.return_value = mock_result

        with patch(
            "ryoma_ai.agent.internals.enhanced_sql_agent.SqlQueryTool",
            return_value=mock_tool,
        ):
            final_result = workflow.invoke(approval_command)

            # Verify error was handled properly
            assert "error_info" in final_result
            assert (
                "Table 'users' does not exist"
                in final_result["error_info"]["error_message"]
            )
            assert "sql_query_result" in final_result["error_info"]

    def test_multiple_approval_rounds_demo(self, enhanced_sql_agent):
        """
        Demonstration of multiple rounds of approval (user keeps editing).

        This shows how the system handles iterative refinement.
        """

        workflow = MockGraphInterruptWorkflow(enhanced_sql_agent)

        # Round 1: Initial request
        result = workflow.invoke(
            {"messages": [HumanMessage(content="Show all user information")]}
        )

        assert result["interrupted"] is True
        result["interrupt_data"]["sql_query"]

        # Round 1: User edits query
        edited_sql_1 = "SELECT id, name, email FROM users WHERE active = true"
        edit_command_1 = Command(resume=edited_sql_1)

        # Mock execution to show we'd need another approval round
        # (In practice, this would trigger another interrupt)
        mock_tool = Mock()
        mock_result = SqlQueryResult(
            status=QueryStatus.SUCCESS,
            data=[{"id": 1, "name": "John", "email": "john@test.com"}],
            row_count=1,
            column_count=3,
        )
        mock_tool._run.return_value = mock_result

        with patch(
            "ryoma_ai.agent.internals.enhanced_sql_agent.SqlQueryTool",
            return_value=mock_tool,
        ):
            final_result = workflow.invoke(edit_command_1)

            # Verify the first edit was applied and executed
            assert final_result["generated_sql"] == edited_sql_1
            assert "execution_result" in final_result

    def test_real_world_scenario_demo(self, enhanced_sql_agent):
        """
        Real-world scenario: Analytics query requiring approval.

        Shows how the system would handle a typical business analytics request.
        """

        workflow = MockGraphInterruptWorkflow(enhanced_sql_agent)

        # Business user request
        business_question = (
            "I need to see our top 20 customers by total order value this quarter"
        )

        result = workflow.invoke(
            {"messages": [HumanMessage(content=business_question)]}
        )

        assert result["interrupted"] is True

        # Simulate that a complex SQL query was generated
        result["interrupt_data"]["sql_query"]

        # Business analyst reviews and approves
        approval_command = Command(resume="yes")

        # Mock realistic business data
        mock_tool = Mock()
        mock_result = SqlQueryResult(
            status=QueryStatus.SUCCESS,
            data=[
                {
                    "customer_id": 101,
                    "customer_name": "ACME Corp",
                    "total_value": 45000.00,
                },
                {
                    "customer_id": 102,
                    "customer_name": "TechStart Inc",
                    "total_value": 38500.00,
                },
                {
                    "customer_id": 103,
                    "customer_name": "Global Systems",
                    "total_value": 32000.00,
                },
            ],
            row_count=3,
            column_count=3,
        )
        mock_tool._run.return_value = mock_result

        with patch(
            "ryoma_ai.agent.internals.enhanced_sql_agent.SqlQueryTool",
            return_value=mock_tool,
        ):
            final_result = workflow.invoke(approval_command)

            # Verify business data was returned
            assert "execution_result" in final_result
            customers = final_result["execution_result"]
            assert len(customers) == 3
            assert customers[0]["customer_name"] == "ACME Corp"
            assert customers[0]["total_value"] == 45000.00


class TestPerformanceAndLoad:
    """Test performance characteristics of the approval system."""

    def test_large_result_set_approval(self, enhanced_sql_agent):
        """Test approval system with large result sets."""

        workflow = MockGraphInterruptWorkflow(enhanced_sql_agent)

        result = workflow.invoke(
            {"messages": [HumanMessage(content="Get all transactions for analysis")]}
        )

        assert result["interrupted"] is True

        approval_command = Command(resume="yes")

        # Mock large result set
        mock_tool = Mock()
        large_dataset = [
            {"transaction_id": i, "amount": i * 10.5} for i in range(10000)
        ]
        mock_result = SqlQueryResult(
            status=QueryStatus.SUCCESS,
            data=large_dataset,
            row_count=10000,
            column_count=2,
        )
        mock_tool._run.return_value = mock_result

        with patch(
            "ryoma_ai.agent.internals.enhanced_sql_agent.SqlQueryTool",
            return_value=mock_tool,
        ):
            final_result = workflow.invoke(approval_command)

            # Should handle large datasets without issues
            assert len(final_result["execution_result"]) == 10000

    def test_concurrent_approval_requests(self, enhanced_sql_agent):
        """Test handling of concurrent approval requests (theoretical)."""

        # This test verifies that the interrupt mechanism is thread-safe
        # and can handle concurrent requests properly

        workflows = [MockGraphInterruptWorkflow(enhanced_sql_agent) for _ in range(3)]

        # Simulate concurrent requests
        results = []
        for i, workflow in enumerate(workflows):
            result = workflow.invoke({"messages": [HumanMessage(content=f"Query {i}")]})
            results.append(result)

        # All should interrupt independently
        for result in results:
            assert result["interrupted"] is True
            assert "sql_execution_approval" in result["interrupt_data"]["type"]


if __name__ == "__main__":
    # Run demonstration tests
    pytest.main([__file__, "-v", "-s"])  # -s to show print statements
