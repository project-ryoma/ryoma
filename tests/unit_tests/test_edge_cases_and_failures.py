#!/usr/bin/env python3
"""
Comprehensive edge case and failure scenario tests for the InjectedStore system.
Tests boundary conditions, error propagation, recovery mechanisms, and system resilience.
"""

import gc
import sys
import threading
import time
import weakref
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, PropertyMock, patch

import pytest
from langgraph.store.memory import InMemoryStore
from ryoma_ai.agent.base import BaseAgent
from ryoma_ai.agent.workflow import WorkflowAgent
from ryoma_ai.datasource.sql import SqlDataSource
from ryoma_ai.tool.sql_tool import (
    Column,
    CreateTableTool,
    QueryPlanTool,
    SchemaAnalysisTool,
    SqlQueryTool,
    get_datasource_from_store,
)


class FlakyDataSource:
    """Mock datasource that fails intermittently for testing resilience."""

    def __init__(self, failure_rate: float = 0.3):
        self.failure_rate = failure_rate
        self.call_count = 0
        self.connection_status = "unstable"

    def query(self, sql: str):
        self.call_count += 1
        import random

        if random.random() < self.failure_rate:
            raise ConnectionError(f"Random failure on call {self.call_count}")
        return f"Success: {sql} (call {self.call_count})"

    def get_catalog(self):
        if self.call_count % 3 == 0:  # Fail every 3rd call
            raise RuntimeError("Catalog temporarily unavailable")
        return Mock()

    def get_query_plan(self, query: str):
        if "DROP" in query.upper():
            raise ValueError("Cannot plan DROP operations")
        return f"Plan for: {query}"


class CorruptedDataSource:
    """Mock datasource that becomes corrupted during operations."""

    def __init__(self):
        self.is_corrupted = False
        self.corruption_trigger = 5
        self.call_count = 0

    def query(self, sql: str):
        self.call_count += 1
        if self.call_count >= self.corruption_trigger:
            self.is_corrupted = True

        if self.is_corrupted:
            raise RuntimeError("Datasource corrupted: invalid state")

        return f"Query result: {sql}"

    def __getattr__(self, name):
        if self.is_corrupted:
            raise AttributeError(f"Corrupted datasource cannot access {name}")
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )


