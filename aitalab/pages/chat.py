"""The chat page."""

from aitalab.templates import template
import reflex as rx
from aitalab.states.chat import QA, ChatState
from aitalab.components.loading_icon import loading_icon
from aitalab.styles import message_style


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
    return rx.chakra.form(
        rx.chakra.form_control(
            rx.text(
                "Model",
                asi_="div",
                mb="1",
                size="2",
                weight="bold",
            ),
            rx.chakra.select(
                ["gpt-3.5-turbo"],
                value=ChatState.current_model,
                on_change=ChatState.set_current_model,
            ),
            label="Model",
        ),
        padding_y="2",
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
            rx.chakra.select(
                ["datasource1", "datasource2"],
                value=ChatState.current_datasource,
                on_change=ChatState.set_current_datasource,
            ),
            label="Datasource",
        ),
        padding_y="2",
    )


@template(route="/", title="Chat")
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
                col_span=1,
                padding="4",
                width="100%",
                max_width="20em",
                background_color=rx.color("mauve", 2),
                color=rx.color("mauve", 12),
                border_left=f"1px solid {rx.color('mauve', 3)}",
                top="0",
                spacing="4"
            ),
            col_span=1,
        ),
        h="100vh",
        width="100%",
        template_columns="repeat(4, 1fr)",
        template_rows="1fr",
        gap="2",
    )
