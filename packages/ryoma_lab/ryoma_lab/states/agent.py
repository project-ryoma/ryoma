import importlib
import json
import logging
import random
import uuid
from typing import Optional

import reflex as rx
from langchain_core.runnables.graph import Edge, Node
from ryoma_ai.agent.factory import AgentFactory, get_builtin_agents
from ryoma_ai.agent.workflow import WorkflowAgent
from ryoma_ai.models.agent import AgentType
from ryoma_lab.models.agent import Agent
from ryoma_lab.states.ai import AIState
from ryoma_lab.states.graph import Graph
from sqlmodel import select


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


class AgentState(AIState):
    agents: list[Agent] = []
    is_open: bool = False
    current_agent_name: Optional[str] = None
    current_agent_description: Optional[str] = None
    current_agent_graph: Optional[Graph] = None

    def open_agent(self, is_open: bool, agent: Agent):
        self.is_open = is_open
        if agent["type"] == AgentType.workflow.value:
            passthrough_agent = AgentFactory.create_agent(agent["name"], model="")
            graph = passthrough_agent.get_graph()
            self.current_agent_graph = Graph(
                nodes=[
                    create_agent_graph_node(node) for _, node in graph.nodes.items()
                ],
                edges=[
                    create_agent_graph_edge(id, edge)
                    for id, edge in enumerate(graph.edges)
                ],
            )
        elif agent["type"] == AgentType.custom.value:
            workflow = json.loads(agent["workflow"])
            self.current_agent_graph = Graph(**workflow)

    @rx.var
    def agent_names(self) -> list[str]:
        return [agent.name for agent in self.agents]

    def _build_workflow(self, graph: Graph):
        workflow_state = WorkflowAgent.init_state()
        tools = []
        for node in graph.nodes:
            if "type" in node and node["type"] == "tool":
                tool_name = node["data"]["label"]
                tool_cls = importlib.import_module(f"ryoma.tool.{tool_name}")
                tools.append(tool_cls)

        workflow_state.set_entry_point("agent")
        workflow_state.add_edge("tools", "agent")

        agent = WorkflowAgent(
            type=AgentType.custom, tools=tools, model="", graph=workflow_state
        )

    def create_agent(self, graph: Graph):
        if not self.current_agent_name:
            return rx.toast.error("Please enter a name for the agent.")
        logging.info("Creating agent with graph %s", graph)
        description = (
            self.current_agent_description or "A custom agent created by the user."
        )

        with rx.session() as session:
            agent = Agent(
                id=str(uuid.uuid4()),
                name=self.current_agent_name,
                type=AgentType.custom,
                description=description,
                workflow=json.dumps(graph),
            )
            session.add(agent)
            session.commit()
        self._load_agents()
        return

    def _load_custom_agents(self):
        with rx.session() as session:
            return session.exec(select(Agent)).all()

    def _load_agents(self):
        builtin_agents = [
            Agent(
                name=agent.name,
                description=agent.value.description,
                type=agent.value.type,
            )
            for agent in get_builtin_agents()
        ]
        custom_agents = [
            Agent(
                id=agent.id,
                name=agent.name,
                description=agent.description,
                type=agent.type,
                workflow=agent.workflow,
            )
            for agent in self._load_custom_agents()
        ]
        self.agents = builtin_agents + custom_agents

    def on_load(self):
        self._load_agents()
