#!/usr/bin/env python3
"""
Comprehensive tests for store functionality and error handling in the InjectedStore system.
Tests store operations, error scenarios, data persistence, and recovery mechanisms.
"""

import threading
import time
from unittest.mock import Mock

import pytest
from langchain_core.stores import InMemoryStore
from ryoma_ai.agent.base import BaseAgent
from ryoma_ai.domain.constants import StoreKeys
from ryoma_ai.tool.sql_tool import get_datasource_from_store
from ryoma_data.sql import SqlDataSource


class MockSqlDataSource:
    """Mock SQL datasource for testing store functionality."""

    def __init__(self, name: str = "test_datasource"):
        self.name = name
        self.connection_status = "connected"
        self.query_count = 0

    def query(self, sql: str):
        self.query_count += 1
        return f"Result for: {sql}"

    def get_catalog(self):
        return Mock()

    def __str__(self):
        return f"MockSqlDataSource({self.name})"

    def __repr__(self):
        return self.__str__()


class TestStoreBasicOperations:
    """Test basic store operations and functionality."""

    def test_store_put_and_get_success(self):
        """Test successful put and get operations."""
        store = InMemoryStore()
        datasource = MockSqlDataSource("test_db")

        # Put datasource in store using new constant
        store.mset([(StoreKeys.ACTIVE_DATASOURCE, datasource)])

        # Retrieve datasource
        results = store.mget([StoreKeys.ACTIVE_DATASOURCE])

        assert results is not None
        assert len(results) > 0
        assert results[0] is datasource
        assert results[0].name == "test_db"

    def test_store_get_nonexistent_key(self):
        """Test getting non-existent key returns None."""
        store = InMemoryStore()

        result = store.get(("nonexistent",), "main")
        assert result is None

    def test_store_multiple_namespaces(self):
        """Test storing data in multiple namespaces."""
        store = InMemoryStore()
        datasource1 = MockSqlDataSource("db1")
        datasource2 = MockSqlDataSource("db2")

        # Store in different namespaces
        store.put(("datasource",), "namespace1", datasource1)
        store.put(("datasource",), "namespace2", datasource2)

        # Retrieve from different namespaces
        result1 = store.get(("datasource",), "namespace1")
        result2 = store.get(("datasource",), "namespace2")

        assert result1.value.name == "db1"
        assert result2.value.name == "db2"

    def test_store_overwrite_existing_key(self):
        """Test overwriting existing key in store."""
        store = InMemoryStore()
        datasource1 = MockSqlDataSource("original")
        datasource2 = MockSqlDataSource("replacement")

        # Put original
        store.put(("datasource",), "main", datasource1)

        # Overwrite with new datasource
        store.put(("datasource",), "main", datasource2)

        # Should get the replacement
        result = store.get(("datasource",), "main")
        assert result.value.name == "replacement"

    def test_store_multiple_keys_same_namespace(self):
        """Test storing multiple keys in same namespace."""
        store = InMemoryStore()
        datasource = MockSqlDataSource("db")
        config = {"setting": "value"}

        # Store different types of data
        store.put(("datasource",), "main", datasource)
        store.put(("config",), "main", config)

        # Retrieve both
        datasource_result = store.get(("datasource",), "main")
        config_result = store.get(("config",), "main")

        assert datasource_result.value.name == "db"
        assert config_result.value["setting"] == "value"


