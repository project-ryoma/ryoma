from typing import List, Optional

from pydantic import BaseModel, Field


class Column(BaseModel):
    column_name: str = Field(..., description="Name of the column", alias="column_name")
    xdbc_type_name: str = Field(..., description="Type of the column", alias="column_type")
    xdbc_nullable: Optional[bool] = Field(None, description="Whether the column is nullable", alias="nullable")
    primary_key: Optional[bool] = Field(None, description="Whether the column is a primary key", alias="primary_key")


class Table(BaseModel):
    table_columns: List[Column] = Field(..., description="List of columns in the table", alias="columns")
    table_name: str = Field(..., description="Name of the table", alias="table_name")


class DatabaseSchema(BaseModel):
    db_schema_name: str = Field(..., description="Name of the database schema", alias="schema_name")
    db_schema_tables: List[Table] = Field(..., description="List of tables in the schema", alias="tables")


class Catalog(BaseModel):
    catalog_name: str = Field(..., description="Name of the catalog", alias="catalog_name")
    catalog_db_schemas: Optional[List[DatabaseSchema]] = Field(None, description="List of database schemas in the catalog", alias="schemas")
    catalog_tables: Optional[List[Table]] = Field(None, description="List of tables in the catalog", alias="tables")
    catalog_columns: Optional[List[Column]] = Field(None, description="List of columns in the catalog", alias="columns")
