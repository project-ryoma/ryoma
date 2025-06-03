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

    def get_column(self, column_name: str) -> Optional[Column]:
        """
        Get a column by its name from the table.

        Args:
              column_name: The name of the column to retrieve.

        Returns:
              Column object if found, otherwise None.
        """
        for column in self.columns:
            if column.name == column_name:
                return column
        return None


class Schema(BaseModel):
    schema_name: str = Field(..., description="Name of the schema")
    tables: Optional[List[Table]] = Field(
        None, description="List of tables in the schema"
    )

    class Config:
        populate_by_name = True

    def get_table(self, table_name: str) -> Optional[Table]:
        """
        Get a table by its name from the schema.

        Args:
            table_name: The name of the table to retrieve.

        Returns:
            Table object if found, otherwise None.
        """
        for table in self.tables or []:
            if table.table_name == table_name:
                return table
        return None


class Catalog(BaseModel):
    catalog_name: str = Field(
        ..., description="Name of the catalog, also known as the database name"
    )
    schemas: Optional[List[Schema]] = Field(
        None, description="List of catalog schemas in the catalog"
    )

    class Config:
        populate_by_name = True

    def get_schema(self, schema_name: str) -> Optional[Schema]:
        """
        Get a schema by its name from the catalog.

        Args:
            schema_name: The name of the schema to retrieve.

        Returns:
            Schema object if found, otherwise None.
        """
        for schema in self.schemas or []:
            if schema.schema_name == schema_name:
                return schema
        return None

    @property
    def prompt(self):
        """
        Generate a prompt for the catalog.

        Returns:
            str: A prompt string summarizing the catalog.
        """
        prompt = f"Catalog: {self.catalog_name}\n"
        for schema in self.schemas or []:
            prompt += f"  Schema: {schema.schema_name}\n"
            for table in schema.tables or []:
                prompt += f"    Table: {table.table_name}\n"
                for column in table.columns:
                    prompt += f"      Column: {column.name} ({column.type})\n"
        return prompt
