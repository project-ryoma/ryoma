"""The Vector Store page."""

import reflex as rx
from ryoma_lab import styles
from ryoma_lab.components.model_selector import embedding_model_selector
from ryoma_lab.components.upload import upload_render
from ryoma_lab.states.base import BaseState
from ryoma_lab.states.datasource import DataSourceState
from ryoma_lab.states.vector_store import VectorStoreState
from ryoma_lab.templates import ThemeState, template


class VectorStoreUploadState(rx.State):
    uploading: bool = False
    progress: int = 0
    total_bytes: int = 0

    async def handle_upload(self,
                            files: list[rx.UploadFile]):
        for file in files:
            file_content = await file.read()
            self.total_bytes += len(file_content)
            await VectorStoreState.handle_upload([file])

    def handle_upload_progress(self,
                               progress: dict):
        self.uploading = True
        self.progress = round(progress["progress"] * 100)
        if self.progress >= 100:
            self.uploading = False

    def cancel_upload(self):
        self.uploading = False
        return rx.cancel_upload("vector_store_upload")


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
                                VectorStoreState.project
                                & VectorStoreState.project.offline_store,
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
                    "Setup Store", rx.icon(tag="plus", width=24, height=24), spacing="3"
                ),
                size="4",
                radius="full",
                on_click=VectorStoreState.toggle_create_store_dialog,
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
                rx.chakra.heading("Online Store *", size="sm"),
                rx.select.root(
                    rx.select.trigger(
                        placeholder="Select the data source as the online store for the embeddings",
                    ),
                    rx.select.content(
                        rx.select.group(
                            rx.foreach(
                                DataSourceState.datasources,
                                lambda ds: rx.select.item(ds.name, value=ds.name),
                            ),
                        ),
                    ),
                    value=VectorStoreState.vector_store,
                    on_change=lambda ds: VectorStoreState.set_vector_store(ds),
                ),
                rx.chakra.heading("Online Store Configs", size="sm"),
                rx.input(
                    placeholder="Enter the online vector store configs",
                    on_blur=VectorStoreState.set_vector_store_configs,
                ),
                rx.flex(
                    rx.dialog.close(
                        rx.button(
                            "Create Store",
                            size="2",
                            on_click=VectorStoreState.create_vector_store,
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


def materialize_feature_render(feature_view) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.chakra.button(
                "Materialize",
                on_click=VectorStoreState.toggle_materialize_feature_dialog,
            ),
        ),
        rx.dialog.content(
            rx.dialog.title(
                "Materialize Feature",
                size="1",
                font_family="Inter",
                padding_top="1em",
            ),
            rx.dialog.description(
                "Materialize the feature data into the vector store.",
                size="2",
                mb="4",
                padding_bottom="1em",
            ),
            rx.vstack(
                rx.chakra.heading("Embeddings", size="sm"),
                embedding_model_selector(
                    VectorStoreState.materialize_embedding_model,
                    VectorStoreState.set_materialize_embedding_model,
                    trigger_width="100%",
                ),
                rx.chakra.heading("Model Configs", size="sm"),
                rx.chakra.input(
                    placeholder="Enter the model configs",
                    on_blur=VectorStoreState.set_materialize_embedding_model_configs,
                ),
                width="100%",
                border=styles.border,
                border_radius=styles.border_radius,
                padding="1em",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Confirm",
                        on_click=lambda: VectorStoreState.materialize_feature(
                            feature_view
                        ),
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
                        rx.chakra.th("Entities"),
                        rx.chakra.th("Feature"),
                        rx.chakra.th("Source"),
                        rx.chakra.th("Materialize"),
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
                            rx.chakra.td(materialize_feature_render(feature_view)),
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


def create_store_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(rx.button("Create Vector Store")),
        rx.dialog.content(
            rx.dialog.title("Create New Vector Store"),
            rx.vstack(
                rx.input(
                    placeholder="Project Name",
                    on_change=VectorStoreState.set_project_name,
                ),
                rx.select(
                    ["FAISS", "Chroma", "Pinecone"],
                    placeholder="Select Vector Store Type",
                    on_change=VectorStoreState.set_vector_store_type,
                ),
                embedding_model_selector(
                    VectorStoreState.embedding_model,
                    VectorStoreState.set_embedding_model,
                    trigger_width="100%",
                ),
                rx.button(
                    "Create",
                    on_click=VectorStoreState.create_vector_store,
                ),
                spacing="4",
            ),
        ),
        open=VectorStoreState.create_store_dialog_open,
    )


def add_documents_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(rx.button("Add Documents")),
        rx.dialog.content(
            rx.dialog.title("Add Documents to Vector Store"),
            rx.vstack(
                rx.upload(
                    rx.vstack(
                        rx.button("Select Files"),
                        rx.text("Drag and drop files here"),
                    ),
                    id="vector_store_upload",
                    multiple=True,
                    accept={".pdf": [], ".txt": [], ".docx": []},
                    max_files=10,
                ),
                rx.vstack(
                    rx.foreach(
                        rx.selected_files("vector_store_upload"), rx.text
                    )
                ),
                rx.progress(value=VectorStoreUploadState.progress, max=100),
                rx.cond(
                    ~VectorStoreUploadState.uploading,
                    rx.button(
                        "Upload",
                        on_click=VectorStoreUploadState.handle_upload(
                            rx.upload_files(
                                upload_id="vector_store_upload",
                                on_upload_progress=VectorStoreUploadState.handle_upload_progress,
                            ),
                        ),
                    ),
                    rx.button(
                        "Cancel",
                        on_click=VectorStoreUploadState.cancel_upload,
                    ),
                ),
                rx.text(
                    "Total bytes uploaded: ",
                    VectorStoreUploadState.total_bytes,
                ),
                rx.button(
                    "Add Documents",
                    on_click=VectorStoreState.add_documents,
                ),
                spacing="4",
            ),
        ),
        open=VectorStoreState.add_documents_dialog_open,
    )


def vector_store_component() -> rx.Component:
    """The Vector Store page.

    Returns:
        The UI for the Vector Store page.
    """
    return rx.vstack(
        setup_store(),
        show_features(),
        add_documents_dialog(),
        width="100%",
        height="100%",
        padding="2em",
    )
