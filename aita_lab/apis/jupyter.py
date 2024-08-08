from fastapi import FastAPI
from fps_auth.config import _AuthConfig
from fps_contents.routes import _Contents
from fps_kernels.routes import _Kernels
from fps_yjs.routes import _Yjs
from jupyverse_api import App
from jupyverse_api.frontend import FrontendConfig
from jupyverse_api.kernels import KernelsConfig

from aita_lab.auth_adapter.jupy_auth import auth_factory


def mount_jupyter_api(
    api: FastAPI,
    auth_config: _AuthConfig,
    frontend_config: FrontendConfig,
    kernel_config: KernelsConfig,
):
    """Enable the jupyverse app."""

    # mount jupyverse app.
    jupyverse_app = App(api)

    auth = auth_factory(jupyverse_app, auth_config, frontend_config)

    contents = _Contents(jupyverse_app, auth)

    kernels = _Kernels(jupyverse_app, kernel_config, auth, frontend_config, None)
