from typing import Optional

from ryoma_lab.models.embedding import Embedding
from ryoma_lab.states.base import BaseState


class AIState(BaseState):
    tab_value: str = "agent"

    embedding: Optional[Embedding] = None

    selected_model: str = "gpt4all:all-MiniLM-L6-v2-f16"
    dimension: int = 512
    api_key: Optional[str] = ""

    def set_model(self, model: str):
        self.selected_model = model
        self.load_embedding()

    def set_dimension(self, dimension: int):
        self.dimension = dimension
        self.load_embedding()

    def set_api_key(self, api_key: str):
        self.api_key = api_key
        self.load_embedding()

    def load_embedding(self):
        self.embedding = Embedding(
            model=self.selected_model,
            model_parameters={"api_key": self.api_key, "dimension": self.dimension},
        )

    def on_load(self):
        self.load_embedding()
