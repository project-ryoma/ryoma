import logging
from typing import Optional

import reflex as rx
from databuilder.loader.base_loader import Loader
from databuilder.loader.generic_loader import GenericLoader
from databuilder.models.table_metadata import TableMetadata
from langchain_core.embeddings import Embeddings
from pyhocon import ConfigTree
from ryoma_lab.models.data_catalog import TableTable
from ryoma_lab.services import embedding as embedding_service
from ryoma_lab.services.catalog import CatalogService
from ryoma_lab.services.vector_store import VectorStoreService
from ryoma_lab.states.ai import AIState
from ryoma_lab.states.datasource import DataSourceState


class CatalogState(DataSourceState):
    current_catalog_id: Optional[int] = None
    current_schema_id: Optional[int] = None
    selected_table: Optional[str] = None

    # vector store configuration
    vector_store_project_name: str = ""
    feature_view_name: str = ""

    def set_selected_table(self, table: str):
        self.selected_table = table

    @rx.var
    def table_metadata(self) -> Optional[TableTable]:
        if not self.selected_table:
            return None
        with CatalogService() as catalog_service:
            return catalog_service.get_table_metadata(self.selected_table)

    def _load_catalog_record(self, record: TableMetadata):
        logging.info(f"Loading catalog entry to database: {record}")

        with CatalogService() as catalog_service:
            catalog_service.save_table(
                table_name=record.name,
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

    def sync_catalog(self, datasource_name: str):
        logging.info(f"Start crawling metadata for datasource {datasource_name}")
        datasource = DataSourceState.connect(datasource_name)
        with CatalogService() as catalog_service:
            self.current_catalog_id = catalog_service.get_catalog_id(
                datasource_name, datasource.database
            )
            if not self.current_catalog_id:
                catalog_service.save_catalog(
                    datasource_name, datasource.database, datasource.db_schema
                )
            self.current_schema_id = catalog_service.get_schema_id(
                self.current_catalog_id, datasource.db_schema
            )
        try:
            datasource.get_catalog(loader=self._record_loader())
            # reload the catalog entries
            self.load_catalogs()
        except Exception as e:
            rx.toast(str(e))

    async def get_embedding_client(self) -> Embeddings:
        aistate = await self.get_state(AIState)
        return embedding_service.get_embedding_client(
            aistate.embedding.model, aistate.embedding.model_parameters
        )

    def _get_table_embedding_content(self, table: TableTable):
        return f"""
Table: {table["table_name"]}
Description: {table["description"]}
Columns: {table["columns"]}
"""

    async def index_table(self, table: TableTable):
        logging.info(f"Indexing table {table}")
        embedding_client = await self.get_embedding_client()
        if not embedding_client:
            return
        table_embeddings = embedding_client.embed_query(
            self._get_table_embedding_content(table)
        )
        with VectorStoreService() as vector_store_service:
            vector_store_service.index_feature_view(
                self.vector_store_project_name,
                self.feature_view_name,
                table_embeddings,
                table["table_name"],
            )
        logging.info(f"Table {table} indexed")

    def on_load(self):
        self.load_catalogs()