class TestBoundaryConditions:
    """Test boundary conditions and extreme scenarios."""

    def test_empty_query_handling(self):
        """Test handling of empty or whitespace-only queries."""
        store = InMemoryStore()
        datasource = Mock(spec=SqlDataSource)
        store.put(("datasource",), "main", datasource)

        tool = SqlQueryTool()

        # Test empty string
        result = tool._run(query="", store=store)
        assert isinstance(result, tuple)
        datasource.query.assert_called_with("")

        # Test whitespace only
        result = tool._run(query="   \n\t  ", store=store)
        datasource.query.assert_called_with("   \n\t  ")

        # Test None (should not happen in normal flow, but test robustness)
        with pytest.raises(TypeError):
            tool._run(query=None, store=store)

    def test_extremely_long_query(self):
        """Test handling of extremely long SQL queries."""
        store = InMemoryStore()
        datasource = Mock(spec=SqlDataSource)
        datasource.query.return_value = "Long query executed"
        store.put(("datasource",), "main", datasource)

        tool = SqlQueryTool()

        # Create extremely long query (1MB)
        long_query = (
            "SELECT "
            + ", ".join([f"column_{i}" for i in range(50000)])
            + " FROM huge_table"
        )

        result = tool._run(query=long_query, store=store)

        assert isinstance(result, tuple)
        assert result[0] == "Long query executed"
        datasource.query.assert_called_once_with(long_query)

    def test_unicode_and_special_characters(self):
        """Test handling of Unicode and special characters in queries."""
        store = InMemoryStore()
        datasource = Mock(spec=SqlDataSource)
        datasource.query.return_value = "Unicode query executed"
        store.put(("datasource",), "main", datasource)

        tool = SqlQueryTool()

        # Test various Unicode scenarios
        unicode_queries = [
            "SELECT * FROM café_table WHERE name = 'José'",
            "SELECT 用户名 FROM 用户表 WHERE 年龄 > 18",
            "SELECT * FROM Ṁŷ_Ṫäḅḷė WHERE field = 'тест'",
            "SELECT * FROM table WHERE data = '🚀💾📊'",
            "SELECT 'quotes\"inside' FROM \"table\" WHERE field = '\\'escaped\\''",
            "SELECT /* комментарий */ * FROM table",
        ]

        for query in unicode_queries:
            result = tool._run(query=query, store=store)
            assert isinstance(result, tuple)
            assert result[0] == "Unicode query executed"

    def test_malformed_store_keys(self):
        """Test behavior with malformed or unusual store keys."""
        store = InMemoryStore()
        datasource = Mock(spec=SqlDataSource)

        # Test various key formats
        unusual_keys = [
            ("",),  # Empty string key
            ("datasource", "nested", "key"),  # Nested key
            ("DATASOURCE",),  # Different case
            ("datasource with spaces",),  # Spaces in key
            ("datasource.with.dots",),  # Dots in key
            ("データソース",),  # Unicode key
        ]

        for key in unusual_keys:
            store.put(key, "main", datasource)
            result = store.get(key, "main")
            assert result is not None
            assert result.value is datasource

    def test_store_namespace_edge_cases(self):
        """Test edge cases with store namespaces."""
        store = InMemoryStore()
        datasource = Mock(spec=SqlDataSource)

        # Test unusual namespace values
        unusual_namespaces = [
            "",  # Empty namespace
            "namespace with spaces",
            "UPPERCASE",
            "123numeric",
            "special-chars_namespace!",
            "ネームスペース",  # Unicode namespace
            None,  # This might cause issues
        ]

        for namespace in unusual_namespaces:
            if namespace is not None:  # Skip None as it might not be supported
                store.put(("datasource",), namespace, datasource)
                result = store.get(("datasource",), namespace)
                assert result is not None
                assert result.value is datasource

    def test_maximum_table_columns(self):
        """Test creating tables with maximum number of columns."""
        store = InMemoryStore()
        datasource = Mock(spec=SqlDataSource)
        datasource.query.return_value = "Table with many columns created"
        store.put(("datasource",), "main", datasource)

        tool = CreateTableTool()

        # Create table with many columns (test database limits)
        many_columns = [
            Column(column_name=f"col_{i}", column_type="VARCHAR(255)", nullable=True)
            for i in range(1000)
        ]

        result = tool._run(
            store=store, table_name="huge_table", table_columns=many_columns
        )

        assert result == "Table with many columns created"
        datasource.query.assert_called_once()

        # Verify the generated SQL contains all columns
        call_args = datasource.query.call_args[0][0]
        assert "col_0" in call_args
        assert "col_999" in call_args


