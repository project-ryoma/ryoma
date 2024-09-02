import reflex as rx

from ryoma_lab.models.cell import CellOutput
from ryoma_lab.states.notebook import NotebookState


def render_dataframe(item: CellOutput) -> rx.Component:
    return rx.data_table(
        data=item.data,
        pagination=True,
        search=True,
        sort=True,
    )


def render_error_output(item: CellOutput) -> rx.Component:
    return rx.vstack(
        rx.text(f"{item.ename}: {item.evalue}", color="red"),
        rx.code(item.traceback, language="python", color_scheme="gray"),
        align_items="stretch",
        width="100%",
    )


def render_output_item(item: CellOutput) -> rx.Component:
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


def render_stream_output(item: CellOutput) -> rx.Component:
    return rx.text(item.text)


def render_execute_result(item: CellOutput) -> rx.Component:
    if NotebookState.data_contains_html(item):
        return rx.html(f"{NotebookState.get_html_content(item)}")
    elif NotebookState.data_contains_image(item):
        return rx.image(
            src=f"data:image/png;base64,{NotebookState.get_image_content(item)}"
        )
    else:
        return rx.markdown(f"```{NotebookState.get_plain_text_content(item)}```")


def render_output(output: list[CellOutput]) -> rx.Component:
    return rx.vstack(rx.foreach(output, render_output_item))
