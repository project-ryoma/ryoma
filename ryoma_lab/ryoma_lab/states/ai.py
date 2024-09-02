from typing import Optional

from ryoma_lab.states.base import BaseState
from ryoma_lab.models.embedding import Embedding


class AIState(BaseState):
    tab_value: str = "agent"

    embedding: Optional[Embedding] = None

    def on_load(self):
        pass
