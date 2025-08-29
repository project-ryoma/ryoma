"""
Factory for creating different types of stores based on configuration.
"""

import logging
from typing import Dict, Any, Optional, Type
from langchain_core.stores import BaseStore, InMemoryStore

logger = logging.getLogger(__name__)


class StoreType:
    """Supported store types."""
    MEMORY = "memory"
    POSTGRES = "postgres"
    REDIS = "redis"


class StoreFactory:
    """Factory for creating store instances based on configuration."""
    
    @staticmethod
    def create_store(
        store_type: str = StoreType.MEMORY,
        store_config: Optional[Dict[str, Any]] = None,
    ) -> BaseStore[str, str]:
        """
        Create a store instance based on the specified type and configuration.
        
        Args:
            store_type: Type of store to create (memory, postgres, redis)
            store_config: Configuration for the store, varies by store type
                - For postgres: {"connection_string": "postgresql://..."}
                - For redis: {"connection_string": "redis://..."}
        
        Returns:
            BaseStore instance
            
        Raises:
            ValueError: If store type is not supported
            ImportError: If required dependencies are not installed
        """
        store_config = store_config or {}
        
        if store_type == StoreType.MEMORY:
            return InMemoryStore()
        
        elif store_type == StoreType.POSTGRES:
            try:
                from langgraph.store.postgres import PostgresStore
            except ImportError as e:
                raise ImportError(
                    "PostgresStore requires langgraph[postgres] to be installed. "
                    "Install with: pip install 'langgraph[postgres]'"
                ) from e
            
            connection_string = store_config.get("connection_string")
            if not connection_string:
                raise ValueError(
                    "PostgreSQL store requires 'connection_string' in store_config"
                )
            
            # Create and setup store
            store = PostgresStore.from_conn_string(connection_string)
            # Setup creates necessary tables
            store.setup()
            
            logger.info("Created PostgreSQL store")
            return store
        
        elif store_type == StoreType.REDIS:
            try:
                from langgraph.store.redis import RedisStore
            except ImportError as e:
                raise ImportError(
                    "RedisStore requires langgraph[redis] to be installed. "
                    "Install with: pip install 'langgraph[redis]'"
                ) from e
            
            connection_string = store_config.get("connection_string")
            if not connection_string:
                raise ValueError(
                    "Redis store requires 'connection_string' in store_config"
                )
            
            # Create and setup store
            store = RedisStore.from_conn_string(connection_string)
            store.setup()
            
            logger.info("Created Redis store")
            return store
        
        else:
            raise ValueError(
                f"Unsupported store type: {store_type}. "
                f"Supported types: {StoreType.MEMORY}, {StoreType.POSTGRES}, {StoreType.REDIS}"
            )
    
    @classmethod
    def create_from_env(cls) -> BaseStore[str, str]:
        """
        Create a store from environment variables.
        
        Looks for:
        - RYOMA_STORE_TYPE: Store type (memory, postgres, redis)
        - RYOMA_STORE_CONNECTION: Connection string for database stores
        
        Returns:
            BaseStore instance
        """
        import os
        
        store_type = os.getenv("RYOMA_STORE_TYPE", StoreType.MEMORY)
        
        if store_type == StoreType.MEMORY:
            return cls.create_store(store_type)
        
        connection_string = os.getenv("RYOMA_STORE_CONNECTION")
        if not connection_string:
            logger.warning(
                f"RYOMA_STORE_TYPE is set to '{store_type}' but "
                "RYOMA_STORE_CONNECTION is not set. Falling back to memory store."
            )
            return cls.create_store(StoreType.MEMORY)
        
        return cls.create_store(
            store_type=store_type,
            store_config={"connection_string": connection_string}
        )