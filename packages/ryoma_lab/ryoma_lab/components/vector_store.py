import reflex as rx
import reflex_chakra as rc
from ryoma_lab import styles
from ryoma_lab.components.model_selector import embedding_model_selector
from ryoma_lab.components.upload import upload_render
from ryoma_lab.states.vector_store import VectorStoreState


def render_project_description():
    return rx.flex(
        rc.heading("Project Description", size="sm"),
        rx.input(
            placeholder="Enter a description for your project (optional)",
            value=VectorStoreState.project_description,
            on_blur=VectorStoreState.set_project_description,
        ),
        direction="column",
        spacing="2",
        border=styles.border,
        border_radius=styles.border_radius,
        width="100%",
        padding="1em",
        background_color=styles.accent_color,
    )


def upload_documents():
    return rx.dialog.root(
        rx.dialog.trigger(
            rc.button(
                rx.flex("Upload Documents +", spacing="3"),
                size="sm",
                width="100%",
                on_click=VectorStoreState.toggle_upload_dialog,
            ),
        ),
        rx.dialog.content(
            rx.dialog.title(
                "Upload Documents",
                size="1",
                font_family="Inter",
                padding_top="1em",
            ),
            rx.dialog.description(
                "Upload documents to index in your project.",
                size="2",
                mb="4",
                padding_bottom="1em",
            ),
            rx.flex(
                upload_render(
                    VectorStoreState.uploaded_files, 
                    VectorStoreState.handle_upload
                ),
                rx.flex(
                    rx.dialog.close(
                        rc.button(
                            "Close",
                            variant="soft",
                            color_scheme="gray",
                        ),
                    ),
                    justify="end",
                ),
                direction="column",
                spacing="4",
            ),
            open=VectorStoreState.upload_dialog_open,
        ),
    )


def setup_project():
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.flex(
                    "New Project", rx.icon(tag="plus", width=24, height=24), spacing="3"
                ),
                size="4",
                radius="full",
                on_click=VectorStoreState.toggle_create_project_dialog,
            ),
        ),
        rx.dialog.content(
            rx.dialog.title(
                "Create a Document Project",
                size="1",
                font_family="Inter",
                padding_top="1em",
            ),
            rx.dialog.description(
                "Create a project to store and search your documents.",
                size="2",
                mb="4",
                padding_bottom="1em",
            ),
            rx.flex(
                rc.heading("Project Name *", size="sm"),
                rx.input(
                    placeholder="Enter the name of your project",
                    value=VectorStoreState.project_name,
                    on_blur=VectorStoreState.set_project_name,
                    required=True,
                ),
                render_project_description(),
                rx.flex(
                    rx.dialog.close(
                        rx.button(
                            "Create Project",
                            size="2",
                            on_click=VectorStoreState.create_project,
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
            open=VectorStoreState.create_project_dialog_open,
        ),
    )


def index_documents_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rc.button(
                "Index Documents",
                color_scheme="blue",
                size="sm",
            ),
        ),
        rx.dialog.content(
            rx.dialog.title(
                "Index Documents",
                size="1",
                font_family="Inter",
                padding_top="1em",
            ),
            rx.dialog.description(
                "Process and index uploaded documents into the vector store for semantic search.",
                size="2",
                mb="4",
                padding_bottom="1em",
            ),
            rx.flex(
                embedding_model_selector(),
                rx.flex(
                    rx.dialog.close(
                        rc.button(
                            "Start Indexing",
                            on_click=VectorStoreState.index_uploaded_documents,
                        ),
                    ),
                    rx.dialog.close(
                        rc.button(
                            "Cancel",
                            variant="outline",
                            color_scheme="gray",
                        ),
                    ),
                    padding_top="1em",
                    spacing="3",
                    justify="end",
                ),
                direction="column",
                spacing="4",
            ),
        ),
    )


def project_info_render(project) -> rx.Component:
    return rx.flex(
        rc.text(f"Documents: {project.document_count}", size="sm"),
        rc.text(f"Description: {project.description or 'No description'}", size="sm"),
        rc.text(f"Created: {project.created_at.strftime('%Y-%m-%d') if project.created_at else 'Unknown'}", size="sm"),
        rx.button(
            "Delete",
            color_scheme="red",
            variant="outline",
            size="1",
            on_click=lambda: VectorStoreState.delete_project(project.project_name),
        ),
        direction="column",
        spacing="2",
        padding="1em",
        border=styles.border,
        border_radius=styles.border_radius,
        background_color=styles.accent_color,
    )


def show_project_details():
    return rc.box(
        rx.cond(
            VectorStoreState.current_project,
            rx.flex(
                rc.heading(f"Project: {VectorStoreState.current_project.project_name}"),
                rc.text("Manage documents in your project"),
                project_info_render(VectorStoreState.current_project),
                upload_documents(),
                rx.cond(
                    VectorStoreState.uploaded_files,
                    rx.flex(
                        rc.heading("Uploaded Files", size="sm"),
                        rx.foreach(
                            VectorStoreState.uploaded_files,
                            lambda file: rc.text(file, size="sm")
                        ),
                        index_documents_dialog(),
                        direction="column",
                        spacing="2",
                    )
                ),
                direction="column",
                spacing="4",
            ),
            rc.text("Select a project to view details")
        ),
        width="100%",
        padding="1em",
    )


def show_projects():
    return rc.box(
        rx.tabs.root(
            rx.tabs.list(
                rx.foreach(
                    VectorStoreState.document_projects,
                    lambda project: rx.tabs.trigger(
                        project.project_name,
                        value=project.project_name,
                        cursor="pointer",
                    ),
                ),
            ),
            rx.tabs.content(
                show_project_details(),
                value=VectorStoreState.current_project.project_name if VectorStoreState.current_project else "",
                width="100%",
            ),
            value=VectorStoreState.current_project.project_name if VectorStoreState.current_project else "",
            on_change=VectorStoreState.set_current_project,
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
        setup_project(),
        rx.cond(
            VectorStoreState.document_projects,
            show_projects(),
        ),
        width="100%",
        height="100%",
        padding_x="1em",
        on_mount=VectorStoreState.on_load,
    )
