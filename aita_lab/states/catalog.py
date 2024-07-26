from typing import Optional

import logging

import reflex as rx
from sqlmodel import select

from aita.datasource.base import DataSource


class CatalogTable(rx.Model, table=True):
    """The Catalog Table Model."""

    datasource_name: str
    catalog_name: str
    schema: str
    table: str


class CatalogState(rx.State):
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
    def commit(catalog: str, schema: str, table: str, datasource_name: Optional[str] = None):
        with rx.session() as session:
            session.add(
                CatalogTable(
                    catalog_name=catalog,
                    schema=schema,
                    table=table,
                    datasource_name=datasource_name,
                )
            )
            session.commit()

    @staticmethod
    def crawl_data_catalog(datasource_name, datasource: DataSource):
        # catalog = datasource.get_metadata()
        # for schema in catalog.catalog_db_schemas:
        #     for table in schema.db_schema_tables:
        #         try:
        #             CatalogState.commit(
        #                 catalog=catalog.catalog_name,
        #                 schema=schema.db_schema_name,
        #                 table=table.table_name,
        #                 datasource_name=datasource_name,
        #             )
        #         except Exception as e:
        #             logging.error(f"Failed to crawl data catalog: {e}")
        return datasource.crawl_data_catalog()

    def on_load(self):
        self.load_entries()
