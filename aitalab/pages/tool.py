"""The Tool Page."""

import reflex as rx

from aitalab.states.tool import ToolState
from aitalab.templates import template


def content_grid():
    """Create a content grid."""
    return rx.chakra.flex(
        rx.foreach(
            ToolState.tools,
            lambda tool: rx.chakra.card(
                rx.chakra.text(tool.name, padding="2px"),
                header=rx.chakra.heading(tool.name, size="md"),
                # adjust the size and make it scrollable
                direction="column",
                overflow="auto",
                height="300px",
                width="50%",
                margin_right="20px",
            ),
        )
    )


@template(route="/tool", title="Tool", on_load=ToolState.on_load())
def tool() -> rx.Component:
    """The tool page.

    Returns:
        The UI for the tool page.
    """
    return rx.vstack(
        rx.heading("Tool", size="8"),
        rx.box(
            content_grid(),
            margin_top="20px",
            width="100%",
        ),
        # make the page full width
        width="100%",
    )
