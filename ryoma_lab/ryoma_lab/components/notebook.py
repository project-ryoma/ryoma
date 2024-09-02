import reflex as rx

from ryoma_lab import styles
from ryoma_lab.components.cell import render_output
from ryoma_lab.components.code_editor import codeeditor
from ryoma_lab.states.notebook import Cell, NotebookState


def notebook_panel() -> rx.Component:
    return rx.flex(
        rx.input(
            placeholder="Enter filename",
            value=NotebookState.notebook_filename,
            on_change=NotebookState.set_notebook_filename,
            size="2",
        ),
        rx.select(
            ["python", "sql"],
            placeholder="Select Kernel",
            on_change=NotebookState.set_kernel_type,
            size="2",
        ),
        rx.button(
            "Run All",
            on_click=NotebookState.run_all_cells,
            variant="outline",
            size="2",
        ),
        rx.button(
            "Restart Kernel",
            on_click=NotebookState.restart_kernel,
            variant="outline",
            size="2",
        ),
        rx.button(
            "Clear All Outputs",
            on_click=NotebookState.clear_all_outputs,
            variant="outline",
            size="2",
        ),
        rx.button(
            "Save",
            on_click=NotebookState.save_notebook,
            variant="outline",
            size="2",
        ),
        justify="start",
        spacing="2",
        width="100%",
        border_radius=styles.border_radius,
    )


def add_cell_button(index: int, position: str) -> rx.Component:
    return rx.button(
        rx.icon("circle_plus", size=18),
        on_click=lambda: NotebookState.add_cell_at(index, position),
        variant="ghost",
        padding="0",
        min_width="20px",
        height="20px",
        cursor="pointer",
    )


def cell_render(cell: Cell, index: int) -> rx.Component:
    return rx.hstack(
        rx.vstack(
            add_cell_button(index, "before"),
            rx.spacer(),
            add_cell_button(index + 1, "after"),
            height="100%",
            width="12px",
            align_items="center",
        ),
        rx.box(
            rx.flex(
                rx.select(
                    ["code", "markdown"],
                    value=cell.cell_type,
                    on_change=lambda x: NotebookState.set_cell_type(index, x),
                    size="2",
                ),
                rx.button(
                    "Run",
                    on_click=lambda: NotebookState.execute_cell(index),
                    variant="solid",
                    size="2",
                ),
                rx.button(
                    "Delete",
                    on_click=lambda: NotebookState.delete_cell(index),
                    variant="outline",
                    size="2",
                ),
                justify="start",
                spacing="2",
                width="100%",
                padding_y="0.5em",
            ),
            rx.cond(
                cell.cell_type == "code",
                codeeditor(
                    value=cell.content,
                    on_change=lambda x: NotebookState.update_cell_content(index, x),
                    language="python",
                    extensions=rx.Var.create(
                        '[loadLanguage("sql"), loadLanguage("python")]',
                        _var_is_local=False,
                    ),
                ),
                codeeditor(
                    value=cell.content,
                    on_change=lambda x: NotebookState.update_cell_content(index, x),
                    language="markdown",
                ),
            ),
            rx.cond(
                cell.output,
                render_output(cell.output),
            ),
            border="1px solid",
            border_color=rx.color("gray", 3),
            border_radius="0.5em",
            padding="0.5em",
            width="100%",
        ),
        rx.spacer(),
        width="100%",
        align_items="stretch",
        padding="1em",
        _hover={"background_color": rx.color("gray", 3)},
    )


def notebook() -> rx.Component:
    """The notebook component."""
    return rx.vstack(
        rx.box(
            rx.heading(
                "Notebook",
                width="100%",
                size="4",
                padding_y="5px",
            ),
            notebook_panel(),
            background_color=rx.color("gray", 3),
            padding="0.5em",
        ),
        rx.cond(
            NotebookState.cells.length() == 0,
            add_cell_button(0, "only"),
        ),
        rx.foreach(
            NotebookState.cells,
            lambda cell, index: cell_render(cell, index),
        ),
        align_items="stretch",
        background_color=rx.color("white"),
        border=styles.border,
        border_radius=styles.border_radius,
        box_shadow="0 0 10px rgba(0,0,0,0.1)",
        overflow="auto",
        height="85vh",
    )
