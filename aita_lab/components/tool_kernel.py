from typing import Optional

import reflex as rx

from aita_lab import styles
from aita_lab.components.code_editor import codeeditor
from aita_lab.states.tool import Tool, ToolOutput
from aita_lab.states.tool_calls import ToolCall


def tool_args(
    tool: Tool,
    update_tool_args: Optional[rx.event.EventHandler] = None,
    render_only: bool = False,
) -> rx.Component:
    return rx.flex(
        rx.cond(
            tool.args & tool.args.length() > 0,
            rx.foreach(
                tool.args,
                lambda arg: rx.box(
                    rx.text(
                        arg.name, asi_="div", mb="1", size="2", weight="bold", padding_left="4px"
                    ),
                    rx.cond(
                        render_only,
                        rx.text(arg.value, asi_="div", mb="1", size="2", padding_left="4px"),
                        codeeditor(
                            value=arg.value,
                            on_change=lambda x: update_tool_args(x),
                            width="100%",
                            min_height="20e",
                            language="python",
                            theme="material",
                            font_size="1em",
                            padding="4px",
                        ),
                    ),
                ),
            ),
        ),
        border_radius=styles.border_radius,
        direction="column",
        padding="8px",
    )


def render_tool_output(tool_output: ToolOutput) -> rx.Component:
    return rx.box(
        rx.chakra.badge(
            "Output",
            asi_="div",
            mb="1",
            size="3",
            weight="bold",
            padding="4px",
        ),
        rx.cond(
            tool_output.show,
            rx.data_table(
                data=tool_output.data,
                width="38em",
                pagination=True,
                search=True,
                sort=True,
                resizable=True,
            ),
        ),
        width="100%",
        padding="8px",
    )


def render_tool_panel(
    tool: Tool,
    run_tool: Optional[rx.event.EventHandler] = None,
    cancel_tool: Optional[rx.event.EventHandler] = None,
    update_tool_args: Optional[rx.event.EventHandler] = None,
    render_only: bool = False,
) -> rx.Component:
    return rx.flex(
        rx.flex(
            rx.chakra.badge(
                tool.name,
                asi_="div",
                mb="1",
                size="3",
                weight="bold",
                height="100%",
            ),
            rx.cond(
                not render_only,
                rx.chakra.button(rx.icon(tag="play"), size="xs", on_click=run_tool, height="100%"),
            ),
            rx.cond(
                not render_only,
                rx.chakra.button(
                    rx.icon(tag="circle_stop"), size="xs", on_click=cancel_tool, height="100%"
                ),
            ),
            align="center",
            spacing="2",
            width="100%",
            height="3em",
            padding="8px",
            background_color=rx.color("mauve", 5),
            align_items="center",
        ),
        tool_args(tool, update_tool_args, render_only),
        spacing="1",
        direction="column",
    )


def tool_history(
    tool_calls: list[ToolCall],
    run_tool: rx.event.EventHandler,
    cancel_tool: rx.event.EventHandler,
    update_tool_args: rx.event.EventHandler,
) -> rx.Component:
    return rx.box(
        rx.cond(
            tool_calls.length() > 0,
            rx.flex(
                rx.badge("Tool Call History"),
                rx.chakra.accordion(
                    rx.foreach(
                        tool_calls,
                        lambda tool_call: rx.chakra.accordion_item(
                            rx.chakra.accordion_button(
                                rx.chakra.text(tool_call.tool.name),
                                rx.chakra.accordion_icon(),
                            ),
                            rx.chakra.accordion_panel(
                                tool_kernel(
                                    tool_call.tool,
                                    run_tool,
                                    cancel_tool,
                                    update_tool_args,
                                    tool_call.tool_output,
                                    render_only=True,
                                )
                            ),
                        ),
                    ),
                    allow_multiple=True,
                    width="100%",
                ),
                direction="column",
                width="100%",
                overflow="auto",
            ),
        ),
    )


def tool_kernel(
    tool: Optional[Tool] = None,
    run_tool: Optional[rx.event.EventHandler] = None,
    cancel_tool: Optional[rx.event.EventHandler] = None,
    update_tool_args: Optional[rx.event.EventHandler] = None,
    tool_output: Optional[ToolOutput] = None,
    render_only: bool = False,
) -> rx.Component:
    return rx.flex(
        rx.cond(
            tool,
            rx.flex(
                rx.badge("Tool Kernel"),
                render_tool_panel(tool, run_tool, cancel_tool, update_tool_args, render_only),
                direction="column",
                width="100%",
            ),
        ),
        rx.divider(),
        rx.cond(
            tool_output & tool_output.show,
            render_tool_output(tool_output),
        ),
        direction="column",
        background_color=rx.color("mauve", 3),
    )


def notebook(
    tool: Tool,
    run_tool: rx.event.EventHandler,
    cancel_tool: rx.event.EventHandler,
    update_tool_args: rx.event.EventHandler,
    tool_output: ToolOutput,
    tool_calls: list[ToolCall] = None,
) -> rx.Component:
    """The code editor wrapper for running tools."""
    return rx.vstack(
        rx.chakra.heading(
            "Notebook",
            size="md",
        ),
        tool_history(tool_calls, run_tool, cancel_tool, update_tool_args),
        tool_kernel(tool, run_tool, cancel_tool, update_tool_args, tool_output),
        width="40em",
        height="85vh",
        padding="10px",
        gap="2",
        align_items="stretch",
        background_color=rx.color("mauve", 2),
        color=rx.color("mauve", 12),
        border=f"1px solid {rx.color('accent', 10)}",
        border_radius=styles.border_radius,
        overflow="auto",
    )
