import reflex as rx
from ryoma_lab import styles
from ryoma_lab.components.model_selector import embedding_model_selector
from ryoma_lab.components.upload import upload_render
from ryoma_lab.states.datasource import DataSourceState
from ryoma_lab.states.vector_store import VectorStoreState


def render_feature_source_configs():
    return rx.flex(
        rx.chakra.heading("Feature Source Configs", size="sm"),
        rx.foreach(
            ["table", "query", "timestamp_field"],
            lambda attribute: rx.flex(
                rx.chakra.text(attribute, size="md"),
                rx.input(
                    placeholder=f"Enter the {attribute}",
                    on_blur=lambda x: VectorStoreState.set_feature_source_config(
                        attribute, x
                    ),
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
                on_click=VectorStoreState.toggle_create_feature_dialog,
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
                    placeholder="Enter the name for your embedding feature",
                    on_blur=VectorStoreState.set_feature_name,
                    required=True,
                ),
                rx.chakra.heading("Entity Name", size="sm"),
                rx.input(
                    placeholder="Enter the entity name",
                    on_blur=VectorStoreState.set_feature_entity_name,
                    required=False,
                ),
                rx.chakra.heading("Feature Data Source", size="sm"),
                rx.select.root(
                    rx.select.trigger("Select the data source for the feature"),
                    rx.select.content(
                        rx.select.group(
                            rx.select.item("Upload files", value="files"),
                            rx.foreach(
                                DataSourceState.datasources,
                                lambda ds: rx.select.item(ds.name, value=ds.name),
                            ),
                        ),
                    ),
                    value=VectorStoreState.feature_datasource,
                    on_change=VectorStoreState.set_feature_datasource,
                ),
                rx.cond(
                    VectorStoreState.feature_datasource,
                    rx.cond(
                        VectorStoreState.feature_datasource == "files",
                        upload_render(
                            VectorStoreState.files, VectorStoreState.handle_upload
                        ),
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
                rx.flex(
                    "New Project", rx.icon(tag="plus", width=24, height=24), spacing="3"
                ),
                size="4",
                radius="full",
                on_click=VectorStoreState.toggle_create_store_dialog,
            ),
        ),
        rx.dialog.content(
            rx.dialog.title(
                "Create a project",
                size="1",
                font_family="Inter",
                padding_top="1em",
            ),
            rx.dialog.description(
                "Create a project to store your RAG data.",
                size="2",
                mb="4",
                padding_bottom="1em",
            ),
            rx.flex(
                rx.chakra.heading("Project Name *", size="sm"),
                rx.input(
                    placeholder="Enter the name of your project",
                    on_blur=VectorStoreState.set_project_name,
                    required=True,
                ),
                rx.chakra.heading("Database *", size="sm"),
                rx.select.root(
                    rx.select.trigger(
                        placeholder="Select the database as your online store for the embeddings",
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
                rx.chakra.heading("Embedding dimension", size="sm"),
                rx.input(
                    placeholder="Enter the dimension of the embeddings",
                    on_blur=VectorStoreState.set_embedding_dimension,
                ),
                rx.flex(
                    rx.dialog.close(
                        rx.button(
                            "Create a project",
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
            open=VectorStoreState.create_store_dialog_open,
        ),
    )


def index_feature_render(feature_view) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.chakra.button(
                "Index",
                on_click=VectorStoreState.toggle_materialize_feature_dialog,
            ),
        ),
        rx.dialog.content(
            rx.dialog.title(
                "Embed and Index Feature",
                size="1",
                font_family="Inter",
                padding_top="1em",
            ),
            rx.dialog.description(
                "Embed and index the feature data into the vector store.",
                size="2",
                mb="4",
                padding_bottom="1em",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Confirm",
                        on_click=lambda: VectorStoreState.index_feature(feature_view),
                    ),
                ),
                rx.dialog.close(
                    rx.button(
                        "Cancel",
                        variant="soft",
                        color_scheme="gray",
                    ),
                ),
                padding_top="1em",
                spacing="3",
                justify="end",
            ),
            open=VectorStoreState.materialize_feature_dialog_open,
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
                        rx.chakra.th("Entity Name"),
                        rx.chakra.th("Feature"),
                        rx.chakra.th("Source"),
                        rx.chakra.th("Index"),
                    )
                ),
                rx.chakra.tbody(
                    rx.foreach(
                        VectorStoreState.current_feature_views,
                        lambda feature_view: rx.chakra.tr(
                            rx.chakra.td(feature_view.name),
                            rx.chakra.td(feature_view.entities),
                            rx.chakra.td(feature_view.feature),
                            rx.chakra.td(feature_view.source),
                            rx.chakra.td(index_feature_render(feature_view)),
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
                    VectorStoreState.vector_stores,
                    lambda project: rx.tabs.trigger(
                        project.project_name,
                        value=project.project_name,
                        cursor="pointer",
                    ),
                ),
            ),
            rx.tabs.content(
                show_features(),
                value=VectorStoreState.current_store.project_name,
                width="100%",
            ),
            value=VectorStoreState.current_store.project_name,
            on_change=VectorStoreState.set_project,
            orientation="horizontal",
            height="100vh",
            width="100%",
        ),
        width="100%",
        border=styles.border,
        border_radius=styles.border_radius,
    )


def vector_store_component() -> rx.Component:
    return rx.vstack(
        setup_store(),
        rx.cond(
            VectorStoreState.vector_stores,
            show_store(),
        ),
        width="100%",
        height="100%",
        padding_x="1em",
    )
