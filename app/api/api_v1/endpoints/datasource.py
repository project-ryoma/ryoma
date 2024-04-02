from fastapi import APIRouter

from aita.datasource.factory import DataSourceFactory
from app.schemas import ConnectionParams, DataSourceConnect, DataSourceConnectResponse, DataSourceCreate
from app.crud import crud_datasource
from app.api.deps import SessionDep

router = APIRouter()


@router.post("/connect", response_model=DataSourceConnectResponse)
def connect(session: SessionDep, connection_params: ConnectionParams):
    datasource_connect = DataSourceConnect(
        name=connection_params.datasource,
        connected=True,
    )
    crud_datasource.connect(session, datasource_connect=datasource_connect)

    return DataSourceConnectResponse(
        status="success", message=f"Connected to {connection_params.datasource}"
    )


@router.post("/create", response_model=DataSourceConnectResponse)
def create(session: SessionDep, datasource_in: DataSourceCreate):
    conn = DataSourceFactory.create_datasource(**datasource_in.dict())
    datasource = DataSourceCreate(
        name=datasource_in.name,
        description=datasource_in.description,
        enabled=datasource_in.enabled,
        connection_string=datasource_in.connection_string,
    )
    crud_datasource.create(session=session, datasource=datasource)
    
    return DataSourceConnectResponse(
        status="success", message=f"Created Data Source: {datasource_in.datasource}"
    )