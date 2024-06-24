"""The Agent Page."""

import reflex as rx

from aita_lab.states.agent import AgentState, Agent
from aita_lab.states.graph import GraphState
from aita_lab.templates import template
from aita_lab.components.reactflow import react_flow, background, controls


def agent_card(agent: Agent):
    """Create an agent card."""
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.chakra.card(
                rx.chakra.text(agent.description),
                header=rx.chakra.heading(agent.name, size="md", padding="2px"),
                direction="column",
                overflow="auto",
                height="300px",
                width="50%",
                margin_right="20px",
            )
        ),
        rx.dialog.content(
            rx.dialog.title(agent.name),
            rx.dialog.description(
                ""
            ),
            rx.cond(
                AgentState.current_agent_graph is not None,
                rx.vstack(
                    rx.heading("Agent Flow", size="6"),
                    react_flow(
                        background(),
                        controls(),
                        nodes_connectable=True,
                        on_connect=lambda e: GraphState.on_connect(e),
                        nodes=AgentState.current_agent_graph.nodes,
                        edges=AgentState.current_agent_graph.edges,
                        fit_view=True,
                    ),
                    margin_top="20px",
                    height="30em",
                    width="100%",
                ),
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button("Close", size="2"),
                ),
                justify="end"
            )
        ),
        on_open_change=lambda is_open: AgentState.open_agent(is_open, agent),
    )


def content_grid():
    """Create a content grid."""
    return rx.vstack(
        rx.chakra.text("Click on an agent to view its flow", width="100", padding_y="4"),
        rx.chakra.flex(
            rx.foreach(AgentState.agents, agent_card, width="100"),
            width="100%"
        )
    )


def create_agent_flow():
    return rx.vstack(
        rx.heading("Create your own agent", size="6"),
        rx.hstack(
            rx.button(
                "Add Tool",
                on_click=GraphState.add_random_node,
            ),
            rx.button(
                "Clear graph",
                on_click=GraphState.clear_graph,
            ),
            width="100%",
        ),
        react_flow(
            background(),
            controls(),
            nodes_draggable=True,
            nodes_connectable=True,
            on_nodes_change=lambda e: GraphState.on_nodes_change(e),
            on_connect=lambda e: GraphState.on_connect(e),
            nodes=GraphState.graph.nodes,
            edges=GraphState.graph.edges,
            fit_view=True,
        ),
        margin_top="20px",
        height="30em",
        width="100%",
    )


@template(route="/agent", title="Agent", on_load=AgentState.on_load())
def agent() -> rx.Component:
    """The tool page.

    Returns:
        The UI for the agent page.
    """
    return rx.vstack(
        rx.heading("Agent", size="8"),
        rx.box(
            content_grid(),
            margin_top="20px",
            width="100%",
        ),
        create_agent_flow(),
        # make the page full width
        width="100%",
    )
