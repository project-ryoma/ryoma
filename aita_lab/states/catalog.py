from typing import Any, Optional

import reflex as rx
from databuilder.loader.base_loader import Loader
from databuilder.loader.generic_loader import GenericLoader
from databuilder.models.table_metadata import TableMetadata
from pyhocon import ConfigFactory
from sqlmodel import select

from aita_lab.states.datasource import DataSourceState


class CatalogTable(rx.Model, table=True):
    """The Catalog Table Model."""

    datasource_name: str
    catalog_name: str
    schema: str
    table: str


class CatalogState(rx.State):
    current_datasource: Optional[str] = None
    catalogs: list[CatalogTable] = []

    is_open: bool = False
    sort_value: str = ""

    def toggle_dialog(self):
        self.is_open = not self.is_open

    def add_catalog(self, catalog: CatalogTable):
        self.commit(*catalog)
        self.load_entries()

    def delete_catalog(self, catalog: CatalogTable):
        self.catalogs.remove(catalog)

    def sort_values(self, value: str):
        self.sort_value = value
        self.catalogs = sorted(self.catalogs, key=lambda x: getattr(x, value))

    def load_entries(self):
        with rx.session() as session:
            self.catalogs = session.exec(select(CatalogTable)).all()

            if self.sort_value:
                self.catalogs = sorted(
                    self.catalogs,
                    key=lambda catalog: getattr(catalog, self.sort_value).lower(),
                )

    @staticmethod
    def commit(datasource_name: str, catalog: str, schema: str, table: str):
        with rx.session() as session:
            session.add(
                CatalogTable(
                    datasource_name=datasource_name,
                    catalog_name=catalog,
                    schema=schema,
                    table=table,
                )
            )
            session.commit()

    def _load_catalog_entries(self, record: TableMetadata):
        self.commit(
            record.database,
            record.cluster,
            record.schema,
            record.name,
        )

    def _data_source_loader(self) -> Loader:
        loader = GenericLoader()
        loader.init(ConfigFactory.from_dict({"callback_function": self.commit}))
        return GenericLoader()

    def crawl_data_catalog(self):
        datasource = DataSourceState.connect(self.current_datasource)
        try:
            datasource.crawl_data_catalog(loader=self._data_source_loader())
        except NotImplementedError as e:
            rx.toast(e)

    def on_load(self):
        self.load_entries()
