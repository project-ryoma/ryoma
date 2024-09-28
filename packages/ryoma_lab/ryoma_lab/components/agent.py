"""The Agent Page."""

import reflex as rx
from ryoma_lab.components.reactflow import background, controls, react_flow
from ryoma_lab.states.agent import Agent, AgentState
from ryoma_lab.states.graph import GraphState
from ryoma_lab.states.tool import ToolState
from ryoma_lab.templates import template


def agent_card(agent: Agent):
    """Create an agent card."""
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.chakra.card(
                rx.chakra.text(
                    agent.description,
                    no_of_lines=3,
                ),
                header=rx.chakra.heading(agent.name, size="md", padding="2px"),
                direction="column",
                overflow="auto",
                height="300px",
                width="50%",
                min_width="12em",
                margin_right="20px",
                cursor="pointer",
                _hover={"background_color": rx.color("gray", 2)},
            )
        ),
        rx.dialog.content(
            rx.dialog.title(agent.name, size="6"),
            rx.dialog.description(agent.description),
            rx.cond(
                AgentState.current_agent_graph is not None,
                rx.vstack(
                    rx.heading("Agent Flow", size="4"),
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
                justify="end",
            ),
        ),
        on_open_change=lambda is_open: AgentState.open_agent(is_open, agent),
    )


def show_agent_grid():
    """Create a content grid."""
    return rx.vstack(
        rx.chakra.flex(rx.foreach(AgentState.agents, agent_card), width="100%"),
        width="100%",
        overflow_x="scroll",
        padding="4px",
    )


def create_agent_flow():
    return rx.vstack(
        rx.heading("Create your own agent", size="6"),
        rx.hstack(
            rx.input(
                placeholder="Agent Name",
                on_blur=AgentState.set_current_agent_name,
                required=True,
            ),
            rx.input(
                placeholder="Describe your agent",
                on_blur=AgentState.set_current_agent_description,
                required=True,
            ),
            rx.select(
                ToolState.tool_names,
                placeholder="Select a tool to add",
                on_change=GraphState.add_tool_node,
            ),
            rx.button(
                "Create",
                variant="solid",
                on_click=lambda: AgentState.create_agent(GraphState.graph),
            ),
            rx.button(
                "Clear",
                variant="soft",
                color_scheme="gray",
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
            border=f"1px solid {rx.color('gray', 6)}",
            border_radius="0.375rem",
        ),
        margin_top="20px",
        height="30em",
        width="100%",
    )


def agent_component() -> rx.Component:
    return rx.vstack(
        show_agent_grid(),
        create_agent_flow(),
        # make the page full width
        width="100%",
    )
