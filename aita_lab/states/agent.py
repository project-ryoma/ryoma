import importlib
from typing import Optional

import random

import reflex as rx
from langchain_core.runnables.graph import Edge, Node

from aita.agent.factory import AgentFactory, get_supported_agents
from aita.agent.graph import GraphAgent
from aita_lab.states.graph import Graph


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


def create_agent_graph_node(node: Node):
    return {
        "id": node.id,
        "data": {"label": node.id},
        "position": get_node_position(node),
    }


def create_agent_graph_edge(id, edge: Edge):
    return {"id": id, "source": edge.source, "target": edge.target, "animated": True}


class Agent(rx.Model):
    id: Optional[str]
    name: str
    description: Optional[str]
    tools: Optional[list[str]]


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
                nodes=[create_agent_graph_node(node) for _, node in graph.nodes.items()],
                edges=[create_agent_graph_edge(id, edge) for id, edge in enumerate(graph.edges)],
            )

    @rx.var
    def agent_names(self) -> list[str]:
        return [agent.name for agent in self.agents]

    def get_custom_agents(self):
        return []

    def on_load(self):
        self.agents = [
            Agent(name=agent.name, description=agent.value.description)
            for agent in get_supported_agents() + self.get_custom_agents()
        ]

    def create_agent(self, graph: Graph):
        state_graph = GraphAgent.init_state_graph()
        tools = []
        for node in graph.nodes:
            if node["type"] == "tool":
                tool_name = node["data"]["label"]
                tool_cls = importlib.import_module(f"aita.tool.{tool_name}")
                tools.append(tool_cls)

        state_graph.set_entry_point("agent")
        state_graph.add_edge("tools", "agent")

        agent = GraphAgent(
            type="custom",
            tools=tools,
            model=self.current_model,
            graph=state_graph
        )
        return
