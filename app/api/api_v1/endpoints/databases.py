from typing import Any

from fastapi import APIRouter

from app.schemas import DataBaseCreate, DataBaseResponse
from app.crud import crud_database
from app.api.deps import SessionDep

router = APIRouter()


@router.post("/create", response_model=DataBaseResponse)
def create(session: SessionDep, database_in: DataBaseCreate) -> Any:
    return crud_database.create(session, database_in)


@router.get("/list", response_model=DataBaseResponse)
def list(session: SessionDep) -> Any:
    return crud_database.list(session)


@router.post("/update", response_model=DataBaseResponse)
def update(session: SessionDep, database_in: DataBaseCreate) -> Any:
    return crud_database.update(session, database_in)


@router.post("/delete", response_model=DataBaseResponse)
def delete(session: SessionDep, database_in: DataBaseCreate) -> Any:
    return crud_database.remove(session, database_in)
