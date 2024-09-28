import uuid
from typing import List, Optional

import reflex as rx
from sqlmodel import Field, Relationship


class CatalogTable(rx.Model, table=True):
    """The Catalog Table Model."""

    __tablename__ = "catalog"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36
    )
    datasource: Optional[str] = Field(None, description="Name of the datasource")
    catalog_name: str = Field(
        ..., description="Name of the catalog, also known as the database name"
    )

    schemas: List["SchemaTable"] = Relationship(back_populates="catalog")


class SchemaTable(rx.Model, table=True):
    """The Schema Model."""

    __tablename__ = "schema"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36
    )
    schema_name: str
    tables: List["TableTable"] = Relationship(back_populates="schema")

    catalog_id: Optional[str] = Field(default=None, foreign_key="catalog.id")
    catalog: Optional[CatalogTable] = Relationship(back_populates="schemas")


class TableTable(rx.Model, table=True):
    """The Table Model."""

    __tablename__ = "table"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36
    )
    table_name: str
    description: Optional[str] = None
    is_view: Optional[bool] = False
    attrs: Optional[str] = None
    columns: List["ColumnTable"] = Relationship(back_populates="table")

    schema_id: Optional[str] = Field(default=None, foreign_key="schema.id")
    schema: Optional[SchemaTable] = Relationship(back_populates="tables")


class ColumnTable(rx.Model, table=True):
    """The Column Model."""

    __tablename__ = "column"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36
    )
    name: str
    type: str
    description: Optional[str] = None

    table_id: Optional[str] = Field(default=None, foreign_key="table.id")
    table: Optional[TableTable] = Relationship(back_populates="columns")
