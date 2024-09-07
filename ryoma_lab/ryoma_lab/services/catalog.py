import uuid
from typing import List, Optional, Tuple

import reflex as rx
from databuilder.models.table_metadata import ColumnMetadata, TableMetadata
from sqlalchemy.orm import joinedload
from sqlmodel import select

from ryoma_lab.models.data_catalog import Catalog, Column, Schema, Table


class CatalogService:
    def __init__(self):
        self.session = rx.session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def load(self) -> List[Catalog]:
        result = self.session.exec(
            select(Catalog).options(
                joinedload(Catalog.schemas).joinedload(Schema.tables)
            )
        ).unique()
        return result.all()

    def get_table_metadata(self, table_name: str) -> Optional[Table]:
        table_metadata = self.session.exec(
            select(Table)
            .options(joinedload(Table.columns))
            .filter(Table.name == table_name)
        ).first()
        return table_metadata

    def upsert_table(
        self,
        table: str,
        columns: List[ColumnMetadata],
        schema_id: int,
        description: Optional[str] = None,
        is_view: Optional[bool] = False,
        attrs: Optional[str] = None,
    ):
        _table = self.session.exec(
            select(Table).filter(
                Table.name == table,
                Table.schema_id == schema_id,
            )
        ).first()
        if not _table:
            _table = Table(
                name=table,
                description=description,
                is_view=is_view,
                attrs=attrs,
                schema_id=schema_id,
            )
            self.session.add(_table)
            self.session.commit()
            self.session.refresh(_table)

        for column in columns:
            _column = Column(
                name=column.name,
                type=column.type,
                description=column.description.text if column.description else None,
                table_id=_table.id,
            )
            self.session.add(_column)
        self.session.commit()

    def upsert(self, datasource_name: str, database: str, schema: Optional[str] = None):
        _catalog = self.session.exec(
            select(Catalog).filter(
                Catalog.datasource == datasource_name,
                Catalog.database == database,
            )
        ).first()
        if not _catalog:
            _catalog = Catalog(
                datasource=datasource_name,
                database=database,
            )
            self.session.add(_catalog)
            self.session.commit()
            self.session.refresh(_catalog)
        if schema:
            _schema = self.session.exec(
                select(Schema).filter(
                    Schema.name == schema,
                    Schema.catalog_id == _catalog.id,
                )
            ).first()
            if not _schema:
                _schema = Schema(name=schema, catalog_id=_catalog.id)
                self.session.add(_schema)
                self.session.commit()
                self.session.refresh(_schema)
            return _catalog.id, _schema.id

    def get_catalog_id(self, datasource_name: str, database: str) -> Optional[int]:
        _catalog = self.session.exec(
            select(Catalog).filter(
                Catalog.datasource == datasource_name,
                Catalog.database == database,
            )
        ).first()
        return _catalog.id if _catalog else None

    def get_schema_id(self, catalog_id: int, schema_name: str) -> Optional[int]:
        _schema = self.session.exec(
            select(Schema).filter(
                Schema.catalog_id == catalog_id,
                Schema.name == schema_name,
            )
        ).first()
        return _schema.id if _schema else None
