#!/usr/bin/env python3
"""
Tests for SqlAgent factory pattern implementation.
Tests the factory pattern, agent creation, and mode-specific functionality.
"""

from typing import Dict, Optional
from unittest.mock import Mock, patch

import pytest
from ryoma_ai.agent.sql import (
    BasicSqlAgent,
    EnhancedSqlAgentImpl,
    ReFoRCESqlAgentImpl,
    SqlAgent,
)
from ryoma_ai.datasource.sql import SqlDataSource
from ryoma_ai.models.agent import SqlAgentMode


class TestSqlAgentFactory:
    """Test the SqlAgent factory pattern via __new__ method."""

    @pytest.fixture
    def mock_datasource(self):
        """Create a mock SQL datasource."""
        datasource = Mock(spec=SqlDataSource)
        datasource.query.return_value = "Mock query result"
        return datasource

    def test_create_basic_agent(self, mock_datasource):
        """Test SqlAgent creates BasicSqlAgent for basic mode."""
        agent = SqlAgent(
            model="gpt-4", datasource=mock_datasource, mode=SqlAgentMode.basic
        )

        assert isinstance(agent, BasicSqlAgent)
        assert agent.mode == SqlAgentMode.basic
        assert len(agent.tools) == 3  # Basic tools

        # Test with string mode
        agent_str = SqlAgent(model="gpt-4", datasource=mock_datasource, mode="basic")

        assert isinstance(agent_str, BasicSqlAgent)
        assert agent_str.mode == SqlAgentMode.basic

    def test_create_enhanced_agent(self, mock_datasource):
        """Test SqlAgent creates EnhancedSqlAgentImpl for enhanced mode."""
        agent = SqlAgent(
            model="gpt-4",
            datasource=mock_datasource,
            mode=SqlAgentMode.enhanced,
            safety_config={"enable_validation": True},
        )

        assert isinstance(agent, EnhancedSqlAgentImpl)
        assert agent.mode == SqlAgentMode.enhanced
        assert len(agent.tools) == 7  # Enhanced tools
        assert hasattr(agent, "_internal_agent")

        # Test with string mode
        agent_str = SqlAgent(model="gpt-4", datasource=mock_datasource, mode="enhanced")

        assert isinstance(agent_str, EnhancedSqlAgentImpl)
        assert agent_str.mode == SqlAgentMode.enhanced

    def test_create_reforce_agent(self, mock_datasource):
        """Test SqlAgent creates ReFoRCESqlAgentImpl for reforce mode."""
        agent = SqlAgent(
            model="gpt-4",
            datasource=mock_datasource,
            mode=SqlAgentMode.reforce,
            safety_config={"enable_validation": True},
        )

        assert isinstance(agent, ReFoRCESqlAgentImpl)
        assert agent.mode == SqlAgentMode.reforce
        assert len(agent.tools) == 7  # ReFoRCE tools
        assert hasattr(agent, "_internal_agent")

        # Test with string mode
        agent_str = SqlAgent(model="gpt-4", datasource=mock_datasource, mode="reforce")

        assert isinstance(agent_str, ReFoRCESqlAgentImpl)
        assert agent_str.mode == SqlAgentMode.reforce

    def test_default_mode(self, mock_datasource):
        """Test SqlAgent defaults to basic mode when no mode specified."""
        agent = SqlAgent(model="gpt-4", datasource=mock_datasource)

        assert isinstance(agent, BasicSqlAgent)
        assert agent.mode == SqlAgentMode.basic

    def test_with_all_parameters(self, mock_datasource):
        """Test SqlAgent with all possible parameters."""
        model_params = {"temperature": 0.7}
        embedding_config = {"model": "text-embedding-ada-002"}
        vector_store_config = {"type": "chroma"}
        safety_config = {"enable_validation": True}

        agent = SqlAgent(
            model="gpt-4",
            model_parameters=model_params,
            datasource=mock_datasource,
            embedding=embedding_config,
            vector_store=vector_store_config,
            mode=SqlAgentMode.enhanced,
            safety_config=safety_config,
            user_id="test_user",
            thread_id="test_thread",
        )

        assert isinstance(agent, EnhancedSqlAgentImpl)
        assert agent.mode == SqlAgentMode.enhanced


