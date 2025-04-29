from abc import ABC
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class SearchResult:
    id: str
    score: float
    metadata: Dict[str, Any]


class VectorStore(ABC):
    def index(
        self,
        ids: List[str],
        vectors: List[List[float]],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Add or update vector entries with corresponding metadata.
        Useful for decoupling from embedding logic (embed first, then index).
        """
        raise NotImplementedError

    def index_documents(
        self,
        ids: List[str],
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """
        Embed and add text documents to the vector store.
        """
        raise NotImplementedError

    def search(self, query_vector: List[float], top_k: int = 5) -> List[SearchResult]:
        """
        Perform vector-based semantic search using a precomputed query vector.
        Returns a list of SearchResult, each with ID, score, and metadata (e.g. text).
        """
        raise NotImplementedError

    def search_documents(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """
        Embed the query and return semantically similar results from the vector store.
        """
        raise NotImplementedError
