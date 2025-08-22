#!/usr/bin/env python3
"""
Simplified edge case and failure tests for the InjectedStore system.
"""

from unittest.mock import Mock

import pytest
from langgraph.store.memory import InMemoryStore
from ryoma_ai.datasource.sql import SqlDataSource
from ryoma_ai.tool.sql_tool import Column, CreateTableTool, SqlQueryTool


class TestBasicEdgeCases:
    """Test essential edge cases and error handling."""

    def test_empty_and_long_queries(self):
        """Test handling of edge case query lengths."""
        store = InMemoryStore()
        datasource = Mock(spec=SqlDataSource)
        datasource.query.return_value = "Query executed"
        store.put(("datasource",), "main", datasource)

        tool = SqlQueryTool()

        # Empty query
        result = tool._run(query="", store=store)
        assert isinstance(result, tuple)
        datasource.query.assert_called_with("")

        # Long query
        long_query = (
            "SELECT " + ", ".join([f"col_{i}" for i in range(100)]) + " FROM table"
        )
        result = tool._run(query=long_query, store=store)
        assert isinstance(result, tuple)
        assert result[0] == "Query executed"

    def test_datasource_failures(self):
        """Test handling of datasource failures."""
        store = InMemoryStore()
        failing_ds = Mock(spec=SqlDataSource)
        failing_ds.query.side_effect = ConnectionError("Connection failed")
        store.put(("datasource",), "main", failing_ds)

        tool = SqlQueryTool()
        result = tool._run(query="SELECT 1", store=store)

        assert isinstance(result, tuple)
        assert "error" in result[0].lower()

    def test_unicode_queries(self):
        """Test handling of Unicode characters."""
        store = InMemoryStore()
        datasource = Mock(spec=SqlDataSource)
        datasource.query.return_value = "Unicode handled"
        store.put(("datasource",), "main", datasource)

        tool = SqlQueryTool()

        unicode_queries = [
            "SELECT * FROM café_table WHERE name = 'José'",
            "SELECT * FROM table WHERE data = '🚀💾📊'",
        ]

        for query in unicode_queries:
            result = tool._run(query=query, store=store)
            assert isinstance(result, tuple)
            assert result[0] == "Unicode handled"

    def test_create_table_with_many_columns(self):
        """Test creating tables with many columns."""
        store = InMemoryStore()
        datasource = Mock(spec=SqlDataSource)
        datasource.query.return_value = "Table created"
        store.put(("datasource",), "main", datasource)

        tool = CreateTableTool()
        columns = [
            Column(column_name=f"col_{i}", column_type="VARCHAR(255)", nullable=True)
            for i in range(50)
        ]

        result = tool._run(store=store, table_name="test_table", table_columns=columns)
        assert result == "Table created"


class TestErrorRecovery:
    """Test error recovery scenarios."""

    def test_intermittent_failures(self):
        """Test handling of intermittent datasource failures."""
        store = InMemoryStore()
        datasource = Mock(spec=SqlDataSource)

        # Simulate alternating success/failure
        datasource.query.side_effect = [
            ConnectionError("Fail"),
            "Success 1",
            ConnectionError("Fail"),
            "Success 2",
        ]

        store.put(("datasource",), "main", datasource)
        tool = SqlQueryTool()

        results = []
        for i in range(4):
            result = tool._run(query=f"SELECT {i}", store=store)
            results.append(result)

        # Should handle both failures and successes
        assert len(results) == 4
        assert any("error" in str(r).lower() for r in results)
        assert any("Success" in str(r) for r in results)

    def test_different_error_types(self):
        """Test handling of various error types."""
        store = InMemoryStore()
        datasource = Mock(spec=SqlDataSource)

        error_types = [
            ConnectionError("Connection lost"),
            RuntimeError("Runtime error"),
            ValueError("Invalid value"),
            TimeoutError("Timeout"),
        ]

        tool = SqlQueryTool()

        for error in error_types:
            datasource.query.side_effect = error
            store.put(("datasource",), "main", datasource)

            result = tool._run(query="SELECT 1", store=store)
            assert isinstance(result, tuple)
            assert "error" in result[0].lower()


class TestMockEdgeCases:
    """Test edge cases with mock objects."""

    def test_mock_return_types(self):
        """Test handling of unexpected return types from mocks."""
        store = InMemoryStore()
        datasource = Mock(spec=SqlDataSource)
        store.put(("datasource",), "main", datasource)

        tool = SqlQueryTool()

        # Test different return types
        return_values = ["string", 123, ["list", "data"], {"dict": "data"}, None]

        for value in return_values:
            datasource.query.return_value = value
            result = tool._run(query="SELECT 1", store=store)
            assert isinstance(result, tuple)
            # Should handle any return type gracefully
            assert str(value) in str(result[0])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
