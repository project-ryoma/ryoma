"""The Vector Store page."""

import reflex as rx

from aita_lab import styles
from aita_lab.states.vector_store import VectorStoreState
from aita_lab.templates import ThemeState, template


def add_feature():
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.chakra.button(
                rx.flex("Add Feature +", spacing="3"),
                size="sm",
                width="100%",
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
                "Create a feature to store your embedding data.",
                size="2",
                mb="4",
                padding_bottom="1em",
            ),
            rx.flex(
                rx.chakra.heading("Feature Name *", size="sm"),
                rx.input(
                    placeholder="Enter the name of the feature",
                    on_blur=VectorStoreState.set_feature_name,
                    required=True,
                ),
                rx.chakra.heading("Schema *", size="sm"),
                rx.input(
                    placeholder="Enter the schema",
                    on_blur=VectorStoreState.set_feature_schema,
                    required=True,
                ),
                rx.chakra.heading("Entities", size="sm"),
                rx.input(
                    placeholder="Enter the entities",
                    on_blur=VectorStoreState.set_feature_entities,
                    required=False,
                ),
                rx.chakra.heading("Source", size="sm"),
                rx.input(
                    placeholder="Enter the source",
                    on_blur=VectorStoreState.set_feature_source,
                    required=False,
                ),
                rx.chakra.heading("ttl", size="sm"),
                rx.input(
                    placeholder="Enter the ttl",
                    on_blur=VectorStoreState.set_feature_ttl,
                    required=False,
                ),
                rx.chakra.button(
                    "Create Feature",
                    on_click=VectorStoreState.create_vector_feature,
                ),
                direction="column",
                spacing="4",
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
                rx.chakra.heading("Project Name *", size="sm"),
                rx.input(
                    placeholder="Enter the name of the project",
                    on_blur=VectorStoreState.set_project_name,
                    required=True,
                ),
                rx.chakra.heading("Online Store Type *", size="sm"),
                rx.select(
                    ["Postgresql", "Sqlite", "Elasticsearch"],
                    placeholder="Select the store type",
                    on_change=VectorStoreState.set_online_store_type,
                ),
                rx.chakra.heading("Online Store Configs", size="sm"),
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


def show_features():
    return rx.chakra.box(
        rx.chakra.heading("Embedding Features"),
        rx.chakra.text("Create a feature to store your embedding data"),
        rx.chakra.table_container(
            rx.chakra.table(
                rx.chakra.thead(
                    rx.chakra.tr(
                        rx.chakra.th("Name"),
                        rx.chakra.th("Entities"),
                        rx.chakra.th("schema"),
                        rx.chakra.th("Source"),
                        rx.chakra.th("ttl"),
                        rx.chakra.th("Load"),
                    )
                ),
                rx.chakra.tbody(
                    rx.foreach(
                        VectorStoreState.vector_features,
                        lambda feature: rx.chakra.tr(
                            rx.chakra.td(feature.name),
                            rx.chakra.td(feature.entities),
                            rx.chakra.td(feature.schema),
                            rx.chakra.td(feature.source),
                            rx.chakra.td(feature.ttl),
                            rx.chakra.td(
                                rx.chakra.button(
                                    "Load",
                                    on_click=VectorStoreState.load_vector_feature,
                                )
                            ),
                        ),
                    ),
                    width="100%",
                ),
                color_scheme="white",
                variant="striped",
                width="100%",
            ),
            add_feature(),
            width="100%",
        ),
        width="100%",
        padding="1em",
    )


def show_store():
    return rx.chakra.box(
        rx.tabs.root(
            rx.tabs.list(
                rx.foreach(
                    VectorStoreState.project_names,
                    lambda project_name: rx.tabs.trigger(
                        project_name,
                        value=project_name,
                        cursor="pointer",
                    ),
                ),
            ),
            rx.tabs.content(
                show_features(),
                value=VectorStoreState.project_name,
                width="100%",
            ),
            value=VectorStoreState.project_name,
            on_change=VectorStoreState.set_project,
            orientation="horizontal",
            height="100vh",
            width="100%",
        ),
        width="100%",
        border=styles.border,
        border_radius=styles.border_radius,
    )


@template(route="/vector_store", title="Vector Store", on_load=[VectorStoreState.on_load()])
def vector_store() -> rx.Component:
    """The Vector Store page.

    Returns:
        The UI for the Vector Store page.
    """
    return rx.vstack(
        rx.chakra.heading("Vector Store"),
        rx.chakra.text("Create a vector store to store your embedding features"),
        setup_store(),
        show_store(),
        width="100%",
    )
