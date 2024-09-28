from typing import List, Optional

import reflex as rx
from databuilder.models.table_metadata import ColumnMetadata
from ryoma_lab.models.data_catalog import (
    CatalogTable,
    ColumnTable,
    SchemaTable,
    TableTable,
)
from sqlalchemy.orm import joinedload
from sqlmodel import select


class CatalogService:
    def __init__(self):
        self.session = rx.session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def load_catalogs(self) -> List[CatalogTable]:
        result = self.session.exec(
            select(CatalogTable).options(
                joinedload(CatalogTable.schemas).joinedload(SchemaTable.tables)
            )
        ).unique()
        return result.all()

    def get_table_metadata(self, table_name: str) -> Optional[TableTable]:
        table_metadata = self.session.exec(
            select(TableTable)
            .options(joinedload(TableTable.columns))
            .filter(TableTable.table_name == table_name)
        ).first()
        return table_metadata

    def save_table(
        self,
        table_name: str,
        columns: List[ColumnMetadata],
        schema_id: int,
        description: Optional[str] = None,
        is_view: Optional[bool] = False,
        attrs: Optional[str] = None,
    ):
        _table = self.session.exec(
            select(TableTable).filter(
                TableTable.table_name == table_name,
                TableTable.schema_id == schema_id,
            )
        ).first()
        if not _table:
            _table = TableTable(
                table_name=table_name,
                description=description,
                is_view=is_view,
                attrs=attrs,
                schema_id=schema_id,
            )
            self.session.add(_table)
            self.session.commit()
            self.session.refresh(_table)

        for column in columns:
            _column = ColumnTable(
                name=column.name,
                type=column.type,
                description=column.description.text if column.description else None,
                table_id=_table.id,
            )
            self.session.add(_column)
        self.session.commit()

    def save_catalog(
        self, datasource_name: str, catalog_name: str, schema_name: Optional[str] = None
    ):
        _catalog = self.session.exec(
            select(CatalogTable).filter(
                CatalogTable.datasource == datasource_name,
                CatalogTable.catalog_name == catalog_name,
            )
        ).first()
        if not _catalog:
            _catalog = CatalogTable(
                datasource=datasource_name,
                catalog_name=catalog_name,
            )
            self.session.add(_catalog)
            self.session.commit()
            self.session.refresh(_catalog)
        if schema_name:
            _schema = self.session.exec(
                select(SchemaTable).filter(
                    SchemaTable.schema_name == schema_name,
                    SchemaTable.catalog_id == _catalog.id,
                )
            ).first()
            if not _schema:
                _schema = SchemaTable(schema_name=schema_name, catalog_id=_catalog.id)
                self.session.add(_schema)
                self.session.commit()
                self.session.refresh(_schema)

    def get_catalog_id(self, datasource_name: str, catalog_name: str) -> Optional[int]:
        _catalog = self.session.exec(
            select(CatalogTable).filter(
                CatalogTable.datasource == datasource_name,
                CatalogTable.catalog_name == catalog_name,
            )
        ).first()
        return _catalog.id if _catalog else None

    def get_schema_id(self, catalog_id: int, schema_name: str) -> Optional[int]:
        _schema = self.session.exec(
            select(SchemaTable).filter(
                SchemaTable.catalog_id == catalog_id,
                SchemaTable.schema_name == schema_name,
            )
        ).first()
        return _schema.id if _schema else None
