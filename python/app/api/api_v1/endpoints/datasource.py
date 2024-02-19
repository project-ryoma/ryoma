from fastapi import APIRouter

from aita.datasource.factory import DataSourceFactory
from aita.metadb import state_store
from app.models import ConnectionParams

router = APIRouter()


@router.post("/")
def connect(datasource: str, connection_params: ConnectionParams):
    conn = DataSourceFactory.create_datasource(datasource=datasource, **connection_params.dict())

    state_store.cache[datasource] = conn
    return {"status": "Success", "message": f"Connected to datasource: {datasource}"}
