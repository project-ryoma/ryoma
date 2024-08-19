"""The Vector Store page."""

import reflex as rx

from ryoma_lab import styles
from ryoma_lab.components.upload import upload_render
from ryoma_lab.states.base import BaseState
from ryoma_lab.states.datasource import DataSourceState
from ryoma_lab.states.vector_store import VectorStoreState
from ryoma_lab.templates import ThemeState, template


def render_feature_source_configs():
    return rx.flex(
        rx.chakra.heading("Feature Source Configs", size="sm"),
        rx.foreach(
            ["database", "table", "column", "query"],
            lambda attribute: rx.flex(
                rx.chakra.text(attribute, size="md"),
                rx.input(
                    placeholder=f"Enter the {attribute}",
                    on_blur=lambda x: VectorStoreState.set_feature_source_config(attribute, x),
                ),
                direction="column",
                spacing="2",
            ),
        ),
        direction="column",
        spacing="4",
        border=styles.border,
        border_radius=styles.border_radius,
        width="100%",
        padding="1em",
        background_color=styles.accent_color,
    )


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
                rx.chakra.heading("Feature View Name *", size="sm"),
                rx.input(
                    placeholder="Enter the name of the feature view (table)",
                    on_blur=VectorStoreState.set_feature_view_name,
                    required=True,
                ),
                rx.chakra.heading("Feature Name *", size="sm"),
                rx.input(
                    placeholder="Enter the feature name",
                    on_blur=VectorStoreState.set_feature_name,
                    required=True,
                ),
                rx.chakra.heading("Entities", size="sm"),
                rx.input(
                    placeholder="Enter the entities",
                    on_blur=VectorStoreState.set_feature_entities,
                    required=False,
                ),
                rx.chakra.heading("Feature Data Source", size="sm"),
                rx.select.root(
                    rx.select.trigger("Select the data source for the feature"),
                    rx.select.content(
                        rx.select.group(
                            rx.select.item("Upload files", value="files"),
                            rx.cond(
                                VectorStoreState.project & VectorStoreState.project.offline_store,
                                rx.select.item(
                                    VectorStoreState.project.offline_store,
                                    value=VectorStoreState.project.offline_store,
                                ),
                            ),
                            # rx.foreach(
                            #     DataSourceState.datasources,
                            #     lambda ds: rx.select.item(ds.name, value=ds.name),
                            # ),
                        ),
                    ),
                    value=VectorStoreState.feature_datasource,
                    on_change=VectorStoreState.set_feature_datasource,
                ),
                rx.cond(
                    VectorStoreState.feature_datasource,
                    rx.cond(
                        VectorStoreState.feature_datasource == "files",
                        upload_render(VectorStoreState.files, VectorStoreState.handle_upload),
                        render_feature_source_configs(),
                    ),
                ),
                rx.flex(
                    rx.dialog.close(
                        rx.chakra.button(
                            "Create Feature",
                            on_click=VectorStoreState.create_vector_feature,
                        ),
                    ),
                    justify="end",
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
                on_click=VectorStoreState.toggle_store_dialog,
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
                rx.chakra.heading("Vector Store *", size="sm"),
                rx.select.root(
                    rx.select.trigger(
                        placeholder="Select the data source as the vector store",
                    ),
                    rx.select.content(
                        rx.select.group(
                            rx.foreach(
                                DataSourceState.datasources,
                                lambda ds: rx.select.item(ds.name, value=ds.name),
                            ),
                        ),
                    ),
                    value=VectorStoreState.online_store,
                    on_change=lambda ds: VectorStoreState.set_online_store(ds),
                ),
                rx.chakra.heading("Vector Store Configs", size="sm"),
                rx.input(
                    placeholder="Enter the vector store configs",
                    on_blur=VectorStoreState.set_online_store_configs,
                ),
                rx.chakra.heading("Offline Store", size="sm"),
                rx.select.root(
                    rx.select.trigger(
                        placeholder="Select the data source as the offline store",
                    ),
                    rx.select.content(
                        rx.select.group(
                            rx.foreach(
                                DataSourceState.datasources,
                                lambda ds: rx.select.item(ds.name, value=ds.name),
                            ),
                        ),
                    ),
                    value=VectorStoreState.offline_store,
                    on_change=lambda ds: VectorStoreState.set_offline_store(ds),
                ),
                rx.chakra.heading("Offline Store Configs", size="sm"),
                rx.input(
                    placeholder="Enter the offline store configs",
                    on_blur=VectorStoreState.set_offline_store_configs,
                ),
                rx.flex(
                    rx.dialog.close(
                        rx.button(
                            "Create Store",
                            size="2",
                            on_click=VectorStoreState.create_store,
                        ),
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
                direction="column",
                spacing="4",
            ),
            open=VectorStoreState.store_dialog_open,
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
                        rx.chakra.th("Feature View"),
                        rx.chakra.th("Entities"),
                        rx.chakra.th("Feature"),
                        rx.chakra.th("Source"),
                        rx.chakra.th("Load"),
                    )
                ),
                rx.chakra.tbody(
                    rx.foreach(
                        VectorStoreState.vector_feature_views,
                        lambda feature_view: rx.chakra.tr(
                            rx.chakra.td(feature_view.name),
                            rx.chakra.td(feature_view.entities),
                            rx.chakra.td(feature_view.feature),
                            rx.chakra.td(feature_view.source),
                            rx.chakra.td(
                                rx.chakra.button(
                                    "Load",
                                    on_click=lambda: VectorStoreState.load_feature_views(
                                        feature_view
                                    ),
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
                    VectorStoreState.projects,
                    lambda project: rx.tabs.trigger(
                        project.project_name,
                        value=project.project_name,
                        cursor="pointer",
                    ),
                ),
            ),
            rx.tabs.content(
                show_features(),
                value=VectorStoreState.project.project_name,
                width="100%",
            ),
            value=VectorStoreState.project.project_name,
            on_change=VectorStoreState.set_project,
            orientation="horizontal",
            height="100vh",
            width="100%",
        ),
        width="100%",
        border=styles.border,
        border_radius=styles.border_radius,
    )


@template(
    route="/vector_store",
    title="Vector Store",
    on_load=[BaseState.on_load, VectorStoreState.on_load, DataSourceState.on_load],
)
def vector_store() -> rx.Component:
    """The Vector Store page.

    Returns:
        The UI for the Vector Store page.
    """
    return rx.vstack(
        rx.chakra.heading("Vector Store [Beta]"),
        rx.chakra.text("Create a vector store to store your embedding features"),
        setup_store(),
        show_store(),
        width="100%",
    )
