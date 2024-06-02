"""The home page of the app."""

import reflex as rx

from aitalab import styles
from aitalab.templates import template


@template(route="/document", title="Document")
def document() -> rx.Component:
    """The document page.

    Returns:
        The UI for the document page.
    """
    with open("README.md", encoding="utf-8") as readme:
        content = readme.read()
    return rx.markdown(content, component_map=styles.markdown_style)
