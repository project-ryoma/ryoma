import logging
from typing import Dict, List, Optional, Union

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from ryoma_ai.agent.base import BaseAgent
from ryoma_ai.llm.provider import load_model_provider
from ryoma_ai.models.agent import AgentType


class EmbeddingAgent(BaseAgent):
    type: str = AgentType.embedding
    description: str = "Simple Embedding Agent"

    def __init__(self, model, model_parameters: Optional[Dict] = None):
        logging.info(f"Initializing Embedding Agent with model: {model}")
        self.embedding: Embeddings = load_model_provider(
            model, "embedding", model_parameters=model_parameters
        )

    def embed_documents(self, texts: List[Document]) -> List[List[float]]:
        return self.embedding.embed_documents([text.page_content for text in texts])

    def embed_query(self, text: Union[Document, str]) -> List[float]:
        text = text.page_content if isinstance(text, Document) else text
        return self.embedding.embed_query(text)
