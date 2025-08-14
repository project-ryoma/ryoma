from typing import Optional
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore
from ryoma_ai.vector_store.config import VectorStoreConfig


def create_vector_store(
    config: VectorStoreConfig,
    embedding_function: Optional[Embeddings] = None
) -> VectorStore:
    """
    Create a LangChain vector store based on config type.
    Supports: chroma, faiss, qdrant, milvus, pgvector
    """
    store_type = config.type.lower()

    if store_type == "chroma":
        try:
            from langchain_chroma import Chroma
        except ImportError:
            raise ImportError("Chroma support requires: pip install langchain-chroma")

        return Chroma(
            collection_name=config.collection_name,
            persist_directory=config.extra_configs.get("persist_directory", "./chroma_db"),
            embedding_function=embedding_function,
        )

    elif store_type == "faiss":
        if not embedding_function:
            raise ValueError("FAISS requires an embedding function")

        try:
            import faiss
            from langchain_community.vectorstores import FAISS
        except ImportError:
            raise ImportError("FAISS support requires: pip install langchain-faiss")

        # FAISS requires dimension to be known upfront
        dimension = config.dimension
        index = faiss.IndexFlatL2(dimension)

        return FAISS(
            embedding_function=embedding_function,
            index=index,
            docstore=config.extra_configs.get("docstore", {}),
            index_to_docstore_id=config.extra_configs.get("index_to_docstore_id", {})
        )

    elif store_type == "qdrant":
        try:
            from langchain_community.vectorstores import Qdrant
            from qdrant_client import QdrantClient
        except ImportError:
            raise ImportError("Qdrant support requires: pip install langchain-qdrant qdrant-client")

        qdrant_config = config.extra_configs
        client = QdrantClient(
            url=qdrant_config.get("url", "http://localhost:6333"),
            api_key=qdrant_config.get("api_key"),
        )

        return Qdrant(
            client=client,
            collection_name=config.collection_name,
            embeddings=embedding_function,
        )

    elif store_type == "milvus":
        try:
            from langchain_community.vectorstores import Milvus
        except ImportError:
            raise ImportError("Milvus support requires: pip install langchain-milvus")

        milvus_config = config.extra_configs
        return Milvus(
            embedding_function=embedding_function,
            collection_name=config.collection_name,
            connection_args={
                "host": milvus_config.get("host", "localhost"),
                "port": milvus_config.get("port", 19530),
                "user": milvus_config.get("user"),
                "password": milvus_config.get("password"),
            },
            consistency_level=milvus_config.get("consistency_level", "Session"),
            drop_old=milvus_config.get("drop_old", False),
        )

    elif store_type == "pgvector":
        try:
            from langchain_postgres import PGVector
        except ImportError:
            raise ImportError("PGVector support requires: pip install langchain-postgres")

        pgvector_config = config.extra_configs
        connection_string = pgvector_config.get(
            "connection_string",
            f"postgresql://{pgvector_config.get('user', 'postgres')}:"
            f"{pgvector_config.get('password', 'password')}@"
            f"{pgvector_config.get('host', 'localhost')}:"
            f"{pgvector_config.get('port', 5432)}/"
            f"{pgvector_config.get('database', 'postgres')}"
        )

        return PGVector(
            embeddings=embedding_function,
            collection_name=config.collection_name,
            connection=connection_string,
            distance_strategy=pgvector_config.get("distance_strategy", "cosine"),
            pre_delete_collection=pgvector_config.get("pre_delete_collection", False),
        )

    else:
        raise ValueError(f"Unsupported vector store type: {store_type}")
