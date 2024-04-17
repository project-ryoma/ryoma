from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud import crud_user
from app.core.config import settings
from app.models import User # noqa: F401
from app.schemas import UserCreate


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    # Base.metadata.create_all(bind=engine)
    user = session.execute(select(User).where(User.email == settings.FIRST_SUPERUSER)).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud_user.create(session=session, obj_in=user_in)
