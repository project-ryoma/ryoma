from typing import List, Optional

from feast import FeatureStore
from ryoma_ai.vector_store.base import SearchResult, VectorStore


class FeastVectorStore(VectorStore):
    def __init__(
        self,
        store: FeatureStore,
        feature_view: str,
        vector_column: str,
        metadata_column: str,
    ):
        self.store = store
        self.feature_view = feature_view
        self.vector_column = vector_column
        self.metadata_column = metadata_column

    def index(
        self,
        ids: List[str],
        vectors: List[List[float]],
        metadatas: Optional[List[dict]] = None,
    ):
        """
        Feast doesn't support direct writes to feature views from Python client.
        This method is a placeholder to document expected interface — assume vectors are ingested via batch jobs.
        """
        raise NotImplementedError(
            "Feast ingestion should be done via batch ingestion outside the API."
        )

    def search(self, query_vector: List[float], top_k: int = 5) -> List[SearchResult]:
        """
        Call custom retrieve_documents() if implemented in your FeatureStore subclass.
        The feature view should contain vector_column (List[float]) and metadata_column (e.g. text).
        """
        if not hasattr(self.store, "retrieve_documents"):
            raise NotImplementedError(
                "Your FeatureStore must implement retrieve_documents(query_vector, ...)"
            )

        return []
