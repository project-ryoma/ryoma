"""The data catalog page """

import reflex as rx

from ryoma_lab import styles
from ryoma_lab.states.catalog import CatalogState
from ryoma_lab.states.datasource import DataSourceState
from ryoma_lab.templates import template


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
    )


def add_data_catalog():
    return rx.vstack(
        rx.dialog.root(
            rx.dialog.trigger(
                rx.button(
                    rx.flex(
                        "Add Data Catalog", rx.icon(tag="plus", width=24, height=24), spacing="3"
                    ),
                    size="4",
                    radius="full",
                ),
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
                rx.select(
                    DataSourceState.datasource_names,
                    on_change=CatalogState.set_current_datasource,
                    placeholder="Select Data Source",
                ),
                rx.flex(
                    rx.dialog.close(
                        rx.button("Add", size="2", on_click=CatalogState.crawl_data_catalog),
                    ),
                    rx.dialog.close(
                        rx.button(
                            "Cancel",
                            variant="soft",
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
        margin_top="20px",
    )


def catalog_list():
    return rx.vstack(
        rx.chakra.accordion(
            rx.foreach(
                CatalogState.catalogs,
                lambda catalog: rx.chakra.accordion_item(
                    rx.chakra.accordion_button(
                        rx.chakra.accordion_icon(),
                        rx.chakra.heading(catalog.database, size="md"),
                    ),
                    rx.chakra.accordion_panel(
                        rx.chakra.accordion(
                            rx.foreach(
                                catalog.schemas,
                                lambda schema: rx.chakra.accordion_item(
                                    rx.chakra.accordion_button(
                                        rx.chakra.accordion_icon(),
                                        rx.chakra.text(schema.name, font_size="md"),
                                    ),
                                    rx.chakra.accordion_panel(
                                        rx.chakra.accordion(
                                            rx.foreach(
                                                schema.tables,
                                                lambda table: rx.chakra.accordion_item(
                                                    rx.chakra.accordion_button(
                                                        rx.chakra.text(table.name, font_size="xs"),
                                                        on_click=lambda: CatalogState.set_selected_table(
                                                            table.name
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
                width="100%",
            ),
            allow_multiple=True,
            min_width="300px",
        ),
        margin_top="20px",
    )


def render_metadata_content():
    return rx.flex(
        rx.chakra.heading(CatalogState.table_metadata.name, size="md"),
        rx.cond(
            CatalogState.table_metadata.description,
            rx.text(CatalogState.table_metadata.description),
        ),
        rx.chakra.table(
            rx.chakra.thead(
                rx.chakra.th("Column Name"),
                rx.chakra.th("Type"),
                rx.chakra.th("Description"),
                background_color=rx.color("mauve", 6),
            ),
            rx.chakra.tbody(
                rx.foreach(
                    CatalogState.table_metadata.columns,
                    lambda column: rx.chakra.tr(
                        rx.chakra.td(column.name),
                        rx.chakra.td(column.type),
                        rx.chakra.td(column.description),
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
        catalog_list(),
        rx.cond(
            CatalogState.selected_table,
            render_metadata_content(),
        ),
        spacing="3",
        width="100%",
    )


@template(
    route="/catalog",
    title="Data Catalog",
    on_load=[
        CatalogState.on_load(),
        DataSourceState.on_load(),
    ],
)
def catalog():
    return rx.vstack(
        rx.heading("Data Catalog", size="8"),
        rx.text("View your data catalog"),
        rx.box(
            catalog_search(),
            add_data_catalog(),
            render_catalog_body(),
            width="100%",
        ),
        width="100%",
    )
