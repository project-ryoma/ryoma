"""The Prompt template Page."""

import reflex as rx

from aita_lab.states.prompt_template import PromptTemplateState
from aita_lab.templates import template


def content_grid():
    """Create a content grid."""
    return rx.chakra.flex(
        rx.foreach(
            PromptTemplateState.prompt_templates,
            lambda pt: rx.chakra.card(
                rx.chakra.vstack(
                    rx.foreach(pt.prompt_lines, lambda line: rx.chakra.text(line, padding="2px")),
                    align_items="flex-start",
                ),
                header=rx.chakra.heading(pt.prompt_template_name, size="md"),
                # adjust the size and make it scrollable
                direction="column",
                overflow="auto",
                height="300px",
                width="50%",
                margin_right="20px",
            ),
        )
    )


def render_question():
    return rx.box(
        rx.chakra.text("A list of prompt templates for question:", size="md"),
        rx.chakra.badge(
            PromptTemplateState.question, margin_top="10px", font_size="md", padding="2px"
        ),
    )


@template(route="/prompt_template", title="Prompt Template", on_load=PromptTemplateState.on_load())
def prompt_template() -> rx.Component:
    """The prompt template page.

    Returns:
        The UI for the prompt template page.
    """
    return rx.vstack(
        rx.heading("Prompt Template", size="8"),
        render_question(),
        rx.box(
            content_grid(),
            margin_top="20px",
            width="100%",
        ),
        # make the page full width
        width="100%",
    )