class TestBasicSqlAgent:
    """Test the BasicSqlAgent implementation."""

    @pytest.fixture
    def mock_datasource(self):
        datasource = Mock(spec=SqlDataSource)
        datasource.query.return_value = "Basic query result"
        return datasource

    def test_basic_agent_initialization(self, mock_datasource):
        """Test BasicSqlAgent initialization."""
        agent = BasicSqlAgent(model="gpt-4", datasource=mock_datasource)

        assert agent.mode == SqlAgentMode.basic
        assert len(agent.tools) == 3

        # Verify tools are basic tools
        tool_names = [tool.name for tool in agent.tools]
        expected_tools = ["sql_database_query", "create_table", "query_profile"]
        for tool_name in expected_tools:
            assert tool_name in tool_names

    def test_basic_agent_unsupported_methods(self, mock_datasource):
        """Test that basic agent raises NotImplementedError for advanced methods."""
        agent = BasicSqlAgent(model="gpt-4", datasource=mock_datasource)

        with pytest.raises(
            NotImplementedError, match="Safety rules require enhanced or reforce mode"
        ):
            agent.enable_safety_rule("no_drop_tables")

        with pytest.raises(
            NotImplementedError, match="Safety rules require enhanced or reforce mode"
        ):
            agent.disable_safety_rule("no_drop_tables")

        with pytest.raises(
            NotImplementedError,
            match="Safety configuration requires enhanced or reforce mode",
        ):
            agent.set_safety_config({"enable_validation": True})

        with pytest.raises(
            NotImplementedError,
            match="Schema analysis requires enhanced or reforce mode",
        ):
            agent.analyze_schema("Find customer data")

        with pytest.raises(
            NotImplementedError,
            match="Query planning requires enhanced or reforce mode",
        ):
            agent.create_query_plan("Get sales data")


class TestEnhancedSqlAgentImpl:
    """Test the EnhancedSqlAgentImpl implementation."""

    @pytest.fixture
    def mock_datasource(self):
        datasource = Mock(spec=SqlDataSource)
        datasource.query.return_value = "Enhanced query result"
        return datasource

    @patch("ryoma_ai.agent.sql.InternalEnhancedSqlAgent")
    def test_enhanced_agent_initialization(self, mock_enhanced_class, mock_datasource):
        """Test EnhancedSqlAgentImpl initialization."""
        mock_internal_agent = Mock()
        mock_enhanced_class.return_value = mock_internal_agent

        agent = EnhancedSqlAgentImpl(
            model="gpt-4",
            datasource=mock_datasource,
            safety_config={"enable_validation": True},
        )

        assert agent.mode == SqlAgentMode.enhanced
        assert len(agent.tools) == 7
        assert agent._internal_agent is mock_internal_agent

        # Verify internal agent was created with correct parameters
        mock_enhanced_class.assert_called_once_with(
            model="gpt-4",
            model_parameters=None,
            datasource=mock_datasource,
            safety_config={"enable_validation": True},
        )

        # Verify tools are enhanced tools
        tool_names = [tool.name for tool in agent.tools]
        expected_tools = [
            "sql_database_query",
            "create_table",
            "query_profile",
            "schema_analysis",
            "query_validation",
            "query_optimization",
            "query_explanation",
        ]
        for tool_name in expected_tools:
            assert tool_name in tool_names

    @patch("ryoma_ai.agent.sql.InternalEnhancedSqlAgent")
    def test_enhanced_agent_safety_methods(self, mock_enhanced_class, mock_datasource):
        """Test safety methods delegation to internal agent."""
        mock_internal_agent = Mock()
        mock_safety_validator = Mock()
        mock_internal_agent.safety_validator = mock_safety_validator
        mock_enhanced_class.return_value = mock_internal_agent

        agent = EnhancedSqlAgentImpl(model="gpt-4", datasource=mock_datasource)

        # Test enable_safety_rule
        agent.enable_safety_rule("no_drop_tables")
        mock_safety_validator.enable_rule.assert_called_once_with("no_drop_tables")

        # Test disable_safety_rule
        agent.disable_safety_rule("no_truncate")
        mock_safety_validator.disable_rule.assert_called_once_with("no_truncate")

        # Test set_safety_config
        config = {"enable_validation": True}
        agent.set_safety_config(config)
        mock_safety_validator.set_safety_config.assert_called_once_with(config)

    @patch("ryoma_ai.agent.sql.InternalEnhancedSqlAgent")
    def test_enhanced_agent_schema_and_planning_methods(
        self, mock_enhanced_class, mock_datasource
    ):
        """Test schema analysis and query planning methods."""
        mock_internal_agent = Mock()
        mock_schema_agent = Mock()
        mock_query_planner = Mock()
        mock_internal_agent.schema_agent = mock_schema_agent
        mock_internal_agent.query_planner = mock_query_planner
        mock_enhanced_class.return_value = mock_internal_agent

        agent = EnhancedSqlAgentImpl(model="gpt-4", datasource=mock_datasource)

        # Test schema analysis
        mock_schema_agent.analyze_schema_relationships.return_value = (
            "Schema analysis result"
        )
        result = agent.analyze_schema("Find customer relationships")
        assert result == "Schema analysis result"
        mock_schema_agent.analyze_schema_relationships.assert_called_once_with(
            "Find customer relationships"
        )

        # Test query planning
        mock_query_planner.create_query_plan.return_value = "Query plan result"
        context = {"tables": ["customers", "orders"]}
        result = agent.create_query_plan("Get customer orders", context)
        assert result == "Query plan result"
        mock_query_planner.create_query_plan.assert_called_once_with(
            "Get customer orders", context
        )

    @patch("ryoma_ai.agent.sql.InternalEnhancedSqlAgent")
    def test_enhanced_agent_missing_components(
        self, mock_enhanced_class, mock_datasource
    ):
        """Test behavior when internal agent is missing expected components."""
        mock_internal_agent = Mock()
        # Don't set safety_validator, schema_agent, or query_planner attributes
        mock_enhanced_class.return_value = mock_internal_agent

        agent = EnhancedSqlAgentImpl(model="gpt-4", datasource=mock_datasource)

        # Safety methods should do nothing when validator is missing
        agent.enable_safety_rule("test_rule")  # Should not raise
        agent.disable_safety_rule("test_rule")  # Should not raise
        agent.set_safety_config({"test": True})  # Should not raise

        # Schema and planning methods should raise NotImplementedError
        with pytest.raises(NotImplementedError, match="Schema analysis not available"):
            agent.analyze_schema("test question")

        with pytest.raises(NotImplementedError, match="Query planning not available"):
            agent.create_query_plan("test question")


