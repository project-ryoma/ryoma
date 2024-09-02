import reflex as rx
from sqlmodel import select

from ryoma_lab.models.vector_store import VectorStore


def get_feature_stores() -> list[VectorStore]:
    with rx.session() as session:
        return list(session.exec(select(VectorStore)).all())
