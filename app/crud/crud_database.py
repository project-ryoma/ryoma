from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import DataBase
from app.schemas.database import DataBaseCreate, DataBaseUpdate


class CRUDDataBase(CRUDBase[DataBase, DataBaseCreate, DataBaseUpdate]):
    def get_by_id(self, session: Session, id: str):
        return session.query(DataBase).filter(DataBase.id == id).first()

    def list(self, session: Session):
        return session.query(DataBase).all()


crud_database = CRUDDataBase(DataBase)
