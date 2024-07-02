"""Welcome to Reflex!."""

# Import all the pages.
import reflex as rx

from aita_lab.pages import *


class State(rx.State):
    """Define empty state to allow access to rx.State.router."""


# Create the app.
app = rx.App(style={"overflow": "hidden"})
