from typing import Optional

import reflex as rx
from feast import FeatureStore

from ryoma_lab.models.data_catalog import CatalogTable, SchemaTable
from ryoma_lab.services.catalog import CatalogService
from ryoma_lab.states.base import BaseState


class WorkspaceState(BaseState):
    _current_store: Optional[FeatureStore] = None

    current_catalog_name: str = ""
    current_schema_name: str = ""
    catalogs: list[CatalogTable] = []
    schemas: list[SchemaTable] = []
    catalog_dialog_open: bool = False
    schema_dialog_open: bool = False

    def set_catalog_name(self, catalog_name: str):
        if catalog_name == "custom":
            return rx.redirect("/datasource")
        self.current_catalog_name = catalog_name
        self.schema_dialog_open = True
        self.schemas = self.current_catalog.schemas

    def toggle_catalog_dialog(self, is_open: bool):
        self.catalog_dialog_open = is_open

    def toggle_schema_dialog(self, is_open: bool):
        self.schema_dialog_open = is_open

    @rx.var
    def current_catalog(self) -> Optional[CatalogTable]:
        if not self.current_catalog_name:
            return None
        res = next(
            (
                catalog
                for catalog in self.catalogs
                if catalog.catalog_name == self.current_catalog_name
            ),
            None,
        )
        return res

    def set_current_schema_name(self, schema_name: str):
        self.current_schema_name = schema_name

    def load_workspaces(self):
        with CatalogService() as catalog_service:
            self.catalogs = catalog_service.load_catalogs()

    def on_load(self) -> None:
        self.load_workspaces()
