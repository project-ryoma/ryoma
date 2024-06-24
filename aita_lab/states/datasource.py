from typing import List, Optional

import logging

import reflex as rx
from sqlmodel import select

from aita.datasource.factory import DataSourceFactory, DataSourceProvider
from aita_lab.states.catalog import CatalogState


class DataSource(rx.Model, table=True):
    """The SqlDataSource model."""

    name: str
    datasource_type: str
    connection_url: str


class DataSourceState(rx.State):
    id: str
    name: str
    datasource_names: list[str] = []
    datasource_type: str
    datasources: list[DataSource] = []
    num_datasources: int
    sort_value: str
    is_open: bool = False
    allow_crawl_catalog: bool = True

    # DataSource related attributes
    connection_url: str
    open_alert: bool = False

    def toggle_dialog(self):
        self.is_open = not self.is_open

    def change_crawl_catalog(self, value: bool):
        self.allow_crawl_catalog = value

    @rx.var
    def datasource_attributes(self) -> List[str]:
        if self.datasource_type:
            model_fields = DataSourceProvider[self.datasource_type].value.__fields__
            return [key for key in model_fields.keys() if key != "type" and key != "name"]
        else:
            return []

    @rx.var
    def missing_attributes(self) -> bool:
        # required by all datasources
        if not self.datasource_type or not self.name:
            return True

        # required by specific datasource
        model_fields = DataSourceProvider[self.datasource_type].value.__fields__
        if not all(
            getattr(self, key) for key in model_fields.keys() if key != "type" and key != "name"
        ):
            return True
        return False

    def set_datasource_attributes(self, attribute: str, value: str):
        setattr(self, attribute, value)

    def get_datasource_attributes(self) -> Optional[dict]:
        if self.datasource_type:
            model_fields = DataSourceProvider[self.datasource_type].value.__fields__
            return {key: getattr(self, key) for key in model_fields.keys() if key != "type"}
        else:
            return None

    def load_entries(self):
        with rx.session() as session:
            self.datasources = session.exec(select(DataSource)).all()
            self.num_datasources = len(self.datasources)

            if self.sort_value:
                self.datasources = sorted(
                    self.datasources,
                    key=lambda datasource: getattr(datasource, self.sort_value).lower(),
                )
            self.datasource_names = [datasource.name for datasource in self.datasources]

    def sort_values(self, sort_value: str):
        self.sort_value = sort_value
        self.load_entries()

    def set_datasource(self, datasource: DataSource):
        self.id = datasource["id"]
        self.name = datasource["name"]
        self.datasource_type = datasource["datasource_type"]
        self.connection_url = datasource["connection_url"]

    def connect_and_add_datasource(self):
        if self.missing_attributes:
            return
        config = self.get_datasource_attributes()
        try:
            ds = DataSourceFactory.create_datasource(self.datasource_type, **config)
            ds.connect()
            logging.info(f"Connected to {self.datasource_type}")
        except Exception as e:
            logging.error(f"Failed to connect to {self.datasource_type}: {e}")
            return
        if self.allow_crawl_catalog:
            CatalogState.crawl_data_catalog(self.name, ds)
        with rx.session() as session:
            session.add(
                DataSource(
                    name=self.name,
                    datasource_type=self.datasource_type,
                    connection_url=self.connection_url,
                )
            )
            session.commit()
        self.load_entries()
        self.toggle_dialog()

    def update_datasource(self):
        with rx.session() as session:
            datasource = session.exec(select(DataSource).where(DataSource.id == self.id)).first()
            datasource.name = self.name
            datasource.connection_url = self.connection_url
            session.add(datasource)
            session.commit()
        self.load_entries()

    def delete_datasource(self, datasource_id: str):
        with rx.session() as session:
            datasource = session.exec(
                select(DataSource).where(DataSource.id == datasource_id)
            ).first()
            session.delete(datasource)
            session.commit()
        self.load_entries()

    @staticmethod
    def get_datasource_by_name(datasource_name: str):
        with rx.session() as session:
            datasource = session.exec(
                select(DataSource).where(DataSource.name == datasource_name)
            ).first()
            return datasource

    @staticmethod
    def connect(datasource_name: str) -> Optional[DataSource]:
        datasource = DataSourceState.get_datasource_by_name(datasource_name)
        if not datasource:
            return
        try:
            source = DataSourceFactory.create_datasource(
                datasource.datasource_type, connection_url=datasource.connection_url
            )
            source.connect()
            logging.info(f"Connected to {datasource.datasource_type}")
            return source
        except Exception as e:
            logging.error(f"Failed to connect to {datasource.datasource_type}: {e}")

    def on_load(self):
        self.load_entries()
