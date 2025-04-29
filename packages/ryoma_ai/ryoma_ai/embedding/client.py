import logging
from abc import ABC, abstractmethod
from typing import List, Optional

from langchain_core.embeddings import Embeddings
from ryoma_ai.llm.provider import load_model_provider


def get_embedding_client(
    selected_model: str, model_parameters: dict[str, str] = None
) -> Embeddings:
    logging.info(f"Creating embedding client for {selected_model}")
    return load_model_provider(
        selected_model,
        "embedding",
        model_parameters=model_parameters,
    )


class EmbeddingClient(ABC):
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        pass

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed(t) for t in texts]

    @abstractmethod
    def langchain(self) -> Embeddings:
        pass


class LangchainEmbeddingClient(EmbeddingClient):
    def __init__(self, lc_embedder: Embeddings):
        self._embedder = lc_embedder

    def embed(self, text: str) -> List[float]:
        return self._embedder.embed_query(text)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return self._embedder.embed_documents(texts)

    def langchain(self) -> Embeddings:
        return self._embedder


def create_embedder(
    model_name: str, model_parameters: Optional[dict] = None
) -> EmbeddingClient:
    lc_embedder = get_embedding_client(
        model_name,
        model_parameters=model_parameters or {},
    )
    return LangchainEmbeddingClient(lc_embedder)
