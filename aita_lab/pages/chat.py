"""The chat page."""

import reflex as rx

from aita_lab import styles
from aita_lab.components.codeeditor import code_editor
from aita_lab.components.loading_icon import loading_icon
from aita_lab.components.model_selector import select_chat_model, select_embedding_model
from aita_lab.states.agent import AgentState
from aita_lab.states.chat import QA, ChatState
from aita_lab.states.datasource import DataSourceState
from aita_lab.states.prompt_template import PromptTemplateState
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
        rx.text(
            "Data Source",
            asi_="div",
            mb="1",
            size="2",
            weight="bold",
        ),
        rx.chakra.form_control(
            rx.select(
                items=DataSourceState.datasource_names,
                value=ChatState.current_datasource,
                placeholder="Select a datasource",
                on_change=ChatState.set_current_datasource,
                width="12em",
            ),
            label="Datasource",
            width="100%",
        ),
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
            rx.select(
                PromptTemplateState.prompt_template_names,
                value=ChatState.current_prompt_template.prompt_template_name,
                on_change=ChatState.set_current_prompt_template,
                width="14em",
                placeholder="Select a prompt template",
            ),
            rx.dialog.root(
                rx.dialog.content(
                    rx.flex(
                        select_embedding_model(
                            ChatState.current_embedding_model, ChatState.set_current_embedding_model
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
                                        lambda x: rx.select.item(
                                            x.name, value=f"{x.name}:{x.feature}"
                                        ),
                                    ),
                                ),
                            ),
                            value=ChatState.current_vector_feature,
                            on_change=ChatState.set_current_vector_feature,
                        ),
                        rx.dialog.close(
                            rx.button(
                                "Confirm",
                                on_click=ChatState.close_vector_feature_dialog,
                            )
                        ),
                        spacing="2",
                        direction="column",
                    ),
                    padding="3",
                    margin_top="3",
                    border=styles.border,
                    border_radius=styles.border_radius,
                ),
                open=ChatState.vector_feature_dialog_open,
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
                size="2",
                weight="bold",
            ),
            rx.select(
                AgentState.agent_names,
                value=ChatState.current_chat_agent_type,
                on_change=ChatState.set_current_chat_agent_type,
                width="14em",
                placeholder="Select an agent type",
            ),
            label="Agent Type",
            width="100%",
        )
    )


def tool_args() -> rx.Component:
    return rx.flex(
        rx.cond(
            ChatState.current_tool_id is not None and ChatState.current_tool_args.length() > 0,
            rx.foreach(
                ChatState.current_tool_args,
                lambda arg: rx.box(
                    rx.text(
                        arg.name,
                        asi_="div",
                        mb="1",
                        size="2",
                        weight="bold",
                    ),
                    code_editor(
                        value=arg.value,
                        on_change=lambda x: ChatState.update_current_tool_arg(arg.name, x),
                        width="100%",
                        min_height="20e",
                        language="python",
                        theme="material",
                        font_size="1em",
                        padding="4px",
                    ),
                    padding="6px",
                ),
            ),
        ),
        border_radius=styles.border_radius,
        direction="column",
    )


def tool_panel() -> rx.Component:
    return rx.flex(
        rx.flex(
            rx.select.root(
                rx.select.trigger(),
                rx.select.content(
                    rx.select.group(
                        rx.select.label("Select a tool"),
                        rx.foreach(
                            ChatState.current_tools_as_list,
                            lambda x: rx.select.item(x.id, value=x.id),
                        ),
                    ),
                ),
                value=ChatState.current_tool_id,
                on_change=ChatState.set_current_tool_by_id,
                padding="10px",
            ),
            rx.select.root(
                rx.select.trigger(),
                rx.select.content(
                    rx.select.group(
                        rx.select.label("Tool Name"),
                        rx.foreach(
                            ChatState.current_tools_as_list,
                            lambda x: rx.select.item(x.name, value=x.name),
                        ),
                    ),
                ),
                value=ChatState.current_tool_name,
                on_change=ChatState.set_current_tool_by_name,
                padding="10px",
            ),
            rx.chakra.button(
                rx.icon(tag="play"),
                size="xs",
                on_click=ChatState.run_tool,
            ),
            rx.chakra.button(
                rx.icon(tag="circle_stop"),
                size="xs",
                on_click=ChatState.cancel_tool,
            ),
            align="center",
            spacing="2",
            width="100%",
            padding="8px",
        ),
        rx.divider(),
        tool_args(),
        spacing="1",
        direction="column",
        background_color=rx.color("mauve", 3),
    )


def tool_kernel() -> rx.Component:
    """The code editor wrapper for running tools."""
    return rx.vstack(
        rx.chakra.heading(
            "Tool Kernel",
            size="md",
        ),
        tool_panel(),
        tool_output(),
        width="40em",
        height="85vh",
        padding="10px",
        gap="2",
        align_items="stretch",
        background_color=rx.color("mauve", 2),
        color=rx.color("mauve", 12),
        border=f"1px solid {rx.color('accent', 10)}",
        border_radius=styles.border_radius,
    )


def tool_output() -> rx.Component:
    return rx.box(
        rx.cond(
            ChatState.run_tool_output.show,
            rx.box(
                rx.badge(
                    "Output",
                    asi_="div",
                    mb="1",
                    size="3",
                    weight="bold",
                    padding="4px",
                ),
                rx.cond(
                    ChatState.run_tool_output.show,
                    rx.data_table(
                        data=ChatState.run_tool_output.data,
                        width="38em",
                        pagination=True,
                        search=True,
                        sort=True,
                        resizable=True,
                    ),
                ),
                width="100%",
                height="30em",
            ),
        ),
    )


@template(
    route="/",
    title="Chat",
    on_load=[
        ChatState.on_load,
        DataSourceState.on_load,
        PromptTemplateState.on_load,
        AgentState.on_load,
        VectorStoreState.on_load,
    ],
)
def chat() -> rx.Component:
    """The main app."""
    return rx.chakra.flex(
        rx.chakra.box(
            rx.chakra.hstack(
                select_chat_model(
                    ChatState.current_chat_model,
                    ChatState.set_current_chat_model,
                    style={"width": "12em"},
                ),
                prompt_template_selector(),
                datasource_selector(),
                agent_selector(),
                padding="4",
                width="100%",
                background_color=rx.color("mauve", 2),
                color=rx.color("mauve", 12),
                border_left=f"1px solid {rx.color('mauve', 3)}",
                top="0",
                spacing="4",
                align_items="stretch",
            ),
            rx.chakra.vstack(
                chat_history(),
                action_bar(),
                background_color=rx.color("mauve", 1),
                color=rx.color("mauve", 12),
                height="80vh",
                align_items="stretch",
                spacing="0",
                padding="20px",
                overflow_y="scroll",
            ),
            flex_grow=1,
        ),
        rx.chakra.grid_item(
            tool_kernel(),
            width="100%",
        ),
        h="100vh",
        width="100%",
        gap="2",
        direction="row",
        overflow_y="hidden",
    )
