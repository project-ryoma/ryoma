import reflex as rx
from sqlmodel import select

from ryoma_lab.models.vector_store import VectorStore


def get_projects() -> list[VectorStore]:
    with rx.session() as session:
        return list(session.exec(select(VectorStore)).all())


def delete_project(project_name: str):
    with rx.session() as session:
        session.query(VectorStore).filter_by(project_name=project_name).delete()
        session.commit()


def save_project(
    project_name: str,
    online_store: str,
    online_store_configs: dict[str, str],
    offline_store: str,
    offline_store_configs: dict[str, str],
) -> None:
    with rx.session() as session:
        session.add(
            VectorStore(
                project_name=project_name,
                online_store=online_store,
                offline_store=offline_store,
                online_store_configs=str(online_store_configs),
                offline_store_configs=str(offline_store_configs),
            )
        )
        session.commit()
