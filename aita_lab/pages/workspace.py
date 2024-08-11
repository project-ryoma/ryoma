"""The workspace page."""

import reflex as rx

from aita_lab import styles
from aita_lab.components.loading_icon import loading_icon
from aita_lab.components.model_selector import select_model
from aita_lab.components.tool_kernel import notebook
from aita_lab.states.agent import AgentState
from aita_lab.states.base import BaseState
from aita_lab.states.datasource import DataSourceState
from aita_lab.states.llm_providers import ChatModelProvider, EmbeddingModelProvider
from aita_lab.states.workspace import QA, ChatState
from aita_lab.states.prompt_template import PromptTemplateState
from aita_lab.states.tool_calls import ToolCallState
from aita_lab.states.vector_store import VectorStoreState
from aita_lab.styles import markdown_style, message_style
from aita_lab.templates import template


def message(qa: QA) -> rx.Component:
    """A single question/answer message.

    Args:
        qa: The question/answer pair.

    Returns:
        A component displaying the question/answer pair.
    """
    return rx.box(
        rx.box(
            rx.markdown(
                qa.question,
                background_color=rx.color("mauve", 4),
                color=rx.color("mauve", 12),
                component_map=markdown_style,
                **message_style,
            ),
            text_align="right",
            margin_top="1em",
        ),
        rx.box(
            rx.markdown(
                qa.answer,
                background_color=rx.color("accent", 4),
                color=rx.color("accent", 12),
                component_map=markdown_style,
                **message_style,
            ),
            text_align="left",
            padding_top="1em",
            width="100%",
        ),
        width="100%",
    )


def chat_history() -> rx.Component:
    """List all the messages in a single conversation."""
    return rx.vstack(
        rx.box(rx.foreach(ChatState.chats[ChatState.current_chat], message), width="100%"),
        py="8",
        flex="1",
        width="100%",
        max_width="50em",
        padding_x="4px",
        align_self="center",
        overflow_y="auto",
        overflow_x="hidden",
        padding_bottom="5em",
    )


def action_bar() -> rx.Component:
    """The action bar to send a new message."""
    return rx.center(
        rx.vstack(
            rx.chakra.form(
                rx.chakra.form_control(
                    rx.flex(
                        rx.radix.text_area(
                            placeholder="Type something...",
                            id="question",
                            enter_key_submit=True,
                            flex_grow=1,
                        ),
                        rx.button(
                            rx.cond(
                                ChatState.processing,
                                loading_icon(height="1em", width="1em"),
                                rx.text("Send"),
                            ),
                            type="submit",
                        ),
                        spacing="4",
                        align_items="center",
                        padding_x="16px",
                    ),
                    is_disabled=ChatState.processing,
                    width="100%",
                ),
                on_submit=ChatState.process_question,
                reset_on_submit=True,
                width="100%",
            ),
            rx.text(
                "Aita may return factually incorrect or misleading responses. Use discretion.",
                text_align="center",
                font_size=".75em",
                color=rx.color("mauve", 10),
            ),
            align_items="center",
            width="100%",
        ),
        position="sticky",
        bottom="0",
        left="0",
        padding_y="16px",
        backdrop_filter="auto",
        backdrop_blur="lg",
        border_top=f"1px solid {rx.color('mauve', 3)}",
        background_color=rx.color("mauve", 2),
        align_items="stretch",
        width="100%",
    )


def datasource_selector() -> rx.Component:
    """The datasource selector."""
    return rx.chakra.form(
        rx.chakra.form_control(
            rx.text(
                "Data Source",
                asi_="div",
                mb="1",
                size="1",
                weight="bold",
                color_scheme="gray",
                padding_left="1px",
            ),
            rx.select.root(
                rx.select.trigger(
                    placeholder="Select a datasource",
                    width="100%",
                ),
                rx.select.content(
                    rx.select.group(
                        rx.select.label("Connected Data Source"),
                        rx.cond(
                            DataSourceState.datasource_names,
                            rx.foreach(
                                DataSourceState.datasource_names,
                                lambda ds: rx.select.item(ds, value=ds),
                            ),
                        ),
                        width="100%",
                    ),
                    rx.select.group(
                        rx.select.item("Create new datasource + ", value="custom"),
                    ),
                    width="100%",
                ),
                value=ChatState.current_datasource,
                on_change=ChatState.set_current_datasource,
                width="100%",
            ),
            label="Datasource",
            width="100%",
        ),
        width="100%",
    )