class TestReFoRCESqlAgentImpl:
    """Test the ReFoRCESqlAgentImpl implementation."""

    @pytest.fixture
    def mock_datasource(self):
        datasource = Mock(spec=SqlDataSource)
        datasource.query.return_value = "ReFoRCE query result"
        return datasource

    @patch("ryoma_ai.agent.sql.InternalReFoRCESqlAgent")
    def test_reforce_agent_initialization(self, mock_reforce_class, mock_datasource):
        """Test ReFoRCESqlAgentImpl initialization."""
        mock_internal_agent = Mock()
        mock_reforce_class.return_value = mock_internal_agent

        agent = ReFoRCESqlAgentImpl(
            model="gpt-4",
            datasource=mock_datasource,
            safety_config={"enable_validation": True},
        )

        assert agent.mode == SqlAgentMode.reforce
        assert len(agent.tools) == 7
        assert agent._internal_agent is mock_internal_agent

        # Verify internal agent was created with correct parameters
        mock_reforce_class.assert_called_once_with(
            model="gpt-4",
            model_parameters=None,
            datasource=mock_datasource,
            safety_config={"enable_validation": True},
        )


class TestBackwardCompatibility:
    """Test backward compatibility with existing code."""

    @pytest.fixture
    def mock_datasource(self):
        datasource = Mock(spec=SqlDataSource)
        return datasource

    def test_can_still_import_sql_agent(self):
        """Test that SqlAgent can still be imported."""
        from ryoma_ai.agent.sql import SqlAgent

        assert SqlAgent is not None

    def test_can_import_from_agent_module(self):
        """Test that classes can be imported from agent module."""
        from ryoma_ai.agent import BasicSqlAgent, SqlAgent

        assert SqlAgent is not None
        assert BasicSqlAgent is not None

    def test_handles_invalid_mode_gracefully(self, mock_datasource):
        """Test that SqlAgent handles invalid modes gracefully."""
        with pytest.raises(ValueError):
            SqlAgent(model="gpt-4", datasource=mock_datasource, mode="invalid_mode")

    def test_user_can_create_sql_agent_directly(self, mock_datasource):
        """Test that users can still create SqlAgent with simple syntax."""
        # This is the key requirement - users should be able to use SqlAgent(...) directly
        agent = SqlAgent(model="gpt-4", datasource=mock_datasource, mode="basic")

        assert isinstance(agent, BasicSqlAgent)
        assert agent.mode == SqlAgentMode.basic

        # Test with enhanced mode
        enhanced_agent = SqlAgent(
            model="gpt-4", datasource=mock_datasource, mode="enhanced"
        )

        assert isinstance(enhanced_agent, EnhancedSqlAgentImpl)
        assert enhanced_agent.mode == SqlAgentMode.enhanced


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
