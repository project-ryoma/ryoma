#!/usr/bin/env python3
"""
Simplified tests for SQL tools with InjectedStore implementation.
"""

import base64
import pickle
from unittest.mock import Mock

import pytest
from langgraph.store.memory import InMemoryStore
from ryoma_ai.datasource.sql import SqlDataSource
from ryoma_ai.tool.sql_tool import (
    Column,
    CreateTableTool,
    QueryOptimizationTool,
    QueryPlanTool,
    QueryProfileTool,
    QueryValidationTool,
    SchemaAnalysisTool,
    SqlQueryTool,
    get_datasource_from_store,
)


class TestDatasourceHelper:
    """Test the get_datasource_from_store helper function."""

    def test_get_datasource_success(self):
        """Test successful datasource retrieval."""
        store = InMemoryStore()
        mock_datasource = Mock(spec=SqlDataSource)
        store.put(("datasource",), "main", mock_datasource)

        result = get_datasource_from_store(store)
        assert result is mock_datasource

    def test_get_datasource_not_found(self):
        """Test error when datasource not found."""
        store = InMemoryStore()

        with pytest.raises(ValueError, match="No datasource available in store"):
            get_datasource_from_store(store)


class TestSqlQueryTool:
    """Tests for SqlQueryTool."""

    @pytest.fixture
    def mock_store(self):
        """Create store with mock datasource."""
        store = InMemoryStore()
        mock_datasource = Mock(spec=SqlDataSource)
        mock_datasource.query.return_value = "Query result"
        store.put(("datasource",), "main", mock_datasource)
        return store, mock_datasource

    def test_successful_query(self, mock_store):
        """Test successful SQL query execution."""
        store, mock_datasource = mock_store
        tool = SqlQueryTool()

        result = tool._run(query="SELECT * FROM test", store=store)

        assert isinstance(result, tuple)
        assert len(result) == 2
        content, artifact = result
        assert content == "Query result"

        # Verify artifact encoding
        decoded_result = pickle.loads(base64.b64decode(artifact))
        assert decoded_result == "Query result"

    def test_query_error(self, mock_store):
        """Test handling of query errors."""
        store, mock_datasource = mock_store
        mock_datasource.query.side_effect = Exception("Database error")
        tool = SqlQueryTool()

        result = tool._run(query="SELECT * FROM test", store=store)

        assert isinstance(result, tuple)
        content, artifact = result
        assert "error while executing the query" in content
        assert "Database error" in content
        assert artifact == ""

    def test_no_datasource(self):
        """Test error when no datasource available."""
        store = InMemoryStore()
        tool = SqlQueryTool()

        result = tool._run(query="SELECT * FROM test", store=store)

        assert isinstance(result, tuple)
        content, _ = result
        assert "No datasource available in store" in content


class TestCreateTableTool:
    """Tests for CreateTableTool."""

    @pytest.fixture
    def mock_store(self):
        store = InMemoryStore()
        mock_datasource = Mock(spec=SqlDataSource)
        mock_datasource.query.return_value = "Table created"
        store.put(("datasource",), "main", mock_datasource)
        return store, mock_datasource

    def test_create_table_success(self, mock_store):
        """Test successful table creation."""
        store, mock_datasource = mock_store
        tool = CreateTableTool()

        columns = [
            Column(column_name="id", column_type="INTEGER", primary_key=True),
            Column(column_name="name", column_type="VARCHAR(255)", nullable=False),
        ]

        result = tool._run(store=store, table_name="users", table_columns=columns)

        assert result == "Table created"
        mock_datasource.query.assert_called_once()

    def test_create_table_error(self, mock_store):
        """Test table creation error handling."""
        store, mock_datasource = mock_store
        mock_datasource.query.side_effect = Exception("Table exists")
        tool = CreateTableTool()

        columns = [Column(column_name="id", column_type="INTEGER")]
        result = tool._run(store=store, table_name="test", table_columns=columns)

        assert "Error creating table" in result
        assert "Table exists" in result


class TestQueryPlanTool:
    """Tests for QueryPlanTool."""

    @pytest.fixture
    def mock_store(self):
        store = InMemoryStore()
        mock_datasource = Mock(spec=SqlDataSource)
        mock_datasource.get_query_plan.return_value = "Query plan"
        store.put(("datasource",), "main", mock_datasource)
        return store, mock_datasource

    def test_get_query_plan(self, mock_store):
        """Test query plan retrieval."""
        store, mock_datasource = mock_store
        tool = QueryPlanTool()

        result = tool._run(query="SELECT * FROM test", store=store)

        assert result == "Query plan"
        mock_datasource.get_query_plan.assert_called_once_with("SELECT * FROM test")

    def test_query_plan_error(self, mock_store):
        """Test query plan error handling."""
        store, mock_datasource = mock_store
        mock_datasource.get_query_plan.side_effect = Exception("Plan failed")
        tool = QueryPlanTool()

        result = tool._run(query="SELECT * FROM test", store=store)

        assert "Error getting query plan" in result
        assert "Plan failed" in result


