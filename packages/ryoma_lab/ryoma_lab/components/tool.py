"""The Tool Page."""

import reflex as rx
from ryoma_lab.states.tool import Tool, ToolState
from ryoma_lab.templates import template


def tool_card(tool: Tool):
    """Create a tool card."""
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.chakra.card(
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
                cursor="pointer",
                _hover={"background_color": rx.color("gray", 2)},
            ),
        ),
        rx.dialog.content(
            rx.dialog.title(tool.name, size="6"),
            rx.dialog.description(tool.description),
            rx.vstack(
                rx.heading("Tool Arguments", size="4"),
                rx.foreach(
                    tool.args,
                    lambda arg: rx.flex(
                        rx.text(
                            arg.name,
                            as_="div",
                            size="2",
                            mb="1",
                            weight="bold",
                        ),
                        rx.cond(
                            arg.description is not None,
                            rx.text(
                                arg.description,
                            ),
                        ),
                        direction="column",
                        spacing="3",
                    ),
                ),
                margin_top="20px",
                width="100%",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button("Close", size="2"),
                ),
                justify="end",
            ),
        ),
    )


def content_grid():
    """Create a content grid."""
    return rx.chakra.flex(
        rx.foreach(
            ToolState.tools,
            lambda tool: tool_card(tool),
        ),
        flex_wrap="wrap",
    )


def tool_component() -> rx.Component:
    return rx.vstack(
        rx.chakra.text("A suite of tools to help you with analyzing your data."),
        rx.box(
            content_grid(),
            margin_top="20px",
            width="100%",
        ),
        # make the page full width
        width="100%",
    )
