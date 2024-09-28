"""The AI Page."""

import reflex as rx
from ryoma_lab.components.agent import agent_component
from ryoma_lab.components.embedding import embedding_component
from ryoma_lab.components.prompt_template import prompt_templatec_component
from ryoma_lab.components.tool import tool_component
from ryoma_lab.components.vector_store import vector_store_component
from ryoma_lab.states.agent import AgentState
from ryoma_lab.states.ai import AIState
from ryoma_lab.states.datasource import DataSourceState
from ryoma_lab.states.prompt_template import PromptTemplateState
from ryoma_lab.states.tool import ToolState
from ryoma_lab.states.vector_store import VectorStoreState
from ryoma_lab.templates import template


@template(
    route="/ai",
    title="AI Assistant",
    description="AI Assistant",
    on_load=[
        AIState.on_load,
        AgentState.on_load,
        PromptTemplateState.on_load,
        ToolState.on_load,
        DataSourceState.on_load,
        VectorStoreState.on_load,
    ],
)
def ai() -> rx.Component:
    """The AI page.

    Returns:
        The UI for the AI page.
    """
    return rx.vstack(
        rx.heading("AI Assistant", size="8"),
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger("Embeddings", value="embeddings", cursor="pointer"),
                rx.tabs.trigger(
                    "Prompt Settings", value="prompt_settings", cursor="pointer"
                ),
                rx.tabs.trigger(
                    "Vector Store", value="vector_store_project_name", cursor="pointer"
                ),
                rx.tabs.trigger("Agent", value="agent", cursor="pointer"),
                rx.tabs.trigger("Tools", value="tool", cursor="pointer"),
            ),
            rx.tabs.content(embedding_component(), padding_y="2em", value="embeddings"),
            rx.tabs.content(
                prompt_templatec_component(),
                padding_y="2em",
                value="prompt_settings",
            ),
            rx.tabs.content(
                vector_store_component(),
                padding_y="2em",
                value="vector_store_project_name",
            ),
            rx.tabs.content(
                agent_component(),
                padding_y="2em",
                value="agent",
            ),
            rx.tabs.content(
                tool_component(),
                padding_y="2em",
                value="tool",
            ),
            value=AIState.tab_value,
            on_change=AIState.set_tab_value,
            default_value="agent",
            orientation="horizontal",
            height="100vh",
            width="100%",
        ),
        width="100%",
    )
