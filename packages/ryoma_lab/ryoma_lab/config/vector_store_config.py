"""Utility to convert rxconfig to VectorStoreConfig."""

from typing import Any, Dict

import reflex as rx
from ryoma_ai.vector_store.config import VectorStoreConfig


def get_vector_store_config_from_rxconfig() -> VectorStoreConfig:
    """
    Create VectorStoreConfig from the current rxconfig settings.

    Returns:
        VectorStoreConfig configured based on rxconfig.py settings
    """
    config = rx.config.get_config()

    # Extract vector store settings from rxconfig
    store_type = getattr(config, "vector_store_type", "chroma")
    store_url = getattr(config, "vector_store_url", None)
    collection_name = getattr(config, "vector_store_collection", "ryoma_vectors")
    dimension = getattr(config, "vector_store_dimension", 768)

    # Build extra_configs based on store type and URL
    extra_configs = _build_extra_configs(store_type, store_url)

    return VectorStoreConfig(
        type=store_type,
        collection_name=collection_name,
        dimension=dimension,
        distance_metric="cosine",
        extra_configs=extra_configs,
    )


def _build_extra_configs(store_type: str, store_url: str = None) -> Dict[str, Any]:
    """
    Build extra configs based on store type and URL.

    Args:
        store_type: The vector store type (chroma, pgvector, etc.)
        store_url: Optional connection URL

    Returns:
        Dictionary of store-specific configurations
    """
    extra_configs = {}

    if store_type == "chroma":
        extra_configs["persist_directory"] = "./data/chroma_db"

    elif store_type == "pgvector":
        if store_url:
            extra_configs["connection_string"] = store_url
        else:
            # Default PostgreSQL settings
            extra_configs.update(
                {
                    "host": "localhost",
                    "port": 5432,
                    "database": "postgres",
                    "user": "postgres",
                    "password": "password",
                }
            )
        extra_configs["distance_strategy"] = "cosine"

    elif store_type == "milvus":
        if store_url:
            # Parse Milvus URL if provided
            # Format: milvus://user:password@host:port
            pass  # Could add URL parsing logic here
        else:
            extra_configs.update(
                {"host": "localhost", "port": 19530, "consistency_level": "Session"}
            )

    elif store_type == "qdrant":
        if store_url:
            extra_configs["url"] = store_url
        else:
            extra_configs["url"] = "http://localhost:6333"

    elif store_type == "faiss":
        extra_configs["index_type"] = "flat"

    return extra_configs
