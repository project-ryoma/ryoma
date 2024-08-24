from typing import Optional

import reflex as rx


class DataSource(rx.Model, table=True):
    """The SqlDataSource model."""

    name: str
    datasource: str
    connection_url: Optional[str]
    attributes: Optional[str]
    catalog_id: Optional[int] = None

    @property
    def attributes_dict(self) -> dict:
        return eval(self.attributes)
