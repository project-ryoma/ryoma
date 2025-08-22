#!/usr/bin/env python3
"""
Comprehensive test suite for SQL tools with InjectedStore implementation.
Tests all SQL tools, error handling, edge cases, and integration scenarios.
"""

import base64
import pickle
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest
from langgraph.store.memory import InMemoryStore
from ryoma_ai.datasource.sql import SqlDataSource
from ryoma_ai.tool.sql_tool import (
    Column,
    CreateTableTool,
    QueryExplanationTool,
    QueryOptimizationTool,
    QueryPlanTool,
    QueryProfileTool,
    QueryValidationTool,
    SchemaAnalysisTool,
    SqlQueryTool,
    TableSelectionTool,
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
        """Test error when datasource not found in store."""
        store = InMemoryStore()

        with pytest.raises(ValueError, match="No datasource available in store"):
            get_datasource_from_store(store)

    def test_get_datasource_store_error(self):
        """Test error handling when store access fails."""
        store = Mock()
        store.get.side_effect = Exception("Store access failed")

        with pytest.raises(Exception, match="Store access failed"):
            get_datasource_from_store(store)


class TestSqlQueryTool:
    """Comprehensive tests for SqlQueryTool."""

    @pytest.fixture
    def mock_store_with_datasource(self):
        """Create a store with mock datasource."""
        store = InMemoryStore()
        mock_datasource = Mock(spec=SqlDataSource)
        mock_datasource.query.return_value = "SELECT result"
        store.put(("datasource",), "main", mock_datasource)
        return store, mock_datasource

    def test_successful_query_execution(self, mock_store_with_datasource):
        """Test successful SQL query execution."""
        store, mock_datasource = mock_store_with_datasource
        tool = SqlQueryTool()

        result = tool._run(query="SELECT * FROM test", store=store)

        assert isinstance(result, tuple)
        assert len(result) == 2
        content, artifact = result
        assert content == "SELECT result"

        # Verify artifact is properly encoded
        decoded_result = pickle.loads(base64.b64decode(artifact))
        assert decoded_result == "SELECT result"

        mock_datasource.query.assert_called_once_with("SELECT * FROM test")

    def test_query_execution_with_datasource_error(self, mock_store_with_datasource):
        """Test handling of datasource query errors."""
        store, mock_datasource = mock_store_with_datasource
        mock_datasource.query.side_effect = Exception("Database connection failed")
        tool = SqlQueryTool()

        result = tool._run(query="SELECT * FROM test", store=store)

        assert isinstance(result, tuple)
        content, artifact = result
        assert (
            "Received an error while executing the query: Database connection failed"
            in content
        )
        assert artifact == ""

    def test_query_execution_no_datasource(self):
        """Test error when no datasource in store."""
        store = InMemoryStore()
        tool = SqlQueryTool()

        result = tool._run(query="SELECT * FROM test", store=store)

        assert isinstance(result, tuple)
        content, artifact = result
        assert (
            "Received an error while executing the query: No datasource available in store"
            in content
        )
        assert artifact == ""

    def test_query_tool_schema(self):
        """Test tool schema and metadata."""
        tool = SqlQueryTool()

        assert tool.name == "sql_database_query"
        assert "Execute a SQL query" in tool.description
        assert tool.response_format == "content_and_artifact"
        assert tool.args_schema is not None


class TestCreateTableTool:
    """Tests for CreateTableTool."""

    @pytest.fixture
    def mock_store_with_datasource(self):
        store = InMemoryStore()
        mock_datasource = Mock(spec=SqlDataSource)
        mock_datasource.query.return_value = "CREATE TABLE success"
        store.put(("datasource",), "main", mock_datasource)
        return store, mock_datasource

    @pytest.fixture
    def sample_columns(self):
        return [
            Column(column_name="id", column_type="INTEGER", primary_key=True),
            Column(column_name="name", column_type="VARCHAR(255)", nullable=False),
            Column(column_name="email", column_type="VARCHAR(255)", nullable=True),
        ]

    def test_successful_table_creation(
        self, mock_store_with_datasource, sample_columns
    ):
        """Test successful table creation."""
        store, mock_datasource = mock_store_with_datasource
        tool = CreateTableTool()

        result = tool._run(
            store=store, table_name="users", table_columns=sample_columns
        )

        assert result == "CREATE TABLE success"
        mock_datasource.query.assert_called_once()

        # Verify the SQL structure is correct
        call_args = mock_datasource.query.call_args[0][0]
        assert "CREATE TABLE users" in call_args
        assert "id" in call_args
        assert "name" in call_args
        assert "email" in call_args

    def test_table_creation_error(self, mock_store_with_datasource, sample_columns):
        """Test error handling in table creation."""
        store, mock_datasource = mock_store_with_datasource
        mock_datasource.query.side_effect = Exception("Table already exists")
        tool = CreateTableTool()

        result = tool._run(
            store=store, table_name="users", table_columns=sample_columns
        )

        assert "Error creating table: Table already exists" in result


class TestQueryPlanTool:
    """Tests for QueryPlanTool."""

    @pytest.fixture
    def mock_store_with_datasource(self):
        store = InMemoryStore()
        mock_datasource = Mock(spec=SqlDataSource)
        mock_datasource.get_query_plan.return_value = "Query plan details"
        store.put(("datasource",), "main", mock_datasource)
        return store, mock_datasource

    def test_successful_query_plan(self, mock_store_with_datasource):
        """Test successful query plan retrieval."""
        store, mock_datasource = mock_store_with_datasource
        tool = QueryPlanTool()

        result = tool._run(query="SELECT * FROM test", store=store)

        assert result == "Query plan details"
        mock_datasource.get_query_plan.assert_called_once_with("SELECT * FROM test")

    def test_query_plan_error(self, mock_store_with_datasource):
        """Test error handling in query plan."""
        store, mock_datasource = mock_store_with_datasource
        mock_datasource.get_query_plan.side_effect = Exception("Plan generation failed")
        tool = QueryPlanTool()

        result = tool._run(query="SELECT * FROM test", store=store)

        assert "Error getting query plan: Plan generation failed" in result


class TestQueryProfileTool:
    """Tests for QueryProfileTool."""

    @pytest.fixture
    def mock_store_with_datasource(self):
        store = InMemoryStore()
        mock_datasource = Mock(spec=SqlDataSource)
        mock_datasource.get_query_profile.return_value = "Query profile details"
        store.put(("datasource",), "main", mock_datasource)
        return store, mock_datasource

    def test_successful_query_profile(self, mock_store_with_datasource):
        """Test successful query profile retrieval."""
        store, mock_datasource = mock_store_with_datasource
        tool = QueryProfileTool()

        result = tool._run(query="SELECT * FROM test", store=store)

        assert result == "Query profile details"
        mock_datasource.get_query_profile.assert_called_once_with("SELECT * FROM test")

    def test_query_profile_error(self, mock_store_with_datasource):
        """Test error handling in query profile."""
        store, mock_datasource = mock_store_with_datasource
        mock_datasource.get_query_profile.side_effect = Exception(
            "Profile generation failed"
        )
        tool = QueryProfileTool()

        result = tool._run(query="SELECT * FROM test", store=store)

        assert "Error getting query profile: Profile generation failed" in result


class TestSchemaAnalysisTool:
    """Tests for SchemaAnalysisTool."""

    @pytest.fixture
    def mock_catalog(self):
        """Create a mock catalog structure."""
        mock_catalog = Mock()
        mock_catalog.catalog_name = "test_catalog"

        # Mock schema
        mock_schema = Mock()
        mock_schema.schema_name = "test_schema"

        # Mock table
        mock_table = Mock()
        mock_table.table_name = "test_table"

        # Mock columns
        mock_column1 = Mock()
        mock_column1.name = "id"
        mock_column1.type = "INTEGER"
        mock_column1.nullable = False

        mock_column2 = Mock()
        mock_column2.name = "name"
        mock_column2.type = "VARCHAR"
        mock_column2.nullable = True

        mock_table.columns = [mock_column1, mock_column2]
        mock_schema.tables = [mock_table]
        mock_catalog.schemas = [mock_schema]

        return mock_catalog

    @pytest.fixture
    def mock_store_with_datasource(self, mock_catalog):
        store = InMemoryStore()
        mock_datasource = Mock(spec=SqlDataSource)
        mock_datasource.get_catalog.return_value = mock_catalog
        store.put(("datasource",), "main", mock_datasource)
        return store, mock_datasource

    def test_analyze_full_catalog(self, mock_store_with_datasource):
        """Test full catalog analysis."""
        store, mock_datasource = mock_store_with_datasource
        tool = SchemaAnalysisTool()

        result = tool._run(store=store)

        assert "Catalog Analysis: test_catalog" in result
        assert "Schemas: 1, Total Tables: 1" in result
        assert "Schema: test_schema (1 tables)" in result

    def test_analyze_specific_schema(self, mock_store_with_datasource):
        """Test specific schema analysis."""
        store, mock_datasource = mock_store_with_datasource
        tool = SchemaAnalysisTool()

        result = tool._run(store=store, schema_name="test_schema")

        assert "Schema Analysis: test_schema" in result
        assert "Tables (1):" in result
        assert "test_table (2 columns)" in result

    def test_analyze_specific_table(self, mock_store_with_datasource):
        """Test specific table analysis."""
        store, mock_datasource = mock_store_with_datasource
        tool = SchemaAnalysisTool()

        result = tool._run(
            store=store, table_name="test_table", schema_name="test_schema"
        )

        assert "Table Analysis: test_table" in result
        assert "Columns (2):" in result
        assert "id: INTEGER (NOT NULL)" in result
        assert "name: VARCHAR" in result

    def test_schema_analysis_error(self, mock_store_with_datasource):
        """Test error handling in schema analysis."""
        store, mock_datasource = mock_store_with_datasource
        mock_datasource.get_catalog.side_effect = Exception("Catalog access failed")
        tool = SchemaAnalysisTool()

        result = tool._run(store=store)

        assert "Error analyzing schema: Catalog access failed" in result


class TestQueryValidationTool:
    """Tests for QueryValidationTool."""

    def test_valid_select_query(self):
        """Test validation of a valid SELECT query."""
        tool = QueryValidationTool()

        # Mock datasource (not used in validation logic)
        mock_datasource = Mock(spec=SqlDataSource)

        result = tool._run(
            query="SELECT id, name FROM users WHERE id > 10", datasource=mock_datasource
        )

        assert "Syntax Check: PASS" in result
        assert "Safety Check: PASS" in result

    def test_dangerous_query_detection(self):
        """Test detection of dangerous operations."""
        tool = QueryValidationTool()
        mock_datasource = Mock(spec=SqlDataSource)

        # Test DROP operation
        result = tool._run(query="DROP TABLE users", datasource=mock_datasource)
        assert "WARNING - DROP operation detected" in result

        # Test DELETE without WHERE
        result = tool._run(query="DELETE FROM users", datasource=mock_datasource)
        assert "WARNING - DELETE without WHERE clause" in result

        # Test UPDATE without WHERE
        result = tool._run(
            query="UPDATE users SET name = 'test'", datasource=mock_datasource
        )
        assert "WARNING - UPDATE without WHERE clause" in result

    def test_syntax_validation(self):
        """Test syntax validation."""
        tool = QueryValidationTool()
        mock_datasource = Mock(spec=SqlDataSource)

        # Test empty query
        result = tool._run(query="", datasource=mock_datasource)
        assert "FAIL - Empty query" in result

        # Test unbalanced parentheses
        result = tool._run(query="SELECT (id FROM users", datasource=mock_datasource)
        assert "FAIL - Unbalanced parentheses" in result

        # Test invalid query
        result = tool._run(query="INVALID QUERY", datasource=mock_datasource)
        assert "FAIL - No valid SQL keywords found" in result


class TestQueryOptimizationTool:
    """Tests for QueryOptimizationTool."""

    def test_optimization_suggestions(self):
        """Test optimization suggestions for various query patterns."""
        tool = QueryOptimizationTool()
        mock_datasource = Mock(spec=SqlDataSource)

        # Test SELECT *
        result = tool._run(query="SELECT * FROM users", datasource=mock_datasource)
        assert "Avoid SELECT *" in result

        # Test DELETE without WHERE
        result = tool._run(query="DELETE FROM users", datasource=mock_datasource)
        assert "Add WHERE clause" in result

        # Test LIKE with leading wildcard
        result = tool._run(
            query="SELECT * FROM users WHERE name LIKE '%john'",
            datasource=mock_datasource,
        )
        assert "Avoid LIKE patterns starting with %" in result

        # Test subquery
        result = tool._run(
            query="SELECT * FROM users WHERE id IN (SELECT user_id FROM orders)",
            datasource=mock_datasource,
        )
        assert "Consider replacing IN (SELECT...)" in result

    def test_good_query_practices(self):
        """Test recognition of good query practices."""
        tool = QueryOptimizationTool()
        mock_datasource = Mock(spec=SqlDataSource)

        result = tool._run(
            query="SELECT id, name FROM users WHERE created_at > '2023-01-01' LIMIT 100",
            datasource=mock_datasource,
        )
        assert "Query appears to follow good practices" in result


class TestIntegrationScenarios:
    """Integration tests combining multiple components."""

    @pytest.fixture
    def complete_setup(self):
        """Set up a complete test environment."""
        store = InMemoryStore()
        mock_datasource = Mock(spec=SqlDataSource)

        # Configure mock responses
        mock_datasource.query.return_value = "Query executed successfully"
        mock_datasource.get_query_plan.return_value = "Execution plan"
        mock_datasource.get_query_profile.return_value = "Performance profile"

        # Mock catalog
        mock_catalog = Mock()
        mock_catalog.catalog_name = "integration_catalog"
        mock_catalog.schemas = []
        mock_datasource.get_catalog.return_value = mock_catalog

        store.put(("datasource",), "main", mock_datasource)
        return store, mock_datasource

    def test_multiple_tools_same_datasource(self, complete_setup):
        """Test multiple tools using the same datasource."""
        store, mock_datasource = complete_setup

        # Test multiple tools
        query_tool = SqlQueryTool()
        plan_tool = QueryPlanTool()
        profile_tool = QueryProfileTool()

        query = "SELECT * FROM test_table"

        # Execute all tools
        query_result = query_tool._run(query=query, store=store)
        plan_result = plan_tool._run(query=query, store=store)
        profile_result = profile_tool._run(query=query, store=store)

        # Verify all tools worked
        assert query_result[0] == "Query executed successfully"
        assert plan_result == "Execution plan"
        assert profile_result == "Performance profile"

        # Verify datasource was accessed correctly
        assert mock_datasource.query.call_count == 1
        assert mock_datasource.get_query_plan.call_count == 1
        assert mock_datasource.get_query_profile.call_count == 1

    def test_error_propagation_across_tools(self):
        """Test error propagation across different tools."""
        store = InMemoryStore()
        # No datasource in store

        tools = [
            SqlQueryTool(),
            QueryPlanTool(),
            QueryProfileTool(),
            SchemaAnalysisTool(),
        ]

        for tool in tools:
            if hasattr(tool, "_run"):
                if tool.name == "schema_analysis":
                    result = tool._run(store=store)
                else:
                    result = tool._run(query="SELECT 1", store=store)

                # All tools should handle the missing datasource gracefully
                assert "No datasource available" in str(result) or "Error" in str(
                    result
                )


class TestEdgeCasesAndFailures:
    """Test edge cases and failure scenarios."""

    def test_store_corruption_handling(self):
        """Test handling of corrupted store data."""
        store = InMemoryStore()
        # Put invalid data in store
        store.put(("datasource",), "main", "invalid_datasource_object")

        tool = SqlQueryTool()
        result = tool._run(query="SELECT 1", store=store)

        # Should handle gracefully
        assert isinstance(result, tuple)
        assert "error" in result[0].lower()

    def test_concurrent_store_access(self, complete_setup):
        """Test concurrent access to the same store."""
        import threading
        import time

        store, mock_datasource = complete_setup
        results = []
        errors = []

        def run_tool():
            try:
                tool = SqlQueryTool()
                result = tool._run(query="SELECT 1", store=store)
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Create multiple threads
        threads = [threading.Thread(target=run_tool) for _ in range(5)]

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # Verify results
        assert len(results) == 5
        assert len(errors) == 0
        for result in results:
            assert result[0] == "Query executed successfully"

    def test_large_query_handling(self, complete_setup):
        """Test handling of large queries."""
        store, mock_datasource = complete_setup
        tool = SqlQueryTool()

        # Create a very large query
        large_query = (
            "SELECT "
            + ", ".join([f"col_{i}" for i in range(1000)])
            + " FROM large_table"
        )

        result = tool._run(query=large_query, store=store)

        assert result[0] == "Query executed successfully"
        mock_datasource.query.assert_called_once_with(large_query)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
