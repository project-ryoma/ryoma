import logging
from typing import List, Optional
import datetime

import reflex as rx
from databuilder.loader.base_loader import Loader
from databuilder.loader.generic_loader import GenericLoader
from databuilder.models.table_metadata import TableMetadata
from langchain_core.embeddings import Embeddings
from pyhocon import ConfigTree

from ryoma_lab.apis import catalog as catalog_api
from ryoma_lab.apis import embedding as embedding_api
from ryoma_lab.models.data_catalog import Catalog, Table
from ryoma_lab.services import vector_store as vector_store_service
from ryoma_lab.states.ai import AIState
from ryoma_lab.states.base import BaseState
from ryoma_lab.states.datasource import DataSourceState
from ryoma_lab.states.vector_store import VectorStoreState


class CatalogState(BaseState):
    current_catalog_id: Optional[int] = None
    current_schema_id: Optional[int] = None
    catalogs: List[Catalog] = []
    selected_table: Optional[str] = None

    # vector store configuration
    vector_store_project_name: str = ""
    feature_view_name: str = ""

    def set_selected_table(self,
                           table: str):
        self.selected_table = table

    @rx.var
    def table_metadata(self) -> Optional[Table]:
        if not self.selected_table:
            return None
        return catalog_api.get_table_metadata(self.selected_table)

    def load_entries(self):
        self.catalogs = catalog_api.load_catalogs()

    def _load_catalog_record(self,
                             record: TableMetadata):
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
            def __init__(self,
                         callback_func):
                self._callback_func = callback_func

            def init(self,
                     conf: ConfigTree) -> None:
                self.conf = conf
                self._callback_func = self._callback_func

        return SessionLoader(self._load_catalog_record)

    def crawl_data_catalog(self,
                           datasource_name: Optional[str] = None):
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

    async def get_embedding_client(self) -> Embeddings:
        aistate = await self.get_state(AIState)
        return embedding_api.get_embedding_client(
            aistate.embedding.model, aistate.embedding.model_parameters
        )

    def _get_embedding_content(self,
                               table: Table):
        return f"Table: {table['name']}\nColumns: {table['columns']}\nDescription: {table['description']}"

    async def _get_fs(self):
        vector_store_state = await self.get_state(VectorStoreState)
        project = vector_store_state.get_project(self.vector_store_project_name)
        return vector_store_service.get_feature_store(project, self.vector_store_config)

    async def index_data_catalog(self,
                                 table: Table):
        logging.info(f"Indexing table {table}")
        embedding_client = await self.get_embedding_client()
        if not embedding_client:
            return
        embedded_table_content = embedding_client.embed_query(
            self._get_embedding_content(table)
        )
        fs = await self._get_fs()
        feature_view = vector_store_service.get_feature_view_by_name(fs, self.feature_view_name)
        embedding_feature_inputs = vector_store_service.build_vector_feature_inputs(
            feature_view=feature_view,
            inputs=embedded_table_content,
            entity_value=table["name"]
        )

        vector_store_service.index_feature_from_data(fs, self.feature_view_name, embedding_feature_inputs)

    def on_load(self):
        self.current_catalog_id = None
        self.current_schema_id = None
        self.catalogs = []
        self.selected_table = None
        self.load_entries()