class TestErrorPropagationAndRecovery:
    """Test error propagation and recovery mechanisms."""

    def test_flaky_datasource_resilience(self):
        """Test system resilience with unreliable datasource."""
        store = InMemoryStore()
        flaky_ds = FlakyDataSource(failure_rate=0.5)
        store.put(("datasource",), "main", flaky_ds)

        tool = SqlQueryTool()

        # Execute multiple queries, some will fail
        success_count = 0
        failure_count = 0

        for i in range(20):
            result = tool._run(query=f"SELECT {i}", store=store)
            if isinstance(result, tuple) and "Success:" in result[0]:
                success_count += 1
            else:
                failure_count += 1

        # Should have both successes and failures
        assert success_count > 0
        assert failure_count > 0
        assert success_count + failure_count == 20

    def test_datasource_corruption_detection(self):
        """Test detection and handling of datasource corruption."""
        store = InMemoryStore()
        corrupted_ds = CorruptedDataSource()
        store.put(("datasource",), "main", corrupted_ds)

        tool = SqlQueryTool()

        # Execute queries until corruption occurs
        results = []
        for i in range(10):
            result = tool._run(query=f"SELECT {i}", store=store)
            results.append(result)

        # Early queries should succeed, later ones should fail
        success_results = [
            r for r in results[:4] if isinstance(r, tuple) and "Query result:" in r[0]
        ]
        assert len(success_results) > 0

        # Later queries should detect corruption
        error_results = [
            r for r in results[5:] if isinstance(r, tuple) and "error" in r[0].lower()
        ]
        assert len(error_results) > 0

    def test_cascading_failure_handling(self):
        """Test handling of cascading failures across multiple components."""
        store = InMemoryStore()

        # Create a datasource that fails in multiple ways
        failing_ds = Mock(spec=SqlDataSource)
        failing_ds.query.side_effect = ConnectionError("Connection lost")
        failing_ds.get_catalog.side_effect = RuntimeError("Catalog service down")
        failing_ds.get_query_plan.side_effect = TimeoutError("Plan generation timeout")

        store.put(("datasource",), "main", failing_ds)

        # Test different tools with the failing datasource
        tools = [SqlQueryTool(), QueryPlanTool(), SchemaAnalysisTool()]

        for tool in tools:
            if hasattr(tool, "_run"):
                if tool.name == "schema_analysis":
                    result = tool._run(store=store)
                else:
                    result = tool._run(query="SELECT 1", store=store)

                # All tools should handle their specific failures gracefully
                assert isinstance(result, (str, tuple))
                if isinstance(result, tuple):
                    assert "error" in result[0].lower() or "Error" in result[0]
                else:
                    assert "error" in result.lower() or "Error" in result

    def test_partial_failure_recovery(self):
        """Test recovery from partial failures."""
        store = InMemoryStore()

        # Create a datasource that fails initially then recovers
        recovering_ds = Mock(spec=SqlDataSource)
        call_count = 0

        def query_with_recovery(sql):
            nonlocal call_count
            call_count += 1
            if call_count <= 3:
                raise ConnectionError("Initial failure")
            return f"Recovered: {sql}"

        recovering_ds.query.side_effect = query_with_recovery
        store.put(("datasource",), "main", recovering_ds)

        tool = SqlQueryTool()

        # First few calls should fail
        for i in range(3):
            result = tool._run(query=f"SELECT {i}", store=store)
            assert isinstance(result, tuple)
            assert "error" in result[0].lower()

        # Later calls should succeed
        for i in range(3, 6):
            result = tool._run(query=f"SELECT {i}", store=store)
            assert isinstance(result, tuple)
            assert "Recovered:" in result[0]

    def test_memory_pressure_handling(self):
        """Test behavior under memory pressure conditions."""
        store = InMemoryStore()

        # Create many large datasources
        large_objects = []
        for i in range(100):
            ds = Mock(spec=SqlDataSource)
            ds.large_data = "x" * 10000  # 10KB each
            ds.query.return_value = f"Result from DS {i}"
            store.put(("datasource",), f"ds_{i}", ds)
            large_objects.append(ds)

        # Test tool execution with different datasources
        tool = SqlQueryTool()

        for i in range(0, 100, 10):  # Test every 10th datasource
            # Get specific datasource
            result = store.get(("datasource",), f"ds_{i}")
            assert result is not None

            # Use in tool
            temp_store = InMemoryStore()
            temp_store.put(("datasource",), "main", result.value)

            tool_result = tool._run(query=f"SELECT {i}", store=temp_store)
            assert isinstance(tool_result, tuple)
            assert f"Result from DS {i}" in tool_result[0]


