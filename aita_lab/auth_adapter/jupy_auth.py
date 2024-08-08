import contextlib
import json
import logging
import random
from typing import Any, Callable, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends
from sqlalchemy import select  # type: ignore

from jupyverse_api import Router
from jupyverse_api.app import App
from jupyverse_api.auth import Auth
from jupyverse_api.frontend import FrontendConfig

from fps_auth.backends import get_backend
from fps_auth.config import _AuthConfig
from .utils import get_db
from fps_auth.models import UserCreate, UserRead, UserUpdate

logger = logging.getLogger("auth")


def auth_factory(
        app: App,
        auth_config: _AuthConfig,
        frontend_config: FrontendConfig,
):
    db = get_db(auth_config)
    backend = get_backend(auth_config, frontend_config, db)

    get_async_session_context = contextlib.asynccontextmanager(db.get_async_session)
    get_user_db_context = contextlib.asynccontextmanager(db.get_user_db)
    get_user_manager_context = contextlib.asynccontextmanager(backend.get_user_manager)

    @contextlib.asynccontextmanager
    async def _get_user_manager():
        async with get_async_session_context() as session:
            async with get_user_db_context(session) as user_db:
                async with get_user_manager_context(user_db) as user_manager:
                    yield user_manager

    async def create_user(**kwargs):
        async with _get_user_manager() as user_manager:
            await user_manager.create(UserCreate(**kwargs))

    async def update_user(user, **kwargs):
        async with _get_user_manager() as user_manager:
            await user_manager.update(UserUpdate(**kwargs), user)

    async def get_user_by_email(user_email):
        async with _get_user_manager() as user_manager:
            return await user_manager.get_by_email(user_email)

    class _Auth(Auth, Router):
        def __init__(self) -> None:
            super().__init__(app)

            self.db = db

            router = APIRouter()

            @router.get("/auth/users")
            async def get_users(
                    user: UserRead = Depends(backend.current_user(permissions={"admin": ["read"]})),
            ):
                async with db.async_session_maker() as session:
                    statement = select(db.User)
                    users = (await session.execute(statement)).unique().all()
                return [usr.User for usr in users if usr.User.is_active]

            @router.get("/api/me")
            async def get_api_me(
                    permissions: Optional[str] = None,
                    user: UserRead = Depends(backend.current_user()),
                    update_user=Depends(backend.update_user),
            ):
                checked_permissions: Dict[str, List[str]] = {}
                if permissions is None:
                    permissions = "{}"
                else:
                    permissions = permissions.replace("'", '"')
                permissions_dict = json.loads(permissions)
                if permissions_dict:
                    user_permissions = user.permissions
                    for resource, actions in permissions_dict.items():
                        user_resource_permissions = user_permissions.get(resource)
                        if user_resource_permissions is None:
                            continue
                        allowed = checked_permissions[resource] = []
                        for action in actions:
                            if action in user_resource_permissions:
                                allowed.append(action)

                keys = ["username", "name", "display_name", "initials", "avatar_url", "color"]
                identity = {k: getattr(user, k) for k in keys}
                if not identity["name"] and not identity["display_name"]:
                    moon = get_anonymous_username()
                    identity["name"] = f"Anonymous {moon}"
                    identity["display_name"] = f"Anonymous {moon}"
                    identity["initials"] = f"A{moon[0]}"
                    await update_user(
                        dict(
                            name=identity["name"],
                            display_name=identity["display_name"],
                            permissions=checked_permissions,
                        )
                    )
                return {
                    "identity": identity,
                    "permissions": checked_permissions,
                }

            # redefine GET /me because we want our current_user dependency
            # it is first defined in users_router and so it wins over the one in
            # fapi_users.get_users_router
            users_router = APIRouter()

            @users_router.get("/me")
            async def get_me(
                    user: UserRead = Depends(backend.current_user(permissions={"admin": ["read"]})),
            ):
                return user

            users_router.include_router(backend.fapi_users.get_users_router(UserRead, UserUpdate))

            # Cookie based auth login and logout
            self.include_router(
                backend.fapi_users.get_auth_router(backend.cookie_authentication), prefix="/auth"
            )
            self.include_router(
                backend.fapi_users.get_register_router(UserRead, UserCreate),
                prefix="/auth",
                dependencies=[Depends(backend.current_user(permissions={"admin": ["write"]}))],
            )
            self.include_router(users_router, prefix="/auth/user")

            # GitHub OAuth register router
            self.include_router(
                backend.fapi_users.get_oauth_router(
                    backend.github_authentication, backend.github_cookie_authentication, db.secret
                ),
                prefix="/auth/github",
            )
            self.include_router(router)

            self.create_user = create_user
            self.__update_user = update_user
            self.get_user_by_email = get_user_by_email

        async def _update_user(self, user, **kwargs):
            return await self.__update_user(user, **kwargs)

        def current_user(self, permissions: Optional[Dict[str, List[str]]] = None) -> Callable:
            return backend.current_user(permissions)

        async def update_user(self, update_user=Depends(backend.update_user)) -> Callable:
            return update_user

        def websocket_auth(
                self,
                permissions: Optional[Dict[str, List[str]]] = None,
        ) -> Callable[[], Tuple[Any, Dict[str, List[str]]]]:
            return backend.websocket_auth(permissions)

    return _Auth()


# From https://en.wikipedia.org/wiki/Moons_of_Jupiter
moons_of_jupyter = (
    "Metis",
    "Adrastea",
    "Amalthea",
    "Thebe",
    "Io",
    "Europa",
    "Ganymede",
    "Callisto",
    "Themisto",
    "Leda",
    "Ersa",
    "Pandia",
    "Himalia",
    "Lysithea",
    "Elara",
    "Dia",
    "Carpo",
    "Valetudo",
    "Euporie",
    "Eupheme",
    # 'S/2003 J 18',
    # 'S/2010 J 2',
    "Helike",
    # 'S/2003 J 16',
    # 'S/2003 J 2',
    "Euanthe",
    # 'S/2017 J 7',
    "Hermippe",
    "Praxidike",
    "Thyone",
    "Thelxinoe",
    # 'S/2017 J 3',
    "Ananke",
    "Mneme",
    # 'S/2016 J 1',
    "Orthosie",
    "Harpalyke",
    "Iocaste",
    # 'S/2017 J 9',
    # 'S/2003 J 12',
    # 'S/2003 J 4',
    "Erinome",
    "Aitne",
    "Herse",
    "Taygete",
    # 'S/2017 J 2',
    # 'S/2017 J 6',
    "Eukelade",
    "Carme",
    # 'S/2003 J 19',
    "Isonoe",
    # 'S/2003 J 10',
    "Autonoe",
    "Philophrosyne",
    "Cyllene",
    "Pasithee",
    # 'S/2010 J 1',
    "Pasiphae",
    "Sponde",
    # 'S/2017 J 8',
    "Eurydome",
    # 'S/2017 J 5',
    "Kalyke",
    "Hegemone",
    "Kale",
    "Kallichore",
    # 'S/2011 J 1',
    # 'S/2017 J 1',
    "Chaldene",
    "Arche",
    "Eirene",
    "Kore",
    # 'S/2011 J 2',
    # 'S/2003 J 9',
    "Megaclite",
    "Aoede",
    # 'S/2003 J 23',
    "Callirrhoe",
    "Sinope",
)


def get_anonymous_username() -> str:
    """
    Get a random user-name based on the moons of Jupyter.
    This function returns names like "Anonymous Io" or "Anonymous Metis".
    """
    return moons_of_jupyter[random.randint(0, len(moons_of_jupyter) - 1)]
