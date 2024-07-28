"""The data catalog page """

import reflex as rx

from aita_lab.states.catalog import CatalogState, CatalogTable
from aita_lab.templates import template
from aita_lab.states.datasource import DataSourceState


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
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.flex("Add Data Catalog", rx.icon(tag="plus", width=24, height=24), spacing="3"),
                size="4",
                radius="full",
                on_click=CatalogState.toggle_dialog,
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
                "Select the data source to add a data catalog",
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
                    rx.button(
                        "Add",
                        size="2",
                        on_click=CatalogState.crawl_data_catalog
                    ),
                ),
                rx.dialog.close(
                    rx.button(
                        "Cancel",
                        variant="soft",
                        color_scheme="gray",
                        on_click=DataSourceState.toggle_dialog,
                    )
                ),
                padding_top="1em",
                spacing="3",
                mt="4",
                justify="end",
            ),
        ),
    )


def show_catalog(catalog: CatalogTable):
    return rx.table.row(
        rx.table.cell(catalog.catalog_name),
        rx.table.cell(catalog.schema),
        rx.table.cell(catalog.table),
        rx.table.cell(catalog.datasource_name),
        rx.table.cell(
            rx.button(
                "Delete",
                on_click=lambda: CatalogState.delete_catalog(catalog),
            )
        ),
    )


def catalog_grid():
    return rx.fragment(
        rx.vstack(
            rx.box(
                add_data_catalog(),
            ),
            rx.hstack(
                rx.select.root(
                    rx.select.trigger(
                        placeholder=f"Sort By:",
                    ),
                    rx.select.content(
                        rx.select.group(
                            rx.select.item("Catalog", value="catalog_name"),
                            rx.select.item("Schema", value="feature"),
                            rx.select.item("Table", value="table"),
                            rx.select.item("Data Source", value="datasource_name"),
                        )
                    ),
                    size="3",
                    value=CatalogState.sort_value,
                    on_change=lambda sort_value: CatalogState.sort_values(sort_value),
                    font_family="Inter",
                ),
                width="100%",
                padding_top="2em",
                padding_bottom="1em",
            ),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Catalog Name"),
                        rx.table.column_header_cell("Schema"),
                        rx.table.column_header_cell("Table"),
                        rx.table.column_header_cell("Data Source"),
                        rx.table.column_header_cell("Delete"),
                    ),
                ),
                rx.table.body(rx.foreach(CatalogState.catalogs, show_catalog)),
                # variant="surface",
                size="3",
                width="100%",
                justify="stretch",
            ),
            margin_top="20px",
        ),
    )


@template(route="/catalog", title="Data Catalog", on_load=[
    CatalogState.on_load(),
    DataSourceState.on_load(),
])
def catalog():
    return rx.vstack(
        rx.heading("Data Catalog", size="8"),
        rx.text("View your data catalog"),
        rx.box(
            catalog_search(),
            catalog_grid(),
            width="100%",
        ),
        width="100%",
    )
