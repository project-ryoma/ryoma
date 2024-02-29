# item = CRUDBase[Item, ItemCreate, ItemUpdate](Item)
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models import User, UserCreate, DataSource, DataSourceConnect

from .crud_item import item
from .crud_user import user
from .crud_datasource import datasource

# For a new basic set of CRUD operations you could just do

# from .base import CRUDBase
# from app.models.item import Item
# from app.schemas.item import ItemCreate, ItemUpdate


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.from_orm(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_user_by_email(*, session: Session, email: str) -> Optional[User]:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(session=session, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def connect_datasource(*, session: Session, datasource_connect: DataSourceConnect) -> DataSource:
    db_obj = DataSource.from_orm(datasource_connect, update={"connected": True})
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def get_datasource_by_id(*, session: Session, id: str) -> Optional[DataSource]:
    statement = select(DataSource).where(DataSource.id == id)
    session_datasource = session.exec(statement).first()
    return session_datasource
