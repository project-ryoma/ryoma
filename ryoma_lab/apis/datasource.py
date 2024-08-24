import reflex as rx
from sqlmodel import select

from ryoma_lab.models.datasource import DataSource


def get_datasource_by_name(datasource_name: str):
    with rx.session() as session:
        datasource = session.exec(
            select(DataSource).where(DataSource.name == datasource_name)
        ).first()
        return datasource


def get_datasource_configs(ds: DataSource) -> dict[str, str]:
    if ds.connection_url:
        return {"connection_url": ds.connection_url}
    else:
        return eval(ds.attributes)
