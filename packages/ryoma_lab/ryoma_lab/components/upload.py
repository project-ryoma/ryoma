from typing import Any

import reflex as rx
from ryoma_lab import styles


def upload_render(files: list[str], handle_upload: Any):
    """The main view."""
    return rx.vstack(
        rx.upload(
            rx.vstack(
                rx.button(
                    "Select File",
                ),
                rx.text("Drag and drop files here or click to select files"),
                align="center",
            ),
            id="upload2",
            multiple=True,
            accept={
                "application/pdf": [".pdf"],
                "image/png": [".png"],
                "image/jpeg": [".jpg", ".jpeg"],
                "image/gif": [".gif"],
                "image/webp": [".webp"],
                "text/html": [".html", ".htm"],
            },
            max_files=5,
            disabled=False,
            on_drop=handle_upload(rx.upload_files(upload_id="upload2")),
            border=styles.border,
            padding="5em",
        ),
        rx.grid(
            rx.foreach(
                files,
                lambda file: rx.vstack(
                    rx.text(file),
                ),
            ),
            columns="2",
            spacing="1",
        ),
        padding="5em",
    )
