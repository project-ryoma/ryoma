from typing import Any, Dict, Optional

from ryoma_ai.agent.base import ChatAgent
from ryoma_ai.api.agent_manager import AgentManager
from ryoma_ai.embedding.config import EmbeddingConfig
from ryoma_ai.embedding.factory import create_embedder
from ryoma_ai.prompt.prompt_builder_orchestrator import PromptBuilder
from ryoma_ai.prompt.prompt_template import PromptTemplateFactory
from ryoma_ai.vector_store.config import VectorStoreConfig
from ryoma_ai.vector_store.factory import create_vector_store


class RyomaClient:
    """
    High-level interface for executing LLM agent workflows and RAG-style semantic search
    using pluggable backends for agents, embedding, and vector storage.
    """

    def __init__(
        self,
        vector_store_config: VectorStoreConfig,
        embedding_config: EmbeddingConfig,
        repr_type: str = "CODE_REPRESENTATION",
    ):
        # Agent manager for running SQL/Python/etc
        self.agent_manager = AgentManager()

        # Prompt construction engine (via representation type)
        self.template_factory = PromptTemplateFactory()
        self.prompt_builder = PromptBuilder(repr_type, self.template_factory)

        # Embedding + semantic search
        self.embedder = create_embedder(embedding_config)
        self.vector_store = create_vector_store(vector_store_config, self.embedder)

    def build_agent(self, context: Dict[str, Any]) -> ChatAgent:
        return self.agent_manager.build_from_context(context)

    def run(self, agent: ChatAgent, user_question: str):
        prompt = self.build_prompt(user_question, context)
        return agent.stream(prompt)

    def build_prompt(
        self,
        question: str,
        context: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> str:
        return self.prompt_builder.build(
            question=question,
            context=context,
            metadata=metadata,
        )

    def build_prompt_with_semantic_context(
        self,
        question: str,
        top_k: int = 5,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        retrieved_docs = self.semantic_search(question, top_k=top_k)
        context = "\n".join([doc["text"] for doc in retrieved_docs])
        return self.build_prompt(question=question, context=context, metadata=metadata)

    def embed_document(self, doc_id: str, text: str):
        self.vector_store.index_documents([doc_id], [text])

    def semantic_search(self, query: str, top_k: int = 5):
        return self.vector_store.search_documents(query, top_k)
