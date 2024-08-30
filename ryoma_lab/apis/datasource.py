import reflex as rx
import logging
from typing import List, Dict, Optional, Any
from sqlmodel import select
from ryoma.datasource.factory import DataSourceFactory
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


def load_datasource_entries() -> List[DataSource]:
    with rx.session() as session:
        return session.exec(select(DataSource)).all()


def get_datasource_by_id(id: int) -> Optional[DataSource]:
    with rx.session() as session:
        return session.get(DataSource, id)


def create_datasource(data: Dict) -> DataSource:
    with rx.session() as session:
        datasource = DataSource(**data)
        session.add(datasource)
        session.commit()
        session.refresh(datasource)
        return datasource


def update_datasource(id: int,
                      data: Dict) -> Optional[DataSource]:
    with rx.session() as session:
        datasource = session.get(DataSource, id)
        if datasource:
            for key, value in data.items():
                setattr(datasource, key, value)
            session.commit()
            session.refresh(datasource)
        return datasource


def delete_datasource(id: int) -> bool:
    with rx.session() as session:
        datasource = session.get(DataSource, id)
        if datasource:
            session.delete(datasource)
            session.commit()
            return True
        return False


def get_all_datasources() -> Dict[str, DataSource]:
    with rx.session() as session:
        datasources = session.exec(select(DataSource)).all()
        logging.info(f"Retrieved {len(datasources)} datasources from the database")
        return {ds.name: ds for ds in datasources}


def connect_datasource(datasource: DataSource):
    try:
        configs = datasource.attributes
        configs["connection_url"] = datasource.connection_url
        source = DataSourceFactory.create_datasource(datasource.datasource, **configs)
        source.connect()
        logging.info(f"Connected to {datasource.datasource}")
        return source
    except Exception as e:
        logging.error(f"Failed to connect to {datasource.datasource}: {e}")
        raise


def connect_datasource_by_name(datasource_name: str) -> Any:
    datasource = get_datasource_by_name(datasource_name)
    if not datasource:
        raise ValueError(f"Datasource {datasource_name} not found")
    configs = eval(datasource.attributes)
    configs["connection_url"] = datasource.connection_url
    return connect_datasource(datasource.datasource, **configs)


def get_datasource_configs(ds: DataSource) -> dict[str, str]:
    if ds.connection_url:
        return {"connection_url": ds.connection_url}
    else:
        return eval(ds.attributes)