class TestGetDatasourceFromStoreFunction:
    """Test the get_datasource_from_store helper function."""

    def test_successful_datasource_retrieval(self):
        """Test successful datasource retrieval from store."""
        store = InMemoryStore()
        datasource = MockSqlDataSource("test_db")
        store.mset([(StoreKeys.ACTIVE_DATASOURCE, datasource)])

        result = get_datasource_from_store(store)

        assert result is datasource
        assert result.name == "test_db"

    def test_no_datasource_in_store(self):
        """Test error when no datasource is in store."""
        store = InMemoryStore()

        with pytest.raises(ValueError, match="No datasource available in store"):
            get_datasource_from_store(store)

    def test_store_access_error(self):
        """Test handling of store access errors."""
        mock_store = Mock()
        mock_store.get.side_effect = RuntimeError("Store corrupted")

        with pytest.raises(RuntimeError, match="Store corrupted"):
            get_datasource_from_store(mock_store)

    def test_datasource_type_validation(self):
        """Test that function works with different datasource types."""
        store = InMemoryStore()

        # Test with mock that implements SqlDataSource interface
        mock_datasource = Mock(spec=SqlDataSource)
        mock_datasource.name = "mock_db"
        store.mset([(StoreKeys.ACTIVE_DATASOURCE, mock_datasource)])

        result = get_datasource_from_store(store)
        assert result is mock_datasource

    def test_invalid_datasource_object(self):
        """Test behavior when invalid object is stored as datasource."""
        store = InMemoryStore()
        # Store invalid object
        store.mset([(StoreKeys.ACTIVE_DATASOURCE, "not_a_datasource")])

        # Should still return the object (type checking happens in tools)
        result = get_datasource_from_store(store)
        assert result == "not_a_datasource"


class TestStoreErrorHandling:
    """Test store error handling and recovery scenarios."""

    def test_concurrent_store_access(self):
        """Test concurrent access to store from multiple threads."""
        store = InMemoryStore()
        datasource = MockSqlDataSource("concurrent_db")
        store.put(("datasource",), "main", datasource)

        results = []
        errors = []

        def access_store(thread_id):
            try:
                for i in range(10):
                    result = get_datasource_from_store(store)
                    results.append((thread_id, result.name))
                    time.sleep(
                        0.001
                    )  # Small delay to increase chance of race conditions
            except Exception as e:
                errors.append((thread_id, e))

        # Create multiple threads
        threads = [threading.Thread(target=access_store, args=(i,)) for i in range(5)]

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # Verify results
        assert len(results) == 50  # 5 threads × 10 operations each
        assert len(errors) == 0

        # All results should be the same datasource
        for thread_id, datasource_name in results:
            assert datasource_name == "concurrent_db"

    def test_concurrent_store_modifications(self):
        """Test concurrent modifications to store."""
        store = InMemoryStore()

        modification_count = 0
        errors = []

        def modify_store(thread_id):
            nonlocal modification_count
            try:
                for i in range(5):
                    datasource = MockSqlDataSource(f"db_{thread_id}_{i}")
                    store.put(("datasource",), f"thread_{thread_id}", datasource)
                    modification_count += 1
                    time.sleep(0.001)
            except Exception as e:
                errors.append((thread_id, e))

        # Create multiple threads that modify store
        threads = [threading.Thread(target=modify_store, args=(i,)) for i in range(3)]

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # Verify no errors occurred
        assert len(errors) == 0
        assert modification_count == 15  # 3 threads × 5 modifications each

        # Verify all modifications were persisted
        for thread_id in range(3):
            result = store.get(("datasource",), f"thread_{thread_id}")
            assert result is not None
            assert f"db_{thread_id}" in result.value.name

    def test_large_object_storage(self):
        """Test storing large objects in store."""
        store = InMemoryStore()

        # Create a large mock datasource with lots of data
        large_datasource = MockSqlDataSource("large_db")
        large_datasource.large_data = "x" * 1000000  # 1MB of data
        large_datasource.metadata = {f"key_{i}": f"value_{i}" for i in range(1000)}

        # Store large object
        store.put(("datasource",), "main", large_datasource)

        # Retrieve and verify
        result = get_datasource_from_store(store)
        assert result.name == "large_db"
        assert len(result.large_data) == 1000000
        assert len(result.metadata) == 1000

    def test_store_memory_cleanup(self):
        """Test that store properly manages memory."""
        store = InMemoryStore()

        # Store many datasources
        for i in range(100):
            datasource = MockSqlDataSource(f"db_{i}")
            store.put(("datasource",), f"namespace_{i}", datasource)

        # Verify all are stored
        for i in range(100):
            result = store.get(("datasource",), f"namespace_{i}")
            assert result is not None
            assert result.value.name == f"db_{i}"

        # Clear some namespaces (if supported by implementation)
        # This test verifies the store can handle many objects


