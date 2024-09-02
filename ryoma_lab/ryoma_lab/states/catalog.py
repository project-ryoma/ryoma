import logging
from typing import List, Optional

import reflex as rx
from databuilder.loader.base_loader import Loader
from databuilder.loader.generic_loader import GenericLoader
from databuilder.models.table_metadata import TableMetadata
from pyhocon import ConfigTree

from ryoma_lab.apis import catalog as catalog_api
from ryoma_lab.models.data_catalog import Catalog, Table
from ryoma_lab.states.datasource import DataSourceState


class CatalogState(rx.State):
    current_catalog_id: Optional[int] = None
    current_schema_id: Optional[int] = None
    catalogs: List[Catalog] = []
    selected_table: Optional[str] = None

    def set_selected_table(self, table: str):
        self.selected_table = table

    @rx.var
    def table_metadata(self) -> Optional[Table]:
        if not self.selected_table:
            return None
        return catalog_api.get_table_metadata(self.selected_table)

    def load_entries(self):
        self.catalogs = catalog_api.load_catalogs()

    def _load_catalog_record(self, record: TableMetadata):
        logging.info(f"Loading catalog entry to database: {record}")

        catalog_api.commit_catalog_record(
            table=record.name,
            columns=record.columns,
            schema_id=self.current_schema_id,
            description=record.description.text if record.description else None,
            is_view=record.is_view,
            attrs=str(record.attrs),
        )

    def _record_loader(self) -> Loader:
        class SessionLoader(GenericLoader):
            def __init__(self, callback_func):
                self._callback_func = callback_func

            def init(self, conf: ConfigTree) -> None:
                self.conf = conf
                self._callback_func = self._callback_func

        return SessionLoader(self._load_catalog_record)

    def crawl_data_catalog(self, datasource_name: Optional[str] = None):
        datasource = DataSourceState.connect(datasource_name)
        try:
            (
                self.current_catalog_id,
                self.current_schema_id,
            ) = catalog_api.commit_catalog(
                datasource_name,
                datasource.database,
                datasource.db_schema,
            )
            datasource.crawl_data_catalog(loader=self._record_loader())

            # reload the catalog entries
            self.load_entries()
        except Exception as e:
            rx.toast(str(e))

    def on_load(self):
        self.current_catalog_id = None
        self.current_schema_id = None
        self.catalogs = []
        self.selected_table = None
        self.load_entries()
