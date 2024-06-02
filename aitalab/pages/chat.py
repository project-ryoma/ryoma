"""The chat page."""

import reflex as rx

from aitalab.components.codeeditor import code_editor
from aitalab.components.loading_icon import loading_icon
from aitalab.states.agent import AgentState
from aitalab.states.chat import QA, ChatState
from aitalab.states.datasource import DataSourceState
from aitalab.states.llm_providers import ModelProvider
from aitalab.states.prompt_template import PromptTemplateState
from aitalab.styles import message_style
from aitalab.templates import template


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
                **message_style,
            ),
            text_align="left",
            padding_top="1em",
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
        overflow="hidden",
        padding_bottom="5em",
    )


def action_bar() -> rx.Component:
    """The action bar to send a new message."""
    return rx.center(
        rx.vstack(
            rx.chakra.form(
                rx.chakra.form_control(
                    rx.hstack(
                        rx.radix.text_field.root(
                            rx.radix.text_field.input(
                                placeholder="Type something...",
                                id="question",
                                width=["15em", "20em", "45em", "50em", "50em", "50em"],
                            ),
                            rx.radix.text_field.slot(
                                rx.tooltip(
                                    rx.icon("info", size=18),
                                    content="Enter a question to get a response.",
                                )
                            ),
                        ),
                        rx.button(
                            rx.cond(
                                ChatState.processing,
                                loading_icon(height="1em"),
                                rx.text("Send"),
                            ),
                            type="submit",
                        ),
                        align_items="center",
                    ),
                    is_disabled=ChatState.processing,
                ),
                on_submit=ChatState.process_question,
                reset_on_submit=True,
            ),
            rx.text(
                "Aita may return factually incorrect or misleading responses. Use discretion.",
                text_align="center",
                font_size=".75em",
                color=rx.color("mauve", 10),
            ),
            align_items="center",
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


def model_selector() -> rx.Component:
    """The model selector."""
    return rx.form(
        rx.chakra.form_control(
            rx.text(
                "Model",
                asi_="div",
                mb="1",
                size="2",
                weight="bold",
            ),
            rx.select.root(
                rx.select.trigger(
                    placeholder="Select a model",
                    width="100%"
                ),
                rx.select.content(
                    *[
                        rx.select.group(
                            rx.select.label(p.value.name),
                            rx.foreach(p.value.models,
                                       lambda x: rx.select.item(x, value=f"{p.value.id}:{x}")
                                       ),
                            width="100%",
                        ) for p in list(ModelProvider)
                    ],
                    width="100%",
                ),
                value=ChatState.current_model,
                on_change=ChatState.set_current_model,
                default_value="gpt-3.5-turbo",
                width="100%",
            ),
            label="Model",
            width="100%",
        ),
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
                width="100%",
            ),
            label="Datasource",
            width="100%",
        ),
        padding_y="2",
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
                value=ChatState.current_prompt_template,
                on_change=ChatState.set_current_prompt_template,
                width="100%",
                placeholder="Select a prompt template",
            ),
            label="Prompt Template",
            width="100%",
        ),
        padding_y="2",
    )


def agent_type_selector() -> rx.Component:
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
                AgentState.agent_types,
                value=ChatState.current_agent_type,
                on_change=ChatState.set_current_agent_type,
                width="100%",
                placeholder="Select an agent type",
            ),
            label="Agent Type",
            width="100%",
        ),
        padding_y="2",
    )


def code_editor_wrapper() -> rx.Component:
    """The code editor wrapper."""
    return rx.chakra.form(
        rx.chakra.form_control(
            rx.text(
                "Kernel",
                asi_="div",
                mb="1",
                size="2",
                weight="bold",
            ),
            rx.cond(
                ChatState.current_tools,
                rx.chakra.box(
                    rx.flex(
                        rx.select(
                            ChatState.current_tool_ids,
                            value=ChatState.current_tool,
                            on_change=ChatState.set_current_tool,
                            placeholder="Select a tool",
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
                    ),
                    rx.foreach(
                        ChatState.current_tools,
                        lambda current_tool: rx.box(
                            rx.foreach(
                                current_tool.args,
                                lambda arg: rx.box(
                                    code_editor(
                                        value=arg[1],
                                        on_change=lambda x: ChatState.set_current_tool_arg(current_tool.id, arg[0], x),
                                        width="100%",
                                        language="python",
                                        theme="material",
                                        font_size="1em",
                                        margin_top="10px",
                                    ),
                                )
                            )
                        )
                    )
                )
            )
        ),
        padding_y="2",
    )


@template(route="/", title="Chat", on_load=[DataSourceState.on_load, PromptTemplateState.on_load])
def chat() -> rx.Component:
    """The main app."""
    return rx.chakra.grid(
        rx.chakra.grid_item(
            rx.chakra.vstack(
                chat_history(),
                action_bar(),
                background_color=rx.color("mauve", 1),
                color=rx.color("mauve", 12),
                min_height="100vh",
                align_items="stretch",
                spacing="0",
            ),
            col_span=3,
        ),
        rx.chakra.grid_item(
            rx.chakra.vstack(
                model_selector(),
                datasource_selector(),
                prompt_template_selector(),
                agent_type_selector(),
                code_editor_wrapper(),
                col_span=1,
                padding="4",
                width="100%",
                max_width="20em",
                background_color=rx.color("mauve", 2),
                color=rx.color("mauve", 12),
                border_left=f"1px solid {rx.color('mauve', 3)}",
                top="0",
                spacing="4",
                align_items="stretch",
            ),
            col_span=1,
        ),
        h="100vh",
        width="100%",
        template_columns="repeat(4, 1fr)",
        template_rows="1fr",
        gap="2",
    )
