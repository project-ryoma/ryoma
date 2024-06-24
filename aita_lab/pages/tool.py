"""The Tool Page."""

import reflex as rx

from aita_lab.states.tool import ToolState
from aita_lab.templates import template


def content_grid():
    """Create a content grid."""
    return rx.chakra.flex(
        rx.foreach(
            ToolState.tools,
            lambda tool: rx.chakra.card(
                rx.chakra.text(
                    tool.description,
                    no_of_lines=3,
                ),
                header=rx.chakra.heading(tool.name, size="md"),
                # adjust the size and make it scrollable
                direction="column",
                overflow="auto",
                height="300px",
                width="200px",
                margin="20px",
            ),
        ),
        flex_wrap = "wrap"
    )


@template(route="/tool", title="Tool", on_load=ToolState.on_load())
def tool() -> rx.Component:
    """The tool page.

    Returns:
        The UI for the tool page.
    """
    return rx.vstack(
        rx.chakra.heading("Tool"),
        rx.chakra.text("A suite of tools to help you with analyzing your data."),
        rx.box(
            content_grid(),
            margin_top="20px",
            width="100%",
        ),
        # make the page full width
        width="100%",
    )
