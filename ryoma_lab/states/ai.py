import reflex as rx

from ryoma_lab.states.base import BaseState


class AIState(BaseState):
    tab_value: str = "agent"

    def on_load(self):
        pass
