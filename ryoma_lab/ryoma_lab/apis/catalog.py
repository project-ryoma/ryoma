from typing import List, Optional

import reflex as rx
from databuilder.models.table_metadata import ColumnMetadata, TableMetadata
from sqlalchemy.orm import joinedload
from sqlmodel import select

from ryoma_lab.models.data_catalog import Catalog, Column, Schema, Table


def load_catalogs():
    with rx.session() as session:
        result = session.exec(
            select(Catalog).options(
                joinedload(Catalog.schemas).joinedload(Schema.tables)
            )
        ).unique()
        return result.all()


def get_table_metadata(table_name: str) -> Optional[Table]:
    with rx.session() as session:
        table_metadata = session.exec(
            select(Table)
            .options(joinedload(Table.columns))
            .filter(Table.name == table_name)
        ).first()
        return table_metadata


def commit_catalog_record(
    table: str,
    columns: List[ColumnMetadata],
    schema_id: int,
    description: Optional[str] = None,
    is_view: Optional[bool] = False,
    attrs: Optional[str] = None,
):
    with rx.session() as session:
        _table = session.exec(
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
            session.add(_table)
            session.commit()
            session.refresh(_table)

        for column in columns:
            _column = Column(
                name=column.name,
                type=column.type,
                description=column.description.text if column.description else None,
                table_id=_table.id,
            )
            session.add(_column)
        session.commit()


def commit_catalog(datasource: str, database: str, schema: str) -> tuple[int, int]:
    with rx.session() as session:
        _catalog = session.exec(
            select(Catalog).filter(
                Catalog.datasource == datasource,
                Catalog.database == database,
            )
        ).first()
        if not _catalog:
            _catalog = Catalog(
                datasource=datasource,
                database=database,
            )
            session.add(_catalog)
            session.commit()
            session.refresh(_catalog)
        catalog_id = _catalog.id

        _schema = session.exec(
            select(Schema).filter(
                Schema.name == schema,
                Schema.catalog_id == catalog_id,
            )
        ).first()
        if not _schema:
            _schema = Schema(name=schema, catalog_id=catalog_id)
            session.add(_schema)
            session.commit()
            session.refresh(_schema)
        schema_id = _schema.id

    return catalog_id, schema_id