class TestSchemaAnalysisTool:
    """Tests for SchemaAnalysisTool."""

    @pytest.fixture
    def mock_store(self):
        store = InMemoryStore()
        mock_datasource = Mock(spec=SqlDataSource)

        # Create simple mock catalog
        mock_catalog = Mock()
        mock_catalog.catalog_name = "test_catalog"
        mock_catalog.schemas = []

        mock_datasource.get_catalog.return_value = mock_catalog
        store.put(("datasource",), "main", mock_datasource)
        return store, mock_datasource

    def test_analyze_catalog(self, mock_store):
        """Test catalog analysis."""
        store, _ = mock_store
        tool = SchemaAnalysisTool()

        result = tool._run(store=store)

        assert "Catalog Analysis: test_catalog" in result

    def test_schema_analysis_error(self, mock_store):
        """Test schema analysis error handling."""
        store, mock_datasource = mock_store
        mock_datasource.get_catalog.side_effect = Exception("Catalog error")
        tool = SchemaAnalysisTool()

        result = tool._run(store=store)

        assert "Error analyzing schema" in result
        assert "Catalog error" in result


class TestQueryValidationTool:
    """Tests for QueryValidationTool."""

    def test_valid_query(self):
        """Test validation of valid query."""
        tool = QueryValidationTool()
        mock_datasource = Mock(spec=SqlDataSource)

        result = tool._run(
            query="SELECT id, name FROM users WHERE id > 10", datasource=mock_datasource
        )

        assert "Syntax Check: PASS" in result
        assert "Safety Check: PASS" in result

    def test_dangerous_query(self):
        """Test detection of dangerous operations."""
        tool = QueryValidationTool()
        mock_datasource = Mock(spec=SqlDataSource)

        # Test DROP
        result = tool._run(query="DROP TABLE users", datasource=mock_datasource)
        assert "WARNING - DROP operation detected" in result

        # Test DELETE without WHERE
        result = tool._run(query="DELETE FROM users", datasource=mock_datasource)
        assert "WARNING - DELETE without WHERE clause" in result

    def test_invalid_syntax(self):
        """Test syntax validation."""
        tool = QueryValidationTool()
        mock_datasource = Mock(spec=SqlDataSource)

        # Empty query
        result = tool._run(query="", datasource=mock_datasource)
        assert "FAIL - Empty query" in result

        # Invalid query
        result = tool._run(query="INVALID SYNTAX", datasource=mock_datasource)
        assert "FAIL - No valid SQL keywords found" in result


class TestQueryOptimizationTool:
    """Tests for QueryOptimizationTool."""

    def test_optimization_suggestions(self):
        """Test optimization suggestions."""
        tool = QueryOptimizationTool()
        mock_datasource = Mock(spec=SqlDataSource)

        # Test SELECT *
        result = tool._run(query="SELECT * FROM users", datasource=mock_datasource)
        assert "Avoid SELECT *" in result

        # Test good practices
        result = tool._run(
            query="SELECT id, name FROM users WHERE created_at > '2023-01-01' LIMIT 100",
            datasource=mock_datasource,
        )
        assert "Query appears to follow good practices" in result


class TestIntegration:
    """Integration tests for multiple tools."""

    @pytest.fixture
    def complete_setup(self):
        """Setup complete test environment."""
        store = InMemoryStore()
        mock_datasource = Mock(spec=SqlDataSource)

        mock_datasource.query.return_value = "Query result"
        mock_datasource.get_query_plan.return_value = "Plan"
        mock_datasource.get_query_profile.return_value = "Profile"

        store.put(("datasource",), "main", mock_datasource)
        return store, mock_datasource

    def test_multiple_tools(self, complete_setup):
        """Test multiple tools with same datasource."""
        store, mock_datasource = complete_setup

        query_tool = SqlQueryTool()
        plan_tool = QueryPlanTool()
        profile_tool = QueryProfileTool()

        query = "SELECT * FROM test"

        query_result = query_tool._run(query=query, store=store)
        plan_result = plan_tool._run(query=query, store=store)
        profile_result = profile_tool._run(query=query, store=store)

        assert query_result[0] == "Query result"
        assert plan_result == "Plan"
        assert profile_result == "Profile"

    def test_error_propagation(self):
        """Test error handling across tools."""
        store = InMemoryStore()  # Empty store

        tools = [SqlQueryTool(), QueryPlanTool(), SchemaAnalysisTool()]

        for tool in tools:
            if tool.name == "schema_analysis":
                result = tool._run(store=store)
            else:
                result = tool._run(query="SELECT 1", store=store)

            # All should handle missing datasource gracefully
            assert "No datasource available" in str(result) or "Error" in str(result)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
