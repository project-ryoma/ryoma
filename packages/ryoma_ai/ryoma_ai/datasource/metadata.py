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


class Schema(BaseModel):
    schema_name: str = Field(..., description="Name of the schema")
    tables: Optional[List[Table]] = Field(
        None, description="List of tables in the schema"
    )

    class Config:
        populate_by_name = True


class Catalog(BaseModel):
    catalog_name: str = Field(
        ..., description="Name of the catalog, also known as the database name"
    )
    schemas: Optional[List[Schema]] = Field(
        None, description="List of catalog schemas in the catalog"
    )

    class Config:
        populate_by_name = True
