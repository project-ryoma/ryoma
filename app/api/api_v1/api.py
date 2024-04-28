from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    agent,
    autocomplete,
    datasources,
    favicon,
    health,
    login,
    users,
    utils,
)

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(agent.router, prefix="/agent", tags=["agent"])
api_router.include_router(datasources.router, prefix="/datasources", tags=["datasources"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(favicon.router, prefix="/favicon.ico", tags=["favicon"])
api_router.include_router(autocomplete.router, prefix="/autocomplete", tags=["autocomplete"])
