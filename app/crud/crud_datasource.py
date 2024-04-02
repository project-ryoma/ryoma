# create a CRUDDataSource class that will be used to interact with the datasource
# support functions: connect, disconnect

from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import DataSource
from app.schemas.datasource import DataSourceConnect, DataSourceDisconnect, DataSourceCreate, DataSourceUpdate


class CRUDDataSource(CRUDBase[DataSource, DataSourceCreate, DataSourceUpdate]):
    def connect(self, session: Session, *, datasource_connect: DataSourceConnect) -> DataSource:
        db_obj = DataSource(
            name=datasource_connect.name,
            connected=datasource_connect.connected,
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def disconnect(self, session: Session, *, data_source_disconnect: DataSourceDisconnect) -> DataSource:
        db_obj = DataSource(
            name=data_source_disconnect.name,
            connected=data_source_disconnect.connected,
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def get_by_id(self, session: Session, id: str):
        return session.query(DataSource).filter(DataSource.id == id).first()


crud_datasource = CRUDDataSource(DataSource)
