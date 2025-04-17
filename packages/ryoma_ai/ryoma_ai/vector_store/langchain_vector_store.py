from langchain_core.vectorstores import VectorStore as LCVectorStore
from typing import List, Optional, Dict
from ryoma_ai.vector_store.base import VectorStore, SearchResult


class LangchainVectorStore(VectorStore):
    """
    Generic wrapper for any LangChain-compatible vector store.
    """

    def __init__(self,
                 impl: LCVectorStore):
        self.impl = impl

    def index(
        self,
        ids: List[str],
        vectors: List[List[float]],
        metadata: Optional[Dict[str, str]] = None,
    ) -> None:
        pass

    def index_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict]] = None,
    ):
        """
        Embed and add text documents to the vector store.
        """
        if metadatas is None:
            metadatas = [{} for _ in documents]

        self.impl.add_texts(documents, metadatas=metadatas)

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
    ) -> List[SearchResult]:
        results = self.impl.similarity_search_by_vector(query_vector, k=top_k)
        return [
            SearchResult(
                id=doc.metadata.get("doc_id", f"result_{i}"),
                score=0.0,
                metadata={k: str(v) for k, v in doc.metadata.items()},
            )
            for i, doc in enumerate(results)
        ]
