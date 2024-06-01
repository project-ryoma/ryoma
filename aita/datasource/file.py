from typing import Optional, Any

from langchain_core.pydantic_v1 import BaseModel, Field
from aita.datasource.base import DataSource
from aita.datasource.catalog import Catalog
import pyarrow as pa


class FileDataSource(DataSource):
    type: str = "file"
    file_path: str = Field(..., description="Path to the file")
    file_format: str = Field(..., description="Format of the file")
    file_name: str = Field(..., description="Name of the file")

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, file_path: str, file_format: str, file_name: Optional[str] = None, **kwargs):
        if not file_name:
            file_name = file_path
        super().__init__(
            file_path=file_path,
            file_name=file_name,
            file_format=file_format,
        )

    def get_metadata(self, **kwargs) -> Catalog:
        table_schema = self.arrow_table.schema
        return Catalog(catalog_name=self.file_name,
                       columns=[{"column_name": name, "column_type": str(table_schema.field(name))} for name in
                                table_schema.names])

    def to_arrow(self, **kwargs) -> pa.Table:
        if self.file_format == "csv":
            from pyarrow.csv import read_csv
            return read_csv(self.file_path, **kwargs)
        elif self.file_format == "parquet":
            from pyarrow.parquet import read_table
            return read_table(self.file_path, **kwargs)
        elif self.file_format == "json":
            from pyarrow.json import read_json
            return read_json(self.file_path, **kwargs)
        else:
            raise NotImplementedError(f"FileFormat is unsupported: {self.file_format}")

    def to_pandas(self, **kwargs):
        return self.to_arrow().to_pandas()

