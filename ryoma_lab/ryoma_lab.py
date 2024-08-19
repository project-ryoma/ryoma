"""Welcome to Ryoma!."""

import reflex as rx

# Import all the pages.
from ryoma_lab.pages import *


class State(rx.State):
    """Define empty state to allow access to rx.State.router."""


# Create the app.
app = rx.App()
