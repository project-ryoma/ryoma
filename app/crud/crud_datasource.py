from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import DataSource
from app.schemas.datasource import DataSourceCreate, DataSourceUpdate


class CRUDDataSource(CRUDBase[DataSource, DataSourceCreate, DataSourceUpdate]):
    def get_by_id(self, session: Session, id: str):
        return session.query(DataSource).filter(DataSource.id == id).first()

    def list(self, session: Session):
        return session.query(DataSource).all()


crud_datasource = CRUDDataSource(DataSource)