@pytest.mark.skip(
    reason="BaseAgent API changed in v0.2.0 - no longer accepts datasource parameter or has add_datasource/get_datasource methods. "
    "Tests need to be updated to use new service-based architecture. See CHANGELOG.md for migration guide."
)
class TestStoreIntegrationWithBaseAgent:
    """Test store integration with BaseAgent class.

    NOTE: These tests are for the old v0.1.x API and need to be updated for v0.2.0.
    In v0.2.0, datasource management moved to DataSourceService.
    """

    def test_base_agent_store_initialization(self):
        """Test that BaseAgent properly initializes store."""
        # TODO: Update for v0.2.0 - BaseAgent no longer accepts datasource parameter
        datasource = MockSqlDataSource("agent_db")
        store = InMemoryStore()
        store.mset([(StoreKeys.ACTIVE_DATASOURCE, datasource)])
        agent = BaseAgent(model="gpt-3.5-turbo", store=store)

        # Verify store is initialized
        assert agent.store is not None
        assert agent.store is store

    def test_base_agent_datasource_update(self):
        """Test updating datasource in BaseAgent updates store."""
        # TODO: Update for v0.2.0 - use DataSourceService instead
        pass

    def test_multiple_agents_separate_stores(self):
        """Test that multiple agents have separate stores."""
        # TODO: Update for v0.2.0
        pass

    def test_agent_store_persistence_across_operations(self):
        """Test that agent store persists across multiple operations."""
        # TODO: Update for v0.2.0 - use DataSourceService
        pass


class TestStoreSerializationAndPersistence:
    """Test store serialization and data persistence scenarios."""

    def test_datasource_serialization_compatibility(self):
        """Test that datasources can be serialized/deserialized for store operations."""
        store = InMemoryStore()
        datasource = MockSqlDataSource("serializable_db")

        # Store datasource
        store.put(("datasource",), "main", datasource)

        # Simulate serialization/deserialization cycle
        # (InMemoryStore doesn't actually serialize, but this tests the interface)
        retrieved = store.get(("datasource",), "main")

        # Test that the object maintains its properties
        assert retrieved.value.name == "serializable_db"
        assert retrieved.value.connection_status == "connected"
        assert retrieved.value.query_count == 0

        # Test that methods still work
        result = retrieved.value.query("SELECT 1")
        assert "SELECT 1" in result
        assert retrieved.value.query_count == 1

    def test_complex_datasource_object_handling(self):
        """Test handling of complex datasource objects with nested data."""
        store = InMemoryStore()

        # Create complex datasource
        datasource = MockSqlDataSource("complex_db")
        datasource.config = {
            "host": "localhost",
            "port": 5432,
            "database": "testdb",
            "nested": {"connection_pool": {"min": 1, "max": 10}, "timeout": 30},
        }
        datasource.connection_history = ["connect", "query", "disconnect"]

        # Store complex object
        store.put(("datasource",), "main", datasource)

        # Retrieve and verify structure is preserved
        result = get_datasource_from_store(store)

        assert result.name == "complex_db"
        assert result.config["host"] == "localhost"
        assert result.config["nested"]["connection_pool"]["max"] == 10
        assert len(result.connection_history) == 3

    def test_store_data_integrity_over_time(self):
        """Test that store maintains data integrity over extended operations."""
        store = InMemoryStore()
        datasource = MockSqlDataSource("integrity_db")
        datasource.operation_log = []

        # Store initial datasource
        store.put(("datasource",), "main", datasource)

        # Perform many operations over time
        for i in range(100):
            retrieved = get_datasource_from_store(store)
            retrieved.operation_log.append(f"operation_{i}")
            retrieved.query(f"SELECT {i}")

            # Re-store modified datasource
            store.put(("datasource",), "main", retrieved)

        # Verify final state
        final_result = get_datasource_from_store(store)
        assert len(final_result.operation_log) == 100
        assert final_result.query_count == 100
        assert final_result.operation_log[0] == "operation_0"
        assert final_result.operation_log[-1] == "operation_99"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
