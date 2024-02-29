# create a CRUDDataSource class that will be used to interact with the datasource
# support functions: connect, disconnect

from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models import DataSource
from app.schemas.datasource import DataSourceConnect, DataSourceDisconnect

class CRUDDataSource:
    def connect(self, db: Session, *, obj_in: DataSourceConnect) -> DataSource:
        db_obj = DataSource(
            name=obj_in.name,
            connection_string=obj_in.connection_string,
            connected=obj_in.connected,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def disconnect(self, db: Session, *, obj_in: DataSourceDisconnect) -> DataSource:
        db_obj = DataSource(
            name=obj_in.name,
            connected=obj_in.connected,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj