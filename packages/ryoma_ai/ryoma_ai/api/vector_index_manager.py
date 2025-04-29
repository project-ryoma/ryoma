# ryoma_ai/api/vector_index_manager.py

from typing import List, Optional

from ryoma_ai.embedding.client import EmbeddingClient
from ryoma_ai.vector_store.base import VectorStore


class VectorIndexManager:
    """
    Handles embedding and semantic indexing/searching using a decoupled embedder + vector store.
    """

    def __init__(self, vector_store: VectorStore, embedder: EmbeddingClient):
        self.vector_store = vector_store
        self.embedder = embedder

    def index_text(self, doc_id: str, text: str):
        """
        Embed a single document and index it by ID.
        """
        vector = self.embedder.embed(text)
        self.vector_store.index([doc_id], [vector], metadatas=[{"text": text}])

    def index_text_batch(
        self, ids: List[str], texts: List[str], metadatas: Optional[List[dict]] = None
    ):
        """
        Embed and index a batch of documents.
        """
        vectors = self.embedder.embed_batch(texts)
        self.vector_store.index(ids, vectors, metadatas=metadatas)

    def search(self, query: str, top_k: int = 5):
        """
        Embed the query and return semantically similar results from the vector store.
        """
        query_vector = self.embedder.embed(query)
        return [r.metadata for r in self.vector_store.search(query_vector, top_k)]
