import os

import reflex as rx

from ryoma_lab import styles
from ryoma_lab.services.file_manager import FileNode
from ryoma_lab.states.notebook import NotebookState


def dropdown_item(children: rx.Component) -> rx.Component:
    return rx.context_menu.root(
        rx.context_menu.trigger(
            children,
        ),
        rx.context_menu.content(
            rx.context_menu.item("Edit", shortcut="⌘ E"),
            rx.context_menu.item("Duplicate", shortcut="⌘ D"),
            rx.context_menu.separator(),
            rx.context_menu.item("Archive", shortcut="⌘ N"),
            rx.context_menu.sub(
                rx.context_menu.sub_trigger("More"),
                rx.context_menu.sub_content(
                    rx.context_menu.item("Move to project…"),
                    rx.context_menu.item("Move to folder…"),
                    rx.context_menu.separator(),
                    rx.context_menu.item("Advanced options…"),
                ),
            ),
            rx.context_menu.separator(),
            rx.context_menu.item("Share"),
            rx.context_menu.item("Add to favorites"),
            rx.context_menu.separator(),
            rx.context_menu.item(
                "Delete", shortcut="⌘ ⌫", color="red"
            ),
        ),
    )


def file_item(file: FileNode) -> rx.Component:
    return dropdown_item(
        rx.box(
            rx.hstack(
                rx.cond(
                    file.is_dir,
                    rx.icon("folder", size=16),
                    rx.icon("file", size=16),
                ),
                rx.text(file.name,  size="1"),
                width="100%"
            ),
            on_double_click=lambda: NotebookState.open_file_or_directory(file),
            _hover={"background_color": rx.color("gray", 3)},
            cursor="pointer",
            width="100%"
        )
    )


def file_directory_sidebar() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.heading(
                "File Directory",
                size="2",
                hidden=~NotebookState.is_sidebar_open,
            ),
            rx.spacer(hidden=~NotebookState.is_sidebar_open),
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
