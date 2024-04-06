from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    autocomplete,
    chat,
    databases,
    favicon,
    health,
    login,
    users,
    utils,
    tools,
)

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(datasource.router, prefix="/datasource", tags=["datasource"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(favicon.router, prefix="/favicon.ico", tags=["favicon"])
api_router.include_router(autocomplete.router, prefix="/autocomplete", tags=["autocomplete"])
api_router.include_router(tools.router, prefix="/tools", tags=["tools"])
