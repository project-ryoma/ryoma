from fastapi import APIRouter

from aita.datasource.factory import DataSourceFactory
from app.models import ConnectionParams, DataSourceConnect, DataSourceConnectResponse
from app import crud
from app.api.deps import SessionDep

router = APIRouter()


@router.post("/connect", response_model=DataSourceConnectResponse)
def connect(session: SessionDep, connection_params: ConnectionParams):
    conn = DataSourceFactory.create_datasource(**connection_params.dict())
    datasource_connect = DataSourceConnect(
        name=connection_params.datasource,
        connection_string=conn.connection_string,
        connected=True,
    )
    crud.connect_datasource(session=session, datasource_connect=datasource_connect)

    return DataSourceConnectResponse(
        status="success", message=f"Connected to {connection_params.datasource}"
    )
