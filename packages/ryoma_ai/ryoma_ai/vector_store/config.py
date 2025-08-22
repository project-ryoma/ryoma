from typing import Any, Dict, Optional

from pydantic import BaseModel


class VectorStoreConfig(BaseModel):
    """
    Unified configuration for all LangChain-supported vector stores.
    Supports: chroma, faiss, qdrant, milvus, pgvector, etc.
    """

    type: str  # "chroma", "faiss", "qdrant", "milvus", "pgvector"
    collection_name: str = "ryoma_index"
    dimension: int = 768
    distance_metric: str = "cosine"  # "cosine", "euclidean", "dot"

    # Performance configs
    batch_size: int = 100
    cache_size: int = 1000
    max_connections: int = 10

    # Store-specific configs go in extra_configs
    # Examples:
    # - Chroma: {"persist_directory": "./chroma_db"}
    # - Qdrant: {"url": "http://localhost:6333", "api_key": "..."}
    # - Milvus: {"host": "localhost", "port": 19530, "user": "...", "password": "..."}
    # - FAISS: {"index_type": "flat", "normalize_L2": False}
    # - PGVector: {"host": "localhost", "port": 5432, "database": "postgres", "user": "...", "password": "..."}
    extra_configs: Dict[str, Any] = {}

    @classmethod
    def for_chroma(
        cls,
        collection_name: str = "ryoma_index",
        persist_directory: str = "./chroma_db",
        **kwargs,
    ) -> "VectorStoreConfig":
        """Create a Chroma configuration."""
        return cls(
            type="chroma",
            collection_name=collection_name,
            extra_configs={"persist_directory": persist_directory, **kwargs},
        )

    @classmethod
    def for_faiss(
        cls, dimension: int = 768, index_type: str = "flat", **kwargs
    ) -> "VectorStoreConfig":
        """Create a FAISS configuration."""
        return cls(
            type="faiss",
            dimension=dimension,
            extra_configs={"index_type": index_type, **kwargs},
        )

    @classmethod
    def for_qdrant(
        cls,
        collection_name: str = "ryoma_index",
        url: str = "http://localhost:6333",
        api_key: Optional[str] = None,
        **kwargs,
    ) -> "VectorStoreConfig":
        """Create a Qdrant configuration."""
        return cls(
            type="qdrant",
            collection_name=collection_name,
            extra_configs={"url": url, "api_key": api_key, **kwargs},
        )

    @classmethod
    def for_milvus(
        cls,
        collection_name: str = "ryoma_index",
        host: str = "localhost",
        port: int = 19530,
        user: Optional[str] = None,
        password: Optional[str] = None,
        **kwargs,
    ) -> "VectorStoreConfig":
        """Create a Milvus configuration."""
        return cls(
            type="milvus",
            collection_name=collection_name,
            extra_configs={
                "host": host,
                "port": port,
                "user": user,
                "password": password,
                **kwargs,
            },
        )

    @classmethod
    def for_pgvector(
        cls,
        collection_name: str = "ryoma_index",
        host: str = "localhost",
        port: int = 5432,
        database: str = "postgres",
        user: str = "postgres",
        password: str = "password",
        connection_string: Optional[str] = None,
        distance_strategy: str = "cosine",
        **kwargs,
    ) -> "VectorStoreConfig":
        """Create a PGVector configuration."""
        return cls(
            type="pgvector",
            collection_name=collection_name,
            extra_configs={
                "host": host,
                "port": port,
                "database": database,
                "user": user,
                "password": password,
                "connection_string": connection_string,
                "distance_strategy": distance_strategy,
                **kwargs,
            },
        )


class DocumentProcessorConfig(BaseModel):
    chunk_size: int = 1000
    chunk_overlap: int = 200
    supported_formats: list = ["pdf", "txt", "csv", "json", "html"]
    max_file_size_mb: int = 100
