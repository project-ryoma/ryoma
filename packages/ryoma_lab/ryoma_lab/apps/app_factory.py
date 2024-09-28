from __future__ import annotations

import os
from typing import List, Optional, Tuple

import marimo._server.api.lifespans as lifespans
from marimo._cli.cli import DEVELOPMENT_MODE
from marimo._config.manager import UserConfigManager
from marimo._server.asgi import ASGIAppBuilder
from marimo._server.file_router import AppFileRouter
from marimo._server.main import create_starlette_app
from marimo._server.model import SessionMode
from marimo._server.sessions import NoopLspServer, SessionManager
from marimo._server.tokens import AuthToken
from starlette.applications import Starlette


def create_marimo_app(
    *,
    quiet: bool = False,
    include_code: bool = False,
    token: str | None = None,
) -> ASGIAppBuilder:
    user_config_mgr = UserConfigManager()

    # Default to an empty token
    # If a user is using the create_asgi_app API,
    # they likely want to provide their own authN/authZ
    if not token:
        auth_token = AuthToken("")
    else:
        auth_token = AuthToken(token)

    # We call the entrypoint `root` instead of `filename` incase we want to
    # support directories or code in the future
    class Builder(ASGIAppBuilder):
        def __init__(self) -> None:
            self._mount_configs: list[tuple[str, str]] = []

        def with_app(self, *, path: str, root: str) -> ASGIAppBuilder:
            self._mount_configs.append((path, root))
            return self

        def build(self) -> Starlette:
            name = os.getcwd()

            session_manager = SessionManager(
                file_router=AppFileRouter.infer(name),
                mode=SessionMode.EDIT,
                development_mode=DEVELOPMENT_MODE,
                quiet=quiet,
                include_code=include_code,
                # Currently we only support run mode,
                # which doesn't require an LSP server
                lsp_server=NoopLspServer(),
                user_config_manager=user_config_mgr,
                # We don't pass any CLI args for now
                # since we don't want to read arbitrary args and apply them
                # to each application
                cli_args={},
                auth_token=AuthToken(""),
            )
            app = create_starlette_app(
                base_url="",
                lifespan=lifespans.Lifespans(
                    [
                        # Not all lifespans are needed for run mode
                        lifespans.etc,
                        lifespans.signal_handler,
                    ]
                ),
                enable_auth=not AuthToken.is_empty(auth_token),
                allow_origins=("*",),
            )
            app.state.session_manager = session_manager
            app.state.base_url = "/_marimo"
            app.state.config_manager = user_config_mgr

            return app

    return Builder()
