from typing import List, Optional

from pydantic import BaseModel


class Column(BaseModel):
    column_name: str
    xdbc_type_name: str
    xdbc_nullable: bool
    primary_key: Optional[bool] = None


class Table(BaseModel):
    table_columns: List[Column]
    table_name: str


class DatabaseSchema(BaseModel):
    db_schema_name: str
    db_schema_tables: List[Table]


class Catalog(BaseModel):
    catalog_name: str
    catalog_db_schemas: List[DatabaseSchema]
