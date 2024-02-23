from fastapi import APIRouter

from aita.datasource.factory import DataSourceFactory
from aita.metadb import state_store
from app.models import ConnectionParams

router = APIRouter()


@router.post("/connect")
def connect(connection_params: ConnectionParams):
    conn = DataSourceFactory.create_datasource(**connection_params.dict())

    state_store.cache[connection_params.datasource] = conn
    return {"status": "Success", "message": f"Connected to datasource: {connection_params.datasource}"}
