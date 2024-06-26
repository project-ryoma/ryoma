"""The RAG (Retrieval Augmented Generation) page."""

import reflex as rx

from aita_lab.templates import ThemeState, template


@template(route="/rag", title="RAG")
def rag() -> rx.Component:
    """The RAG page.

    Returns:
        The UI for the RAG page.
    """
    return rx.vstack(
        rx.heading("RAG", size="8"),
        rx.text("RAG page coming soon!"),
    )
