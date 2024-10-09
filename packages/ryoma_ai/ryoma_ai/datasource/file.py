from typing import Any, Optional

import pyarrow as pa
from ryoma_ai.datasource.base import DataSource
from ryoma_ai.datasource.metadata import Table


class FileConfig:
    pass


class FileDataSource(DataSource):
    type: str = "file"
    file_path: str
    file_format: str
    file_name: str

    def __init__(
        self,
        file_path: str,
        file_format: str,
        file_name: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(
            type="file",
        )
        if not file_name:
            file_name = file_path
        self.file_path = file_path
        self.file_format = file_format
        self.file_name = file_name

    def get_catalog(self, **kwargs) -> Table:
        table_schema = self.to_arrow(**kwargs).schema
        return Table(
            table_name=self.file_name,
            table_columns=[
                {"column_name": name, "column_type": str(table_schema.field(name))}
                for name in table_schema.names
            ],
        )

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
