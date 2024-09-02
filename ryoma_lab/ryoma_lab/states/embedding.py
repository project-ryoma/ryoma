import logging
from typing import Optional

from ryoma.agent.utils import load_model_provider
from ryoma_lab.models.embedding import Embedding
from ryoma_lab.states.ai import AIState


class EmbeddingState(AIState):
    selected_model: str = "gpt4all:all-MiniLM-L6-v2-f16"
    dimension: int = 512
    api_key: Optional[str]

    def set_model(self, model: str):
        self.selected_model = model

    def set_dimension(self, dimension: int):
        self.dimension = dimension

    def set_api_key(self, api_key: str):
        self.api_key = api_key

    def create_embedding(self):
        self._create_embedding_client()

    def _create_embedding_client(self):
        logging.info(f"Creating embedding client for {self.selected_model}")
        model = load_model_provider(
            self.selected_model,
            "embedding",
            model_parameters={"api_key": self.api_key, "dimension": self.dimension},
        )
        self.embedding = Embedding(
            name=self.selected_model,
            model=model,
        )

    def on_load(self):
        self._create_embedding_client()
