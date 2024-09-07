from typing import Optional

import reflex as rx


class DataSourceModel(rx.Model, table=True):
    """The DataSource model."""

    __tablename__ = "datasource"

    name: str
    type: str
    connection_url: Optional[str]
    attributes: Optional[str]
    catalog_id: Optional[int] = None
    index_id: Optional[int] = None

    @property
    def attributes_dict(self) -> dict:
        return eval(self.attributes)
