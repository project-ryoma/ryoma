import logging
from typing import Any, Dict, List, Optional, Union

import reflex as rx
from ryoma_ai.datasource.base import DataSource, SqlDataSource
from ryoma_ai.datasource.factory import DataSourceFactory
from ryoma_lab.models.datasource import DataSourceTable
from sqlmodel import select


class DataSourceService:
    def __init__(self):
        self.session = rx.session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def get_datasource_by_name(self, datasource_name: str) -> Optional[DataSourceTable]:
        return self.session.exec(
            select(DataSourceTable).where(DataSourceTable.name == datasource_name)
        ).first()

    def get_datasource_configs(self, ds: DataSourceTable) -> dict[str, str]:
        if ds.connection_url:
            return {"connection_url": ds.connection_url}
        else:
            return eval(ds.attributes)

    def load_datasources(self) -> List[DataSourceTable]:
        return self.session.exec(select(DataSourceTable)).all()

    def get_datasource_by_id(self, id: int) -> Optional[DataSourceTable]:
        return self.session.get(DataSourceTable, id)

    def save_datasource(
        self, datasource: Union[dict[str, Any], DataSourceTable] = None
    ) -> DataSourceTable:
        if not isinstance(datasource, DataSourceTable):
            datasource = DataSourceTable(**datasource)
        self.session.add(datasource)
        self.session.commit()
        self.session.refresh(datasource)
        return datasource

    def update_datasource(self, id: int, data: Dict) -> Optional[DataSourceTable]:
        datasource = self.session.get(DataSourceTable, id)
        if datasource:
            for key, value in data.items():
                setattr(datasource, key, value)
            self.session.commit()
            self.session.refresh(datasource)
        return datasource

    def delete_datasource(self, id: int) -> bool:
        datasource = self.session.get(DataSourceTable, id)
        if datasource:
            self.session.delete(datasource)
            self.session.commit()
            return True
        return False

    @staticmethod
    def connect_datasource(datasource_type: str, configs: dict) -> SqlDataSource:
        try:
            source = DataSourceFactory.create_datasource(datasource_type, **configs)
            source.connect()
            logging.info(f"Connected to {datasource_type}")
            return source
        except Exception as e:
            logging.error(f"Failed to connect to {datasource_type}: {e}")
            raise

    def connect_datasource_by_name(self, datasource_name: str) -> DataSource:
        datasource = self.get_datasource_by_name(datasource_name)
        if not datasource:
            raise ValueError(f"Datasource {datasource_name} not found")
        configs = self.get_datasource_configs(datasource)
        return self.connect_datasource(datasource.type, configs)
