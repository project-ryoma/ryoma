"""The Vector Store page."""

import reflex as rx

from aita_lab.states.vector_store import VectorStoreState
from aita_lab.templates import ThemeState, template


def add_feature():
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.flex("Add Feature", rx.icon(tag="plus", width=24, height=24), spacing="3"),
                size="4",
                radius="full",
                on_click=VectorStoreState.open_feature_dialog,
            ),
        ),
        rx.dialog.content(
            rx.dialog.title(
                "Feature Information",
                size="1",
                font_family="Inter",
                padding_top="1em",
            ),
            rx.dialog.description(
                "Select the feature and enter the feature information for your data source",
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
                    placeholder="Enter the name of the feature",
                    on_blur=VectorStoreState.set_name,
                    required=True,
                ),
            ),
        ),
    )


def setup_store():
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.flex("Setup Store", rx.icon(tag="plus", width=24, height=24), spacing="3"),
                size="4",
                radius="full",
                on_click=VectorStoreState.open_store_dialog,
            ),
        ),
        rx.dialog.content(
            rx.dialog.title(
                "Create Store",
                size="1",
                font_family="Inter",
                padding_top="1em",
            ),
            rx.dialog.description(
                "Create a Vector Store to store your embedding features.",
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
                    placeholder="Enter the name of the project",
                    on_blur=VectorStoreState.set_project_name,
                    required=True,
                ),
                rx.text(
                    "Online Store *",
                    as_="div",
                    size="2",
                    mb="1",
                    weight="bold",
                ),
                rx.select(
                    ["Postgresql", "Sqlite", "Elasticsearch"],
                    placeholder="Select the store type",
                    on_change=VectorStoreState.set_online_store_type,
                ),
                rx.input(
                    placeholder="Enter the vector online store configs",
                    on_blur=VectorStoreState.set_online_store_configs,
                ),
                rx.chakra.button(
                    "Create Store",
                    on_click=VectorStoreState.create_store,
                ),
                direction="column",
                spacing="4",
            ),
        ),
    )


@template(route="/vector_store", title="Vector Store")
def vector_store() -> rx.Component:
    """The Vector Store page.

    Returns:
        The UI for the Vector Store page.
    """
    return rx.vstack(
        rx.chakra.heading("Vector Store"),
        rx.chakra.text("Create a vector store to store your embedding features"),
        setup_store(),
    )
