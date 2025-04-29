from langchain.embeddings.base import Embeddings
from langchain_community.vectorstores import Chroma, PGVector, Qdrant
from ryoma_ai.vector_store.base import VectorStore
from ryoma_ai.vector_store.config import VectorStoreConfig
from ryoma_ai.vector_store.langchain_vector_store import LangchainVectorStore


def create_vector_store(
    config: VectorStoreConfig, embedding_function: Embeddings = None
) -> VectorStore:
    """
    Create a vector store backend based on type and config.
    """
    store_type = config.type.lower()

    if store_type == "chroma":
        store = Chroma(
            collection_name=config.collection_name,
            persist_directory=config.persist_path,
            embedding_function=embedding_function,
        )
    elif store_type == "pgvector":
        store = PGVector(
            collection_name=config.collection_name,
            connection_string=config.pgvector_url,
            embedding_function=embedding_function,
        )
    elif store_type == "qdrant":
        store = Qdrant(
            collection_name=config.collection_name,
            url=config.qdrant_url,
            embedding_function=embedding_function,
        )
    else:
        raise ValueError(f"Unsupported vector store type: {store_type}")

    return LangchainVectorStore(store)
