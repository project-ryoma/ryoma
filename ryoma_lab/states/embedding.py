from typing import Optional

from ryoma_lab.states.ai import AIState
from ryoma.agent.utils import load_model_provider
from langchain_core.embeddings import Embeddings


class EmbeddingState(AIState):
    selected_model: str = "gpt4all:all-MiniLM-L6-v2-f16"
    dimension: int = 512
    api_key: Optional[str]

    def set_model(self,
                  model: str):
        self.selected_model = model

    def set_dimension(self,
                      dimension: int):
        self.dimension = dimension

    def set_api_key(self,
                    api_key: str):
        self.api_key = api_key

    def _create_embedding_client(self) -> Embeddings:
        return load_model_provider(
            self.selected_model,
            "embedding",
            model_parameters={
                "api_key": self.api_key,
                "dimension": self.dimension
            }
        )

    def on_load(self):
        pass
