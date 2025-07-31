#!/usr/bin/env python3
"""
Unit tests to verify that LangGraph injected state/store works correctly
for passing datasource to SQL tools in the WorkflowAgent.
"""

import pytest
from unittest.mock import Mock

from ryoma_ai.agent.workflow import WorkflowAgent
from ryoma_ai.agent.sql import SqlAgent
from ryoma_ai.tool.sql_tool import SqlQueryTool, SchemaAnalysisTool
from ryoma_ai.datasource.sql import SqlDataSource
from ryoma_ai.models.agent import SqlAgentMode


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
        return [
            SqlQueryTool(),
            SchemaAnalysisTool(),
        ]

    @pytest.fixture
    def workflow_agent(self, mock_datasource, sql_tools):
        """Create a WorkflowAgent with mock datasource and SQL tools."""
        return WorkflowAgent(
            tools=sql_tools,
            model="gpt-3.5-turbo",
            datasource=mock_datasource
        )

    def test_agent_has_datasource(self, workflow_agent, mock_datasource):
        """Test that the agent properly stores the datasource."""
        assert workflow_agent.get_datasource() is mock_datasource

    def test_workflow_creation(self, workflow_agent):
        """Test that workflow can be created successfully."""
        workflow = workflow_agent.workflow
        assert workflow is not None

    def test_state_formatting_excludes_datasource(self, workflow_agent, mock_datasource):
        """Test that _format_messages no longer includes datasource in the state."""
        formatted_state = workflow_agent._format_messages("Test question")
        
        # datasource should no longer be in formatted state since we use InjectedStore
        assert "datasource" not in formatted_state
        assert "messages" in formatted_state
        assert len(formatted_state["messages"]) == 1

    def test_tool_node_creation(self, workflow_agent, sql_tools):
        """Test that tool node can be created successfully."""
        tool_node = workflow_agent.build_tool_node(sql_tools)
        assert tool_node is not None

    def test_sql_tools_have_injected_store_annotation(self):
        """Test that SQL tools have the correct InjectedStore annotation."""
        sql_query_tool = SqlQueryTool()
        schema_analysis_tool = SchemaAnalysisTool()
        
        # Check that tools have the proper schema with InjectedStore annotation
        assert hasattr(sql_query_tool, 'args_schema')
        assert hasattr(schema_analysis_tool, 'args_schema')
        
        # Verify that the args_schema includes datasource field
        query_schema = sql_query_tool.args_schema
        analysis_schema = schema_analysis_tool.args_schema
        
        assert hasattr(query_schema, '__annotations__')
        assert hasattr(analysis_schema, '__annotations__')
        
        # The datasource field should be present in the schema
        assert 'datasource' in query_schema.model_fields
        assert 'datasource' in analysis_schema.model_fields

    def test_message_state_structure(self, workflow_agent):
        """Test that MessageState has the correct structure for InjectedStore approach."""
        from ryoma_ai.states import MessageState
        
        # Check that MessageState has messages field but no datasource field
        assert hasattr(MessageState, '__annotations__')
        assert 'messages' in MessageState.__annotations__
        # datasource should no longer be in state since we use InjectedStore
        assert 'datasource' not in MessageState.__annotations__

    def test_workflow_agent_initialization_with_tools(self, mock_datasource):
        """Test WorkflowAgent initialization with various tool configurations and store setup."""
        # Test with empty tools list
        agent_no_tools = WorkflowAgent(
            tools=[],
            model="gpt-3.5-turbo",
            datasource=mock_datasource
        )
        assert agent_no_tools.get_datasource() is mock_datasource
        assert agent_no_tools.tools == []
        # Check that store is configured in config
        assert "store" in agent_no_tools.config
        assert agent_no_tools.config["store"]["datasource"] is mock_datasource
        
        # Test with SQL tools
        sql_tools = [SqlQueryTool(), SchemaAnalysisTool()]
        agent_with_tools = WorkflowAgent(
            tools=sql_tools,
            model="gpt-3.5-turbo", 
            datasource=mock_datasource
        )
        assert agent_with_tools.get_datasource() is mock_datasource
        assert len(agent_with_tools.tools) == 2
        # Check that store is configured in config
        assert "store" in agent_with_tools.config
        assert agent_with_tools.config["store"]["datasource"] is mock_datasource

    def test_format_messages_without_current_state(self, workflow_agent):
        """Test _format_messages when there's no current workflow state."""
        # This should not raise an exception even if no workflow has been run yet
        formatted_state = workflow_agent._format_messages("Test question")
        
        assert isinstance(formatted_state, dict)
        assert "messages" in formatted_state
        # datasource should no longer be in formatted state since we use InjectedStore
        assert "datasource" not in formatted_state

    def test_print_graph_events_handles_non_message_objects(self, workflow_agent):
        """Test that _print_graph_events handles non-message objects gracefully."""
        # Create mock events with non-message objects (like tuples from tools)
        mock_events = [
            {
                "tools": {
                    "messages": [
                        ("result", "artifact"),  # Tuple without .id attribute
                        None,  # Non-message object
                        "string_result"  # String without .id attribute
                    ]
                }
            }
        ]
        
        printed = set()
        
        # Should not raise AttributeError
        try:
            workflow_agent._print_graph_events(mock_events, printed)
        except AttributeError as e:
            if "'tuple' object has no attribute 'id'" in str(e):
                pytest.fail("_print_graph_events should handle non-message objects gracefully")
            else:
                raise

    def test_sql_agent_mode_selection(self, mock_datasource):
        """Test that SqlAgent correctly selects modes and doesn't always use reforce mode."""
        # Test basic mode (default)
        basic_agent = SqlAgent(
            model="gpt-3.5-turbo",
            datasource=mock_datasource
        )
        assert basic_agent.mode == SqlAgentMode.basic
        assert basic_agent._agent is None  # Should use parent WorkflowAgent
        assert len(basic_agent.tools) == 3  # Only basic tools
        assert [tool.name for tool in basic_agent.tools] == [
            'sql_database_query', 'create_table', 'query_profile'
        ]

        # Test explicit basic mode
        explicit_basic_agent = SqlAgent(
            model="gpt-3.5-turbo",
            datasource=mock_datasource,
            mode=SqlAgentMode.basic
        )
        assert explicit_basic_agent.mode == SqlAgentMode.basic
        assert explicit_basic_agent._agent is None
        assert len(explicit_basic_agent.tools) == 3

        # Test enhanced mode
        enhanced_agent = SqlAgent(
            model="gpt-3.5-turbo",
            datasource=mock_datasource,
            mode=SqlAgentMode.enhanced
        )
        assert enhanced_agent.mode == SqlAgentMode.enhanced
        assert enhanced_agent._agent is not None  # Should use EnhancedSqlAgent
        assert len(enhanced_agent.tools) == 7  # All enhanced tools

        # Test reforce mode
        reforce_agent = SqlAgent(
            model="gpt-3.5-turbo",
            datasource=mock_datasource,
            mode=SqlAgentMode.reforce
        )
        assert reforce_agent.mode == SqlAgentMode.reforce
        assert reforce_agent._agent is not None  # Should use ReFoRCESqlAgent
        assert len(reforce_agent.tools) == 7  # All enhanced tools