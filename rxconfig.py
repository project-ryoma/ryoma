import logging
from typing import Optional

import reflex as rx
from reflex.constants import LogLevel


class RyomaConfig(rx.Config):
    """Extended Reflex config with vector store settings."""
    
    # Vector store configuration
    vector_store_type: str = "chroma"
    vector_store_url: Optional[str] = None
    vector_store_collection: str = "ryoma_vectors"
    vector_store_dimension: int = 768


config = RyomaConfig(
    app_name="ryoma_lab",
    loglevel=LogLevel.INFO,
    # db_url="duckdb:///:memory:",
    
    # Vector store settings (can be overridden by environment variables)
    vector_store_type="chroma",  # Can be: chroma, pgvector, milvus, qdrant, faiss
    vector_store_url=None,  # If None, will use defaults for the store type
    vector_store_collection="ryoma_vectors",
    vector_store_dimension=768,
)

# Setup basic configuration for logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