def prompt_template_selector() -> rx.Component:
    """The prompt template selector."""
    return rx.chakra.form(
        rx.chakra.form_control(
            rx.text(
                "Prompt Template",
                asi_="div",
                mb="1",
                size="2",
                weight="bold",
            ),
            rx.select.root(
                rx.select.trigger(
                    placeholder="Select a prompt template",
                    width="100%",
                ),
                rx.select.content(
                    rx.select.group(
                        rx.select.label("Prompt templates"),
                        rx.foreach(
                            PromptTemplateState.prompt_templates,
                            lambda pt: rx.cond(
                                pt.prompt_template_type == "builtin",
                                rx.select.item(
                                    pt.prompt_template_name, value=pt.prompt_template_name
                                ),
                            ),
                        ),
                    ),
                    rx.select.group(
                        rx.select.label("Custom prompt"),
                        rx.foreach(
                            PromptTemplateState.prompt_templates,
                            lambda pt: rx.cond(
                                pt.prompt_template_type == "custom",
                                rx.select.item(
                                    pt.prompt_template_name, value=pt.prompt_template_name
                                ),
                            ),
                        ),
                        rx.chakra.button(
                            rx.flex("Create new prompt +", spacing="3"),
                            size="sm",
                            width="100%",
                            on_click=rx.redirect("/prompt_template"),
                        ),
                    ),
                ),
                value=ChatState.current_prompt_template.prompt_template_name,
                on_change=ChatState.set_current_prompt_template,
                width="100%",
            ),
            rx.cond(
                ChatState.vector_feature_dialog_open,
                rx.flex(
                    rx.form(
                        rx.chakra.form_control(
                            rx.text(
                                "Embedding Model *",
                                asi_="div",
                                mb="1",
                                size="2",
                                weight="bold",
                            ),
                            select_model(
                                EmbeddingModelProvider,
                                ChatState.current_embedding_model,
                                ChatState.set_current_embedding_model,
                                trigger_width="100%",
                            ),
                            label="Model",
                            width="100%",
                        ),
                        width="100%",
                    ),
                    rx.text(
                        "K-Shot",
                        asi_="div",
                        mb="1",
                        size="2",
                        weight="bold",
                    ),
                    rx.input(
                        placeholder="Enter the number of examples",
                        width="100%",
                        on_blur=ChatState.set_current_k_shot,
                        padding_top="2",
                    ),
                    rx.text(
                        "Vector Feature *",
                        asi_="div",
                        mb="1",
                        size="2",
                        weight="bold",
                    ),
                    rx.select.root(
                        rx.select.trigger(
                            placeholder="Select your feature",
                        ),
                        rx.select.content(
                            rx.select.group(
                                rx.select.label("Select your feature"),
                                rx.foreach(
                                    VectorStoreState.vector_feature_views,
                                    lambda x: rx.select.item(x.name, value=f"{x.name}:{x.feature}"),
                                ),
                                rx.select.item(
                                    "Create new feature +",
                                    value="new",
                                ),
                            ),
                        ),
                        value=ChatState.current_vector_feature,
                        on_change=ChatState.set_current_vector_feature,
                    ),
                    spacing="2",
                    direction="column",
                    margin_top="1em",
                    padding="1em",
                    border=styles.border,
                ),
            ),
            label="Prompt Template",
            width="100%",
        ),
    )


