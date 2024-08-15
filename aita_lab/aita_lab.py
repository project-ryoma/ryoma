"""Welcome to Aita!."""

import reflex as rx

from aita_lab.apps.app_factory import create_marimo_app

# Import all the pages.
from aita_lab.pages import *


class State(rx.State):
    """Define empty state to allow access to rx.State.router."""


# Create the app.
app = rx.App()
marimo_app = create_marimo_app(
    quiet=True,
    include_code=True,
    token="",
).build()

app.api.mount("/_marimo", marimo_app)
