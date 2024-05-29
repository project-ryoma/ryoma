from typing import List

from aita.datasource.base import DataSource
from aita.datasource.catalog import Catalog


class FileDataSource(DataSource):
    file_path: str
    file_format: str
    name: str

    def __init__(self, file_path: str, name: str, format: str = None):
        self.file_path = file_path
        self.file_format = format
        self.name = name
        super().__init__(type="file", file_path=self.file_path, file_format=self.file_format, name=self.name)

    def get_metadata(self, **kwargs) -> Catalog:
        table_schema = self.to_arrow().schema
        return Catalog(catalog_name=self.name,
                       columns=[{"column_name": name, "column_type": str(table_schema.field(name))} for name in
                                table_schema.names])

    def to_arrow(self, **kwargs):
        if self.file_format == "csv":
            from pyarrow.csv import read_csv
            return read_csv(self.file_path)
        elif self.file_format == "parquet":
            from pyarrow.parquet import read_table
            return read_table(self.file_path)
        elif self.file_format == "json":
            from pyarrow.json import read_json
            return read_json(self.file_path)
        else:
            raise NotImplementedError(f"FileFormat is unsupported: {self.file_format}")

    def to_pandas(self, **kwargs):
        return self.to_arrow().to_pandas()
