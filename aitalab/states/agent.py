from typing import Optional

import reflex as rx

from aita.agent.factory import get_supported_agents


class Agent(rx.Model):
    id: Optional[str]
    name: str
    desciption: Optional[str]


class AgentState(rx.State):
    agents: list[Agent]
    agent_types: list[str] = [agent.name for agent in get_supported_agents()]
