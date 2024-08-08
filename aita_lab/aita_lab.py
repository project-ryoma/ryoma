"""Welcome to Reflex!."""

import os

import reflex as rx
from fps_auth.config import _AuthConfig
from jupyverse_api.frontend import FrontendConfig
from jupyverse_api.kernels import KernelsConfig

from aita_lab.apis.jupyter import mount_jupyter_api

# Import all the pages.
from aita_lab.pages import *


class State(rx.State):
    """Define empty state to allow access to rx.State.router."""


# Create the app.
app = rx.App()


def enable_jupyter():
    """Enable Jupyter."""
    frontend_config = FrontendConfig()
    auth_config = _AuthConfig(
        **{
            "mode": "token",
            "directory": None,
            "clear_users": False,
            "test": False,
            "global_email": "admin@aita.com",
            "cookie_secure": False,
        }
    )
    kernel_config = KernelsConfig()

    mount_jupyter_api(app.api, auth_config, frontend_config, kernel_config)


ENABLE_JUPYTER = os.environ.get("ENABLE_JUPYTER", "false").lower() == "true"
if ENABLE_JUPYTER:
    enable_jupyter()
