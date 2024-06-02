"""The home page of the app."""

import reflex as rx

from aita.datasource.factory import DataSourceProvider, get_supported_datasources
from aitalab.states.datasource import DataSource, DataSourceState
from aitalab.templates import template


def show_datasource(datasource: DataSource):
    return rx.table.row(
        rx.table.cell(datasource.name),
        rx.table.cell(datasource.connection_url),
        rx.table.cell(update_datasource(datasource)),
        rx.table.cell(
            rx.button(
                "Delete",
                on_click=lambda: DataSourceState.delete_datasource(datasource),
            )
        )
    )


def add_datasource():
    datasources = [ds.name for ds in get_supported_datasources()]
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.flex(
                    "Add Data Source",
                    rx.icon(tag="plus", width=24, height=24),
                    spacing="3"
                ),
                size="4",
                radius="full",
                on_click=DataSourceState.toggle_dialog,
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
                    required=True
                ),
                rx.text(
                    "Type *",
                    as_="div",
                    size="2",
                    mb="1",
                    weight="bold",
                ),
                rx.select(
                    datasources,
                    placeholder="Select the data source type",
                    on_change=DataSourceState.set_datasource_type,
                ),
                rx.cond(
                    DataSourceState.datasource_type,
                    rx.vstack(
                        rx.foreach(
                            DataSourceState.datasource_attributes,
                            lambda field:
                            rx.vstack(
                                rx.text(
                                    field,
                                    as_="div",
                                    size="2",
                                    mb="1",
                                    weight="bold",
                                ),
                                rx.input(placeholder=f"Enter the {field} for the data source",
                                         on_blur=lambda x: DataSourceState.set_datasource_attributes(field, x),
                                         width="100%"),
                                width="100%",
                            )
                        ),
                        width="100%",
                    )
                ),
                direction="column",
                spacing="4",
            ),
            rx.cond(
                DataSourceState.missing_attributes,
                rx.chakra.alert(
                    rx.chakra.alert_icon(),
                    rx.chakra.alert_title(
                        "Please fill in all the required fields",
                    ),
                    status="warning",
                    mb="3",
                    mt="3",
                ),
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancel",
                        variant="soft",
                        color_scheme="gray",
                        on_click=DataSourceState.toggle_dialog,
                    )
                ),
                rx.dialog.close(
                    rx.button(
                        "Connect",
                        on_click=DataSourceState.connect_and_add_datasource,
                        variant="solid",
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
        open=DataSourceState.is_open,
    )


def update_datasource(datasource: DataSource):
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("square_pen", width=24, height=24),
                on_click=lambda: DataSourceState.set_datasource(datasource),
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
                rx.text(
                    "Connection URL",
                    as_="div",
                    size="2",
                    mb="1",
                    weight="bold",
                ),
                rx.input(
                    placeholder=datasource.connection_url,
                    default_value=datasource.connection_url,
                    on_blur=DataSourceState.set_connection_url,
                ),
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
                        on_click=DataSourceState.update_datasource,
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


def content_grid():
    return rx.fragment(
        rx.vstack(
            rx.box(
                add_datasource(),
            ),
            rx.divider(),
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
                padding_top="2em",
                padding_bottom="1em",
            ),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Name"),
                        rx.table.column_header_cell("Connection URL"),
                        rx.table.column_header_cell("Edit"),
                        rx.table.column_header_cell("Delete"),
                    ),
                ),
                rx.table.body(rx.foreach(DataSourceState.datasources, show_datasource)),
                # variant="surface",
                size="3",
                width="100%",
                justify="stretch",
            ),
        ),
    )


@template(route="/datasource", title="Data Source", on_load=DataSourceState.on_load())
def datasource() -> rx.Component:
    """The home page.

    Returns:
        The UI for the home page.
    """
    return rx.vstack(
        rx.heading("Data Source", size="8"),
        rx.text("Connect to your data source"),
        rx.box(
            content_grid(),
            margin_top="20px",
            width="100%",
        ),
        # make the page full width
        width="100%",
    )
