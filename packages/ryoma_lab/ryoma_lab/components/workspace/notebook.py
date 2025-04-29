import reflex as rx
from ryoma_lab import styles
from ryoma_lab.components.code_editor import codeeditor
from ryoma_lab.components.workspace.cell import render_output
from ryoma_lab.models.cell import Cell
from ryoma_lab.states.datasource import DataSourceState
from ryoma_lab.states.workspace import WorkspaceState


def datasource_selector() -> rx.Component:
    """The type selector."""
    return rx.hstack(
        rx.select.root(
            rx.select.trigger(placeholder="Select Data Source", width="10em"),
            rx.select.content(
                rx.select.group(
                    rx.select.label("Connected Data Source"),
                    rx.cond(
                        DataSourceState.catalogs,
                        rx.foreach(
                            DataSourceState.catalogs,
                            lambda catalog: rx.select.item(
                                catalog.catalog_name, value=catalog.catalog_name
                            ),
                        ),
                    ),
                    width="100%",
                ),
                rx.select.group(
                    rx.select.item("Create new data source + ", value="custom"),
                ),
                width="100%",
                position="popper",
                side="bottom",
            ),
            on_change=WorkspaceState.set_catalog_name,
            open=WorkspaceState.catalog_dialog_open,
            on_open_change=WorkspaceState.toggle_catalog_dialog,
        ),
        rx.cond(
            WorkspaceState.schemas.length() > 0,
            rx.select.root(
                rx.select.trigger(placeholder="Select your schema", width="10em"),
                rx.select.content(
                    rx.select.group(
                        rx.select.label("Schema"),
                        rx.foreach(
                            WorkspaceState.schemas,
                            lambda schema: rx.select.item(
                                schema.schema_name, value=schema.schema_name
                            ),
                        ),
                    ),
                    width="100%",
                    position="popper",
                    side="bottom",
                ),
                open=WorkspaceState.schema_dialog_open,
                on_open_change=WorkspaceState.toggle_schema_dialog,
                value=WorkspaceState.current_schema_name,
                on_change=WorkspaceState.set_current_schema_name,
                width="100%",
            ),
        ),
        width="100%",
    )


def notebook_panel() -> rx.Component:
    return rx.vstack(
        rx.flex(
            rx.input(
                placeholder="Enter filename",
                value=WorkspaceState.notebook_filename,
                on_change=WorkspaceState.set_notebook_filename,
                size="2",
                min_width="10em",
            ),
            rx.select(
                ["python", "sql"],
                default_value="sql",
                placeholder="Select Kernel",
                on_change=WorkspaceState.set_kernel_type,
                width="10em",
                size="2",
                min_width="10em",
            ),
            datasource_selector(),
            spacing="2",
        ),
        rx.flex(
            rx.button(
                "Run All",
                on_click=WorkspaceState.run_all_cells,
                variant="outline",
                size="2",
            ),
            rx.button(
                "Restart Kernel",
                on_click=WorkspaceState.restart_kernel,
                variant="outline",
                size="2",
            ),
            rx.button(
                "Clear All Outputs",
                on_click=WorkspaceState.clear_all_outputs,
                variant="outline",
                size="2",
            ),
            rx.button(
                "Save",
                on_click=WorkspaceState.save_notebook,
                variant="outline",
                size="2",
            ),
            justify="start",
            spacing="2",
            width="100%",
            border_radius=styles.border_radius,
        ),
        width="100%",
    )


def add_cell_button(index: int, position: str) -> rx.Component:
    return rx.button(
        rx.icon("circle_plus", size=18),
        on_click=lambda: WorkspaceState.add_cell_at(index, position),
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
                    on_change=lambda x: WorkspaceState.set_cell_type(index, x),
                    size="2",
                ),
                rx.button(
                    "Run",
                    on_click=lambda: WorkspaceState.execute_cell(index),
                    variant="solid",
                    size="2",
                ),
                rx.button(
                    "Delete",
                    on_click=lambda: WorkspaceState.delete_cell(index),
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
                    on_change=lambda content: WorkspaceState.update_cell_content(
                        index, content
                    ),
                    extensions=rx.Var.create(
                        '[loadLanguage("sql"), loadLanguage("python")]',
                        _var_is_local=False,
                    ),
                ),
                codeeditor(
                    value=cell.content,
                    on_change=lambda content: WorkspaceState.update_cell_content(
                        index, content
                    ),
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
                "Kernel",
                width="100%",
                size="4",
                padding_y="5px",
            ),
            notebook_panel(),
            background_color=rx.color("gray", 3),
            padding="0.5em",
        ),
        rx.cond(
            WorkspaceState.cells.length() == 0,
            add_cell_button(0, "only"),
        ),
        rx.foreach(
            WorkspaceState.cells,
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
