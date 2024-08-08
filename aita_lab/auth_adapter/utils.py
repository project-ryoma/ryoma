from typing import Any, AsyncGenerator

import secrets
from dataclasses import dataclass
from pathlib import Path

import reflex as rx
from fastapi import Depends, FastAPI
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from aita_lab.states.base import OAuthAccount, User

rx_config = rx.config.get_config()
from fps_auth.config import _AuthConfig


@dataclass
class Res:
    User: Any
    async_session_maker: Any
    get_async_session: Any
    get_user_db: Any
    secret: Any


def get_db(auth_config: _AuthConfig) -> Res:
    jupyter_dir = (
        Path.home() / ".local" / "share" / "jupyter"
        if auth_config.directory is None
        else Path(auth_config.directory)
    )
    jupyter_dir.mkdir(parents=True, exist_ok=True)
    name = "jupyverse"
    if auth_config.test:
        name += "_test"
    secret_path = jupyter_dir / f"{name}_secret"
    # userdb_path = jupyter_dir / f"{name}_users.db"
    userdb_path = "reflex.db"

    if auth_config.clear_users:
        if userdb_path.is_file():
            userdb_path.unlink()
        if secret_path.is_file():
            secret_path.unlink()
    if auth_config.mode == "token":
        if secret_path.is_file():
            secret_path.unlink()

    if not secret_path.is_file():
        secret_path.write_text(secrets.token_hex(32))

    secret = secret_path.read_text()

    database_url = f"sqlite+aiosqlite:///{userdb_path}"

    engine = create_async_engine(database_url)
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

    async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
        async with async_session_maker() as session:
            yield session

    async def get_user_db(session: AsyncSession = Depends(get_async_session)):
        yield SQLAlchemyUserDatabase(session, User, OAuthAccount)

    return Res(
        User=User,
        async_session_maker=async_session_maker,
        get_async_session=get_async_session,
        get_user_db=get_user_db,
        secret=secret,
    )
