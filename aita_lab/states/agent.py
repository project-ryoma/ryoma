from typing import Optional

import reflex as rx
import random
from langchain_core.runnables.graph import Node
from aita.agent.graph import GraphAgent
from aita.agent.factory import get_supported_agents, AgentFactory
from aita_lab.states.graph import Graph


class Agent(rx.Model):
    id: Optional[str]
    name: str
    description: Optional[str]


def get_node_position(node: Node):
    if node.id == "__start__":
        return {"x": 20, "y": 20}
    elif node.id == "agent":
        return {"x": 20, "y": 100}
    elif node.id == "__end__":
        return {"x": 20, "y": 200}
    elif node.id == "tools":
        return {"x": 200, "y": 100}
    else:
        return {"x": random.randint(0, 500), "y": random.randint(0, 500)}


class AgentState(rx.State):
    agents: list[Agent] = []
    is_open: bool = False
    current_agent: Optional[Agent] = None
    current_agent_graph: Optional[Graph] = None

    def open_agent(self, is_open: bool, agent: Agent):
        self.is_open = is_open
        passthrough_agent = AgentFactory.create_agent(agent["name"], model="")
        if isinstance(passthrough_agent, GraphAgent):
            graph = passthrough_agent.get_graph()
            self.current_agent_graph = Graph(
                nodes=[{
                    "id": node.id,
                    "data": {"label": node.id},
                    "position": get_node_position(node),
                } for node_key, node in graph.nodes.items()],
                edges=[{
                    "id": id,
                    "source": edge.source,
                    "target": edge.target,
                    "animated": True
                } for id, edge in enumerate(graph.edges)]
            )
            print(self.current_agent_graph)

    @rx.var
    def agent_names(self) -> list[str]:
        return [agent.name for agent in self.agents]

    def on_load(self):
        self.agents = [Agent(
            name=agent.name,
            description="",
        ) for agent in get_supported_agents()]
