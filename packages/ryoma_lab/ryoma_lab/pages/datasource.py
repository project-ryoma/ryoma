"""The home page of the app."""

import reflex as rx
from ryoma_ai.datasource.factory import get_supported_datasources
from ryoma_lab import styles
from ryoma_lab.components.catalog import (
    catalog_search,
    render_catalog_body,
    sync_data_catalog_render,
)
from ryoma_lab.states.ai import AIState
from ryoma_lab.states.catalog import CatalogState
from ryoma_lab.states.datasource import DataSourceState, DataSourceTable
from ryoma_lab.states.vector_store import VectorStoreState
from ryoma_lab.templates import template


def show_datasource(datasource_model: DataSourceTable):
    return rx.table.row(
        rx.table.cell(datasource_model.name),
        rx.table.cell(datasource_model.type),
        rx.table.cell(update_datasource(datasource_model)),
        rx.table.cell(sync_data_catalog_render(datasource_model)),
        rx.table.cell(
            rx.button(
                "Delete",
                on_click=lambda: DataSourceState.delete_datasource(datasource_model.id),
            )
        ),
    )


def show_datasource_configs():
    return rx.tabs.root(
        rx.tabs.list(
            rx.tabs.trigger("Connection URL", value="connection_url"),
            rx.tabs.trigger("Custom Config", value="custom_config"),
        ),
        rx.tabs.content(
            rx.vstack(
                rx.text(
                    DataSourceState.connection_url,
                    as_="div",
                    size="2",
                    mb="1",
                    weight="bold",
                ),
                rx.input(
                    placeholder=f"Enter the Connection URL for the data source",
                    on_blur=DataSourceState.set_connection_url,
                    width="100%",
                ),
                width="100%",
            ),
            value="connection_url",
        ),
        rx.tabs.content(
            rx.vstack(
                rx.foreach(
                    DataSourceState.datasource_attribute_names,
                    lambda attribute_name: rx.vstack(
                        rx.text(
                            attribute_name,
                            as_="div",
                            size="2",
                            mb="1",
                            weight="bold",
                        ),
                        rx.input(
                            placeholder=f"Enter the {attribute_name} for the data source",
                            value=DataSourceState.attributes[attribute_name],
                            on_change=lambda value: DataSourceState.set_datasource_attributes(
                                attribute_name, value
                            ),
                            type=rx.cond(
                                attribute_name.contains("password"), "password", "text"
                            ),
                            width="100%",
                        ),
                        width="100%",
                    ),
                ),
                width="100%",
            ),
            value="custom_config",
        ),
        default_value="connection_url",
        on_change=DataSourceState.set_config_type,
    )


def add_datasource():
    datasources = [ds.name for ds in get_supported_datasources()]
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.flex(
                    "Add Data Source",
                    rx.icon(tag="plus", width=24, height=24),
                    spacing="3",
                ),
                size="4",
                radius="full",
            ),
        ),
        rx.dialog.content(
            rx.dialog.title(
                "Connection Information",
                size="1",
                font_family="Inter",
                padding_top="1em",
            ),
            rx.dialog.description(
                "Select the data source and enter the connection information for your data source",
                size="2",
                mb="4",
                padding_bottom="1em",
            ),
            rx.flex(
                rx.text(
                    "Name *",
                    as_="div",
                    size="2",
                    mb="1",
                    weight="bold",
                ),
                rx.input(
                    placeholder="Enter the name of the data source",
                    on_blur=DataSourceState.set_name,
                    required=True,
                ),
                rx.text(
                    "Data Source *",
                    as_="div",
                    size="2",
                    mb="1",
                    weight="bold",
                ),
                rx.select(
                    datasources,
                    placeholder="Select the data source",
                    value=DataSourceState.datasource,
                    on_change=DataSourceState.set_datasource,
                ),
                rx.cond(DataSourceState.datasource, show_datasource_configs()),
                direction="column",
                spacing="4",
            ),
            rx.cond(
                DataSourceState.datasource & DataSourceState.missing_configs,
                rx.callout(
                    "Please fill in all the required fields",
                    icon="info",
                    spacing="3",
                ),
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Connect",
                        on_click=DataSourceState.connect_and_add_datasource,
                        variant="solid",
                    )
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
            style={"width": 450},
            box_shadow="lg",
            padding="1em",
            border_radius="25px",
            font_family="Inter",
        ),
    )


def update_datasource(datasource: DataSourceTable):
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("square_pen", width=24, height=24),
                on_click=DataSourceState.toggle_update_datasource_dialog(datasource),
            ),
        ),
        rx.dialog.content(
            rx.dialog.title("Data Source Details"),
            rx.dialog.description(
                "Update your data source details.",
                size="2",
                mb="4",
                padding_bottom="1em",
            ),
            rx.flex(
                rx.text(
                    "Name",
                    as_="div",
                    size="2",
                    mb="1",
                    weight="bold",
                ),
                rx.input(
                    placeholder=datasource.name,
                    default_value=datasource.name,
                    on_blur=DataSourceState.set_name,
                ),
                show_datasource_configs(),
                direction="column",
                spacing="3",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancel",
                        variant="soft",
                        color_scheme="gray",
                    ),
                ),
                rx.dialog.close(
                    rx.button(
                        "Update",
                        on_click=lambda: DataSourceState.update_datasource(
                            datasource.id
                        ),
                        variant="solid",
                    ),
                ),
                padding_top="1em",
                spacing="3",
                mt="4",
                justify="end",
            ),
            style={"max_width": 450},
            box_shadow="lg",
            padding="1em",
            border_radius="25px",
        ),
    )


def data_source_table() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.heading(
                f"Total: {DataSourceState.num_datasources} datasources",
                size="5",
                font_family="Inter",
            ),
            rx.spacer(),
            rx.select(
                ["name", "type", "connection_url"],
                placeholder="Sort By: Name",
                size="3",
                on_change=lambda sort_value: DataSourceState.sort_values(sort_value),
                font_family="Inter",
            ),
            width="100%",
        ),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Name"),
                    rx.table.column_header_cell("Data Source"),
                    rx.table.column_header_cell("Update"),
                    rx.table.column_header_cell("Catalog"),
                    rx.table.column_header_cell("Delete"),
                ),
            ),
            rx.table.body(rx.foreach(DataSourceState.datasources, show_datasource)),
            size="6",
            width="100%",
            justify="stretch",
            variant="surface",
        ),
        width="100%",
        border=styles.border,
        border_radius=styles.border_radius,
        padding="1em",
    )


@template(
    route="/datasource",
    title="Data Source",
    on_load=[
        DataSourceState.on_load,
        CatalogState.on_load,
        VectorStoreState.on_load,
        AIState.on_load,
    ],
)
def datasource() -> rx.Component:
    """The Data Source page.

    Returns:
        The UI for the Data Source page.
    """
    return rx.vstack(
        rx.heading("Data Source", size="8"),
        rx.text("Connect to your data source"),
        rx.box(
            rx.vstack(
                add_datasource(),
                catalog_search(),
                rx.divider(),
                data_source_table(),
                render_catalog_body(),
            ),
            margin_top="10px",
            width="100%",
        ),
        width="100%",
    )
