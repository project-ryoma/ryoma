from typing import Optional, Union

import pandas as pd
import reflex as rx
from ryoma_lab.models.cell import (
    CellOutput,
    DataframeOutput,
    ErrorOutput,
    ExecuteResultOutput,
    StreamOutput,
    UnknownOutput,
)
from ryoma_lab.states.workspace import WorkspaceState


def render_dataframe(item: DataframeOutput) -> rx.Component:
    return rx.data_table(data=item.dataframe)


def render_error_output(item: ErrorOutput) -> rx.Component:
    return rx.vstack(
        rx.text(f"{item.ename}: {item.evalue}", color="red"),
        rx.code(item.traceback, language="python", color_scheme="gray"),
        align_items="stretch",
        width="100%",
    )


def render_output_item(
    item: Union[
        CellOutput,
        StreamOutput,
        ExecuteResultOutput,
        DataframeOutput,
        ErrorOutput,
        UnknownOutput,
    ]
) -> rx.Component:
    return rx.box(
        rx.cond(
            item.output_type == "stream",
            render_stream_output(item),
            rx.cond(
                item.output_type == "execute_result",
                render_execute_result(item),
                rx.cond(
                    item.output_type == "dataframe",
                    render_dataframe(item),
                    rx.cond(
                        item.output_type == "error",
                        render_error_output(item),
                        rx.text("Unknown output type"),
                    ),
                ),
            ),
        )
    )


def render_stream_output(item: StreamOutput) -> rx.Component:
    return rx.text(item.text)


def render_execute_result(item: ExecuteResultOutput) -> rx.Component:
    if WorkspaceState.data_contains_html(item):
        return rx.html(f"{WorkspaceState.get_html_content(item)}")
    elif WorkspaceState.data_contains_image(item):
        return rx.image(
            src=f"data:image/png;base64,{WorkspaceState.get_image_content(item)}"
        )
    else:
        return rx.markdown(f"```{WorkspaceState.get_plain_text_content(item)}```")


def render_output(
    output: list[
        Union[
            StreamOutput,
            ExecuteResultOutput,
            DataframeOutput,
            ErrorOutput,
            UnknownOutput,
        ]
    ]
) -> rx.Component:
    return rx.vstack(rx.foreach(output, render_output_item))
