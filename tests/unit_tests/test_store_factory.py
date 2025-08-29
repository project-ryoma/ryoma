"""
Tests for store factory.
"""

import os
import sys
from unittest.mock import Mock, patch

import pytest
from langchain_core.stores import InMemoryStore
from ryoma_ai.store.store_factory import StoreFactory, StoreType


def test_create_memory_store():
    """Test creating an in-memory store."""
    store = StoreFactory.create_store(StoreType.MEMORY)
    assert isinstance(store, InMemoryStore)


def test_create_memory_store_default():
    """Test that memory store is created by default."""
    store = StoreFactory.create_store()
    assert isinstance(store, InMemoryStore)


def test_create_postgres_store_missing_dependency():
    """Test that proper error is raised when postgres dependency is missing."""
    with patch.dict("sys.modules", {"langgraph.store.postgres": None}):
        with pytest.raises(ImportError, match="langgraph\\[postgres\\]"):
            StoreFactory.create_store(
                StoreType.POSTGRES, {"connection_string": "postgresql://localhost"}
            )


@patch("langgraph.store.postgres.PostgresStore")
def test_create_postgres_store_missing_connection_string(mock_postgres_store):
    """Test that proper error is raised when connection string is missing."""
    with pytest.raises(ValueError, match="connection_string"):
        StoreFactory.create_store(StoreType.POSTGRES)


@patch("langgraph.store.postgres.PostgresStore")
def test_create_postgres_store_success(mock_postgres_store):
    """Test successful postgres store creation."""
    mock_store_instance = Mock()
    mock_postgres_store.from_conn_string.return_value = mock_store_instance

    connection_string = "postgresql://user:pass@localhost/db"
    store = StoreFactory.create_store(
        StoreType.POSTGRES, {"connection_string": connection_string}
    )

    mock_postgres_store.from_conn_string.assert_called_once_with(connection_string)
    mock_store_instance.setup.assert_called_once()
    assert store == mock_store_instance


def test_create_redis_store_missing_dependency():
    """Test that proper error is raised when redis dependency is missing."""
    with patch.dict("sys.modules", {"langgraph.store.redis": None}):
        with pytest.raises(ImportError, match="langgraph\\[redis\\]"):
            StoreFactory.create_store(
                StoreType.REDIS, {"connection_string": "redis://localhost"}
            )


@patch("langgraph.store.redis.RedisStore")
def test_create_redis_store_missing_connection_string(mock_redis_store):
    """Test that proper error is raised when connection string is missing."""
    with pytest.raises(ValueError, match="connection_string"):
        StoreFactory.create_store(StoreType.REDIS)


@patch("langgraph.store.redis.RedisStore")
def test_create_redis_store_success(mock_redis_store):
    """Test successful redis store creation."""
    mock_store_instance = Mock()
    mock_redis_store.from_conn_string.return_value = mock_store_instance

    connection_string = "redis://localhost:6379"
    store = StoreFactory.create_store(
        StoreType.REDIS, {"connection_string": connection_string}
    )

    mock_redis_store.from_conn_string.assert_called_once_with(connection_string)
    mock_store_instance.setup.assert_called_once()
    assert store == mock_store_instance


def test_unsupported_store_type():
    """Test that proper error is raised for unsupported store type."""
    with pytest.raises(ValueError, match="Unsupported store type"):
        StoreFactory.create_store("unsupported")


def test_create_from_env_default():
    """Test creating store from env with defaults."""
    with patch.dict(os.environ, {}, clear=True):
        store = StoreFactory.create_from_env()
        assert isinstance(store, InMemoryStore)


def test_create_from_env_memory():
    """Test creating memory store from env."""
    with patch.dict(os.environ, {"RYOMA_STORE_TYPE": "memory"}):
        store = StoreFactory.create_from_env()
        assert isinstance(store, InMemoryStore)


@patch("langgraph.store.postgres.PostgresStore")
def test_create_from_env_postgres(mock_postgres_store):
    """Test creating postgres store from env."""
    mock_store_instance = Mock()
    mock_postgres_store.from_conn_string.return_value = mock_store_instance

    connection_string = "postgresql://user:pass@localhost/db"
    with patch.dict(
        os.environ,
        {"RYOMA_STORE_TYPE": "postgres", "RYOMA_STORE_CONNECTION": connection_string},
    ):
        store = StoreFactory.create_from_env()

    mock_postgres_store.from_conn_string.assert_called_once_with(connection_string)
    assert store == mock_store_instance


def test_create_from_env_postgres_missing_connection():
    """Test fallback to memory when connection string is missing."""
    with patch.dict(os.environ, {"RYOMA_STORE_TYPE": "postgres"}):
        with patch("ryoma_ai.store.store_factory.logger") as mock_logger:
            store = StoreFactory.create_from_env()
            assert isinstance(store, InMemoryStore)
            mock_logger.warning.assert_called_once()


@patch("langgraph.store.redis.RedisStore")
def test_create_from_env_redis(mock_redis_store):
    """Test creating redis store from env."""
    mock_store_instance = Mock()
    mock_redis_store.from_conn_string.return_value = mock_store_instance

    connection_string = "redis://localhost:6379"
    with patch.dict(
        os.environ,
        {"RYOMA_STORE_TYPE": "redis", "RYOMA_STORE_CONNECTION": connection_string},
    ):
        store = StoreFactory.create_from_env()

    mock_redis_store.from_conn_string.assert_called_once_with(connection_string)
    assert store == mock_store_instance
