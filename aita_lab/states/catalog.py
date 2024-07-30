from typing import Any, Dict, List, Optional

import logging

import reflex as rx
from databuilder.loader.base_loader import Loader
from databuilder.loader.generic_loader import GenericLoader
from databuilder.models.table_metadata import ColumnMetadata, TableMetadata
from pyhocon import ConfigTree
from sqlalchemy.orm import joinedload
from sqlmodel import Field, Relationship, Session, select

from aita_lab.states.datasource import DataSourceState


class Catalog(rx.Model, table=True):
    """The Catalog Table Model."""

    id: Optional[int] = Field(default=None, primary_key=True)
    datasource: str
    database: str

    schemas: List["Schema"] = Relationship(back_populates="catalog")


class Schema(rx.Model, table=True):
    """The Schema Model."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    tables: List["Table"] = Relationship(back_populates="schema")

    catalog_id: Optional[int] = Field(default=None, foreign_key="catalog.id")
    catalog: Optional[Catalog] = Relationship(back_populates="schemas")


class Table(rx.Model, table=True):
    """The Table Model."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    is_view: Optional[bool] = False
    attrs: Optional[str] = None
    columns: List["Column"] = Relationship(back_populates="table")

    schema_id: Optional[int] = Field(default=None, foreign_key="schema.id")
    schema: Optional[Schema] = Relationship(back_populates="tables")


class Column(rx.Model, table=True):
    """The Column Model."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    type: str
    description: Optional[str] = None

    table_id: Optional[int] = Field(default=None, foreign_key="table.id")
    table: Optional[Table] = Relationship(back_populates="columns")


class CatalogState(rx.State):
    current_datasource: Optional[str] = None
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
        with rx.session() as session:
            table_metadata = session.exec(
                select(Table)
                .options(joinedload(Table.columns))
                .filter(Table.name == self.selected_table)
            ).first()
            return table_metadata

    def load_entries(self):
        with rx.session() as session:
            result = session.exec(
                select(Catalog).options(joinedload(Catalog.schemas).joinedload(Schema.tables))
            ).unique()
            self.catalogs = result.all()

    def _commit_catalog_record(
        self,
        table: str,
        columns: List[ColumnMetadata],
        description: Optional[str] = None,
        is_view: Optional[bool] = False,
        attrs: Optional[str] = None,
        **kwargs,
    ):
        with rx.session() as session:
            _table = session.exec(
                select(Table).filter(
                    Table.name == table,
                    Table.schema_id == self.current_schema_id,
                )
            ).first()
            if not _table:
                _table = Table(
                    name=table,
                    description=description,
                    is_view=is_view,
                    attrs=attrs,
                    schema_id=self.current_schema_id,
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

    def _load_catalog_record(self, record: TableMetadata):
        logging.info(f"Loading catalog entry to database: {record}")

        self._commit_catalog_record(
            table=record.name,
            columns=record.columns,
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

    def _commit_catalog(self, session: Session, datasource: str, database: str, schema: str):

        # check if catalog already exists
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
        self.current_catalog_id = _catalog.id

        _schema = session.exec(
            select(Schema).filter(
                Schema.name == schema,
                Schema.catalog_id == self.current_catalog_id,
            )
        ).first()
        if not _schema:
            _schema = Schema(name=schema, catalog_id=self.current_catalog_id)
            session.add(_schema)
            session.commit()
            session.refresh(_schema)
        self.current_schema_id = _schema.id

    def crawl_data_catalog(self):
        datasource = DataSourceState.connect(self.current_datasource)
        try:
            with rx.session() as session:
                self._commit_catalog(
                    session,
                    self.current_datasource,
                    datasource.database,
                    datasource.db_schema,
                )
                datasource.crawl_data_catalog(loader=self._record_loader())

            # reload the catalog entries
            self.load_entries()
        except NotImplementedError as e:
            rx.toast(e)

    def on_load(self):
        self.current_datasource = None
        self.current_catalog_id = None
        self.current_schema_id = None
        self.catalogs = []
        self.selected_table = None
        self.load_entries()
