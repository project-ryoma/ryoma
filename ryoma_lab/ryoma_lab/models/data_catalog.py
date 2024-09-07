import uuid
from typing import List, Optional

import reflex as rx
from sqlmodel import Field, Relationship


class Catalog(rx.Model, table=True):
    """The Catalog Table Model."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36
    )
    datasource: str
    database: str

    schemas: List["Schema"] = Relationship(back_populates="catalog")


class Schema(rx.Model, table=True):
    """The Schema Model."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36
    )
    name: str
    tables: List["Table"] = Relationship(back_populates="schema")

    catalog_id: Optional[str] = Field(default=None, foreign_key="catalog.id")
    catalog: Optional[Catalog] = Relationship(back_populates="schemas")


class Table(rx.Model, table=True):
    """The Table Model."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36
    )
    name: str
    description: Optional[str] = None
    is_view: Optional[bool] = False
    attrs: Optional[str] = None
    columns: List["Column"] = Relationship(back_populates="table")

    schema_id: Optional[str] = Field(default=None, foreign_key="schema.id")
    schema: Optional[Schema] = Relationship(back_populates="tables")


class Column(rx.Model, table=True):
    """The Column Model."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36
    )
    name: str
    type: str
    description: Optional[str] = None

    table_id: Optional[str] = Field(default=None, foreign_key="table.id")
    table: Optional[Table] = Relationship(back_populates="columns")
