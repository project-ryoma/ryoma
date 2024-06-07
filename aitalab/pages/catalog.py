"""The data catalog page """

import reflex as rx

from aitalab.templates import template


def catalog_search():
    return rx.flex(
        rx.input(
            placeholder="Search for a table or column",
            width="100%",
        ),
        rx.button("Search"),
        spacing="3",
        justify="center",
        align="center",
        width="100%",
    )


@template(route="/catalog", title="Data Catalog")
def catalog():
    return rx.vstack(
        rx.heading("Data Catalog", size="8"),
        rx.text("View your data catalog"),
        catalog_search(),
        width="100%",
    )
