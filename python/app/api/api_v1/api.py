from fastapi import APIRouter

from app.api.api_v1.endpoints import items, login, users, utils, chat, datasource, health, favicon, autocomplete

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(datasource.router, prefix="/datasource", tags=["datasource"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(favicon.router, prefix="/favicon.ico", tags=["favicon"])
api_router.include_router(autocomplete.router, prefix="/autocomplete", tags=["autocomplete"])
