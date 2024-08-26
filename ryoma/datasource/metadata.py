from typing import List, Optional

from pydantic import BaseModel, Field


class Column(BaseModel):
    name: str = Field(..., description="Name of the column")
    type: Optional[str] = Field(
        None, description="Type of the column", alias="column_type"
    )
    nullable: Optional[bool] = Field(
        None, description="Whether the column is nullable", alias="nullable"
    )
    primary_key: Optional[bool] = Field(
        None, description="Whether the column is a primary key"
    )

    class Config:
        populate_by_name = True


class Table(BaseModel):
    table_name: str = Field(..., description="Name of the table")
    columns: List[Column] = Field(..., description="List of columns in the table")

    class Config:
        populate_by_name = True


class Database(BaseModel):
    database_name: str = Field(
        ..., description="Name of the database", alias="schema_name"
    )
    tables: List[Table] = Field(..., description="List of tables in the database")

    class Config:
        populate_by_name = True


class Catalog(BaseModel):
    catalog_name: str = Field(..., description="Name of the catalog")
    databases: Optional[List[Database]] = Field(
        None, description="List of database schemas in the catalog"
    )

    class Config:
        populate_by_name = True
