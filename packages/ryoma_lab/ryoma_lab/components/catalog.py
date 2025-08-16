"""The data catalog page """

import reflex as rx
import reflex_chakra as rc
from ryoma_ai.datasource.metadata import Table
from ryoma_lab import styles
from ryoma_lab.states.catalog import CatalogState
from ryoma_lab.states.datasource import DataSourceTable
from ryoma_lab.states.vector_store import VectorStoreState


def catalog_search():
    return rx.flex(
        rx.input(
            placeholder="Search for a table or column",
            width="100%",
        ),
        rx.button("Search"),
        spacing="3",
        justify="center",
        align="center",
        width="100%",
        margin_y="10px",
    )


def render_catalog_list():
    return rx.vstack(
        rc.accordion(
            rx.foreach(
                CatalogState.catalogs,
                lambda catalog: rc.accordion_item(
                    rc.accordion_button(
                        rc.accordion_icon(),
                        rc.heading(catalog.catalog_name, size="md"),
                    ),
                    rc.accordion_panel(
                        rc.accordion(
                            rx.foreach(
                                catalog.schemas,
                                lambda schema: rc.accordion_item(
                                    rc.accordion_button(
                                        rc.accordion_icon(),
                                        rc.text(
                                            schema.schema_name, font_size="md"
                                        ),
                                    ),
                                    rc.accordion_panel(
                                        rc.accordion(
                                            rx.foreach(
                                                schema.tables,
                                                lambda table: rc.accordion_item(
                                                    rc.accordion_button(
                                                        rc.text(
                                                            table.table_name,
                                                            font_size="xs",
                                                        ),
                                                        on_click=lambda: CatalogState.set_selected_table(
                                                            table.table_name
                                                        ),
                                                    ),
                                                ),
                                            ),
                                            allow_multiple=True,
                                        )
                                    ),
                                ),
                            ),
                            allow_multiple=True,
                        )
                    ),
                ),
            ),
            allow_multiple=True,
            min_width="300px",
        ),
        border=styles.border,
        border_radius=styles.border_radius,
        padding="1em",
        min_height="40vh",
    )


def render_metadata_content():
    return rx.flex(
        rx.hstack(
            rx.heading(CatalogState.table_metadata.table_name),
            index_data_catalog_render(CatalogState.table_metadata),
            width="100%",
        ),
        rx.cond(
            CatalogState.table_metadata.description,
            rx.text(CatalogState.table_metadata.description),
        ),
        rc.table(
            rc.thead(
                rc.th("Column Name"),
                rc.th("Type"),
                rc.th("Description"),
                background_color=rx.color("mauve", 6),
            ),
            rc.tbody(
                rx.foreach(
                    CatalogState.table_metadata.columns,
                    lambda column: rc.tr(
                        rc.td(column.name),
                        rc.td(column.type),
                        rc.td(column.description),
                    ),
                ),
                background_color=rx.color("mauve", 3),
            ),
        ),
        direction="column",
        width="100%",
        spacing="3",
        border=styles.border,
        border_radius=styles.border_radius,
        padding="1em",
    )


def render_catalog_body():
    return rx.flex(
        render_catalog_list(),
        rx.cond(
            CatalogState.selected_table,
            render_metadata_content(),
        ),
        spacing="3",
        width="100%",
    )


def sync_data_catalog_render(
    datasource: DataSourceTable,
):
    return rx.vstack(
        rx.dialog.root(
            rx.dialog.trigger(
                rx.button("Sync"),
            ),
            rx.dialog.content(
                rx.dialog.title(
                    "Connect and Add Data Catalog",
                    size="1",
                    font_family="Inter",
                    padding_top="1em",
                ),
                rx.dialog.description(
                    "Currently only support adding catalogs from data sources. "
                    + "Please select a data source to crawl the catalog.",
                    size="2",
                    mb="4",
                    padding_bottom="1em",
                ),
                rx.flex(
                    rx.dialog.close(
                        rx.button(
                            "Sync",
                            size="2",
                            on_click=lambda: CatalogState.sync_catalog(datasource.name),
                        ),
                    ),
                    rx.dialog.close(
                        rx.button(
                            "Cancel",
                            variant="outline",
                            color_scheme="gray",
                        )
                    ),
                    padding_top="1em",
                    spacing="3",
                    mt="4",
                    justify="end",
                ),
            ),
        ),
    )


def index_data_catalog_render(
    table: Table,
):
    return rx.vstack(
        rx.dialog.root(
            rx.dialog.trigger(
                rx.button("Index"),
            ),
            rx.dialog.content(
                rx.dialog.title(
                    "Embed and Index Data Source",
                    size="1",
                    font_family="Inter",
                    padding_top="1em",
                ),
                rx.dialog.description(
                    "Index data source to enable search and discovery. ",
                    size="2",
                    mb="4",
                    padding_bottom="1em",
                ),
                rx.select.root(
                    rx.select.trigger(
                        placeholder="Select Vector Store",
                        width="100%",
                    ),
                    rx.select.content(
                        rx.foreach(
                            VectorStoreState.document_projects,
                            lambda project: rx.select.item(
                                project.project_name,
                                value=project.project_name,
                            ),
                        )
                    ),
                    value=CatalogState.vector_store_project_name,
                    on_change=CatalogState.set_vector_store_project_name,
                ),
                rx.flex(
                    rx.dialog.close(
                        rx.button(
                            "Start",
                            size="2",
                            on_click=lambda: CatalogState.index_table(table),
                        ),
                    ),
                    rx.dialog.close(
                        rx.button(
                            "Cancel",
                            variant="outline",
                            color_scheme="gray",
                        )
                    ),
                    padding_top="1em",
                    spacing="3",
                    mt="4",
                    justify="end",
                ),
            ),
        ),
    )
