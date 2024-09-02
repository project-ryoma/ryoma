from typing import Optional

from ryoma_lab.models.embedding import Embedding
from ryoma_lab.states.base import BaseState


class AIState(BaseState):
    tab_value: str = "agent"

    embedding: Optional[Embedding] = None

    def on_load(self):
        pass