def agent_selector() -> rx.Component:
    return rx.chakra.form(
        rx.chakra.form_control(
            rx.text(
                "Agent Type",
                asi_="div",
                mb="1",
                size="1",
                weight="bold",
                color_scheme="gray",
                padding_left="1px",
            ),
            rx.select.root(
                rx.select.trigger(
                    placeholder="Select an agent",
                    width="100%",
                ),
                rx.select.content(
                    rx.select.group(
                        rx.foreach(
                            AgentState.agent_names,
                            lambda agent_name: rx.select.item(agent_name, value=agent_name),
                        ),
                        rx.chakra.button(
                            "Create new agent +",
                            on_click=lambda: rx.redirect("/agent"),
                            size="sm",
                            width="100%",
                            justify="start",
                        ),
                        width="100%",
                    )
                ),
                value=ChatState.current_chat_agent_type,
                on_change=ChatState.set_current_chat_agent_type,
                width="100%",
            ),
            label="Agent Type",
            width="100%",
            min_width="12em",
        )
    )


def chat_model_selector() -> rx.Component:
    return rx.box(
        rx.text(
            "Chat Model *",
            asi_="div",
            mb="1",
            size="1",
            weight="bold",
            color_scheme="gray",
            padding_left="1px",
        ),
        select_model(
            ChatModelProvider,
            ChatState.current_chat_model,
            ChatState.set_current_chat_model,
        ),
        width="100%",
    )


@template(
    route="/",
    title="Workspace",
    on_load=[
        BaseState.on_load,
        ChatState.on_load,
        DataSourceState.on_load,
        PromptTemplateState.on_load,
        AgentState.on_load,
        VectorStoreState.on_load,
        ToolCallState.on_load,
    ],
)
def workspace() -> rx.Component:
    """The main app."""
    return rx.chakra.flex(
        rx.chakra.flex(
            rx.chakra.hstack(
                rx.flex(
                    chat_model_selector(),
                    datasource_selector(),
                    agent_selector(),
                    direction="row",
                    spacing="3",
                ),
                rx.dialog.root(
                    rx.dialog.trigger(
                        rx.chakra.button(
                            rx.tooltip(
                                rx.icon("settings"),
                                content="Try advanced settings!",
                            ),
                            color=rx.color("accent", 12),
                            size="md",
                            align_self="center",
                        )
                    ),
                    rx.dialog.content(
                        rx.dialog.title("Advanced Settings"),
                        rx.dialog.description(
                            "Advanced settings for AI agent, including data source, prompt template, and agent type."
                        ),
                        rx.flex(
                            prompt_template_selector(),
                            direction="column",
                            spacing="4",
                            padding_y="1em",
                            width="100%",
                        ),
                        rx.flex(
                            rx.dialog.close(
                                rx.button("Confirm"),
                            ),
                            rx.dialog.close(
                                rx.button(
                                    "Close",
                                    variant="soft",
                                    color_scheme="gray",
                                ),
                            ),
                            justify="end",
                            spacing="3",
                        ),
                    ),
                ),
                direction="row",
                padding="4",
                background_color=rx.color("mauve", 3),
                color=rx.color("mauve", 12),
                top="0",
                spacing="4",
                align_items="start",
            ),
            rx.chakra.vstack(
                chat_history(),
                action_bar(),
                background_color=rx.color("mauve", 2),
                color=rx.color("mauve", 12),
                height="100%",
                align_items="stretch",
                spacing="0",
                padding="20px",
                overflow_y="scroll",
                flex_grow=0,
            ),
            direction="column",
            width="100%",
            border=styles.border,
            border_radius=styles.border_radius,
            background_color=rx.color("mauve", 2),
        ),
        rx.chakra.grid_item(
            notebook(
                ChatState.current_tool,
                ChatState.run_tool,
                ChatState.cancel_tool,
                ChatState.update_tool_arg,
                ChatState.tool_output,
                ToolCallState.tool_calls,
            ),
            width="100%",
        ),
        h="85vh",
        width="100%",
        gap="2",
        direction="row",
        overflow_y="hidden",
    )
