import os

import reflex as rx

from ryoma_lab import styles
from ryoma_lab.services.file_manager import FileNode
from ryoma_lab.states.notebook import NotebookState


def file_item(file: FileNode) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.cond(
                file.is_dir,
                rx.icon("folder", size=16),
                rx.icon("file", size=16),
            ),
            rx.text(file.name, cursor="pointer", size="1"),
        ),
        _hover={"background_color": rx.color("gray", 2)},
        on_click=lambda: NotebookState.open_file(file.name),
    )


def file_directory_sidebar() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.heading("File Directory", size="2"),
            rx.spacer(),
            rx.icon(
                "chevron_left",
                cursor="pointer",
                on_click=NotebookState.toggle_sidebar,
            ),
            width="100%",
        ),
        rx.vstack(
            rx.foreach(NotebookState.file_list, lambda file: file_item(file)),
            margin_top="0.5em",
            align_items="start",
            width="100%",
        ),
        width=NotebookState.sidebar_width,
        height="100%",
        border=styles.border,
        border_radius=styles.border_radius,
        padding="1em",
        transition="width 0.3s",
        overflow="scroll",
    )