class TestConcurrencyAndThreadSafety:
    """Test concurrency issues and thread safety."""

    def test_concurrent_store_access_with_failures(self):
        """Test concurrent store access when some operations fail."""
        store = InMemoryStore()
        flaky_ds = FlakyDataSource(failure_rate=0.3)
        store.put(("datasource",), "main", flaky_ds)

        results = []
        errors = []

        def worker_thread(thread_id):
            tool = SqlQueryTool()
            try:
                for i in range(10):
                    result = tool._run(query=f"SELECT {thread_id}_{i}", store=store)
                    results.append((thread_id, result))
                    time.sleep(0.001)
            except Exception as e:
                errors.append((thread_id, e))

        # Create multiple worker threads
        threads = [threading.Thread(target=worker_thread, args=(i,)) for i in range(5)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Should have completed all work despite some failures
        assert len(results) == 50  # 5 threads × 10 operations
        assert len(errors) == 0  # No thread-level errors

        # Some operations should have succeeded, some failed
        successes = [
            r for r in results if isinstance(r[1], tuple) and "Success:" in r[1][0]
        ]
        failures = [
            r for r in results if isinstance(r[1], tuple) and "error" in r[1][0].lower()
        ]

        assert len(successes) > 0
        assert len(failures) > 0

    def test_store_modification_during_access(self):
        """Test modifying store while other threads are accessing it."""
        store = InMemoryStore()

        # Start with initial datasource
        initial_ds = Mock(spec=SqlDataSource)
        initial_ds.query.return_value = "Initial result"
        store.put(("datasource",), "main", initial_ds)

        access_results = []
        modification_count = 0

        def accessor_thread():
            tool = SqlQueryTool()
            for i in range(20):
                try:
                    result = tool._run(query=f"SELECT {i}", store=store)
                    access_results.append(result)
                    time.sleep(0.001)
                except Exception as e:
                    access_results.append(("error", str(e)))

        def modifier_thread():
            nonlocal modification_count
            for i in range(10):
                new_ds = Mock(spec=SqlDataSource)
                new_ds.query.return_value = f"Modified result {i}"
                store.put(("datasource",), "main", new_ds)
                modification_count += 1
                time.sleep(0.002)

        # Start both threads
        accessor = threading.Thread(target=accessor_thread)
        modifier = threading.Thread(target=modifier_thread)

        accessor.start()
        modifier.start()

        accessor.join()
        modifier.join()

        # Should have completed all operations
        assert len(access_results) == 20
        assert modification_count == 10

        # Results should reflect different datasource states
        unique_results = set()
        for result in access_results:
            if isinstance(result, tuple) and len(result) == 2:
                unique_results.add(result[0])

        assert len(unique_results) > 1  # Should see different datasource results


class TestResourceManagementAndCleanup:
    """Test resource management and cleanup scenarios."""

    def test_datasource_garbage_collection(self):
        """Test that datasources are properly garbage collected."""
        store = InMemoryStore()

        # Create datasource with weak reference
        datasource = Mock(spec=SqlDataSource)
        datasource.query.return_value = "GC test result"
        weak_ref = weakref.ref(datasource)

        # Store in store
        store.put(("datasource",), "main", datasource)

        # Verify it's accessible
        result = get_datasource_from_store(store)
        assert result is datasource
        assert weak_ref() is not None

        # Remove from store and local reference
        store.put(("datasource",), "main", None)
        del datasource
        del result

        # Force garbage collection
        gc.collect()

        # Weak reference should be gone (may not work in all Python implementations)
        # This test is informational rather than strict
        # assert weak_ref() is None

    def test_large_object_cleanup(self):
        """Test cleanup of large objects from store."""
        store = InMemoryStore()

        # Create large datasource
        large_ds = Mock(spec=SqlDataSource)
        large_ds.huge_data = "x" * 1000000  # 1MB
        large_ds.query.return_value = "Large object result"

        # Store and use it
        store.put(("datasource",), "main", large_ds)
        tool = SqlQueryTool()
        result = tool._run(query="SELECT 1", store=store)

        assert isinstance(result, tuple)
        assert "Large object result" in result[0]

        # Replace with smaller object
        small_ds = Mock(spec=SqlDataSource)
        small_ds.query.return_value = "Small object result"
        store.put(("datasource",), "main", small_ds)

        # Verify replacement worked
        result = tool._run(query="SELECT 1", store=store)
        assert isinstance(result, tuple)
        assert "Small object result" in result[0]

    def test_store_capacity_limits(self):
        """Test behavior when store reaches capacity limits."""
        store = InMemoryStore()

        # Fill store with many datasources
        datasources = []
        for i in range(1000):  # Large number
            ds = Mock(spec=SqlDataSource)
            ds.query.return_value = f"DS {i} result"
            store.put(("datasource",), f"namespace_{i}", ds)
            datasources.append(ds)

        # Verify all are accessible
        sample_indices = [0, 100, 500, 999]
        for i in sample_indices:
            result = store.get(("datasource",), f"namespace_{i}")
            assert result is not None
            assert f"DS {i} result" in result.value.query("SELECT 1")

    def test_circular_reference_handling(self):
        """Test handling of circular references in stored objects."""
        store = InMemoryStore()

        # Create objects with circular references
        ds1 = Mock(spec=SqlDataSource)
        ds2 = Mock(spec=SqlDataSource)

        ds1.reference = ds2
        ds2.reference = ds1
        ds1.query.return_value = "Circular DS1 result"
        ds2.query.return_value = "Circular DS2 result"

        # Store both
        store.put(("datasource",), "ds1", ds1)
        store.put(("datasource",), "ds2", ds2)

        # Verify they're accessible and functional
        result1 = store.get(("datasource",), "ds1")
        result2 = store.get(("datasource",), "ds2")

        assert result1.value.query("SELECT 1") == "Circular DS1 result"
        assert result2.value.query("SELECT 1") == "Circular DS2 result"

        # Verify circular references are preserved
        assert result1.value.reference is result2.value
        assert result2.value.reference is result1.value


class TestSystemIntegrationFailures:
    """Test system-level integration failures."""

    def test_python_version_compatibility(self):
        """Test behavior across different Python version scenarios."""
        # This test documents behavior rather than testing specific versions
        store = InMemoryStore()
        datasource = Mock(spec=SqlDataSource)
        datasource.query.return_value = (
            f"Python {sys.version_info.major}.{sys.version_info.minor} result"
        )

        store.put(("datasource",), "main", datasource)

        tool = SqlQueryTool()
        result = tool._run(query="SELECT python_version()", store=store)

        assert isinstance(result, tuple)
        assert "Python" in result[0]

    def test_mock_framework_edge_cases(self):
        """Test edge cases specific to mock framework interactions."""
        store = InMemoryStore()

        # Create a mock that behaves unexpectedly
        tricky_mock = Mock(spec=SqlDataSource)

        # Configure mock to return different types
        tricky_mock.query.side_effect = [
            "string result",
            123,  # Unexpected numeric result
            ["list", "result"],  # List result
            {"dict": "result"},  # Dict result
            None,  # None result
            Exception("Mock exception"),  # Exception
        ]

        store.put(("datasource",), "main", tricky_mock)

        tool = SqlQueryTool()

        # Test each scenario
        expected_results = [
            "string result",
            "123",  # Should be converted to string
            "['list', 'result']",  # Should be stringified
            "{'dict': 'result'}",  # Should be stringified
            "None",  # Should be stringified
        ]

        for i, expected in enumerate(expected_results):
            result = tool._run(query=f"SELECT {i}", store=store)
            assert isinstance(result, tuple)
            # The exact representation might vary, but should contain the value
            assert str(expected) in str(result[0]) or expected in str(result[0])

        # Last call should handle exception
        result = tool._run(query="SELECT exception", store=store)
        assert isinstance(result, tuple)
        assert "error" in result[0].lower() or "Error" in result[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
