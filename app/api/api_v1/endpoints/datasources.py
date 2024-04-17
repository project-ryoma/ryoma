from typing import Any

from fastapi import APIRouter

from app.schemas import DataSourceCreate, DataSourceResponse
from app.crud import crud_datasource
from app.api.deps import SessionDep

router = APIRouter()


@router.post("/create", response_model=DataSourceResponse)
def create(session: SessionDep, DataSource_in: DataSourceCreate) -> Any:
    return crud_datasource.create(session, DataSource_in)


@router.get("/list", response_model=DataSourceResponse)
def list(session: SessionDep) -> Any:
    return crud_datasource.list(session)


@router.post("/update", response_model=DataSourceResponse)
def update(session: SessionDep, DataSource_in: DataSourceCreate) -> Any:
    return crud_datasource.update(session, DataSource_in)


@router.post("/delete", response_model=DataSourceResponse)
def delete(session: SessionDep, DataSource_in: DataSourceCreate) -> Any:
    return crud_datasource.remove(session, DataSource_in)
