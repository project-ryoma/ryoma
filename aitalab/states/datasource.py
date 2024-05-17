from typing import List

from aita.datasource.sql import SqlDataSource
from sqlmodel import select
import reflex as rx


class DataSource(SqlDataSource, rx.Model, table=True):
    """The SqlDataSource model."""


class DataSourceState(rx.State):
    name: str
    datasource_type: str
    connection_url: str
    datasources: list[DataSource] = []
    num_datasources: int

    def load_entries(self) -> List[DataSource]:
        with rx.session() as session:
            self.datasources = session.exec(select(DataSource)).all()
            self.num_datasources = len(self.datasources)

            if self.sort_value:
                self.datasources = sorted(
                    self.datasources, key=lambda datasource: getattr(datasource, self.sort_value).lower()
                )
            return self.datasources

    def sort_values(self, sort_value: str):
        self.sort_value = sort_value
        self.load_entries()

    def set_datasource(self, datasource: DataSource):
        self.name = datasource.name
        self.datasource_type = datasource.name
        self.connection_url = datasource.connection_url

    def add_datasource(self):
        with rx.session() as session:
            session.add(
                DataSource(
                    connection_url=self.connection_url
                )
            )
            session.commit()
        self.load_entries()
        return rx.window_alert(f"User {self.name} has been added.")

    def update_datasource(self):
        with rx.session() as session:
            datasource = session.exec(
                select(DataSource).where(DataSource.id == self.id)
            ).first()
            datasource.name = self.name
            datasource.connection_url = self.connection_url
            session.add(datasource)
            session.commit()
        self.load_entries()

    def delete_datasource(self, datasource_id: str):
        with rx.session() as session:
            datasource = session.exec(
                select(DataSource).where(DataSource.id == datasource_id)
            ).first()
            session.delete(datasource)
            session.commit()
        self.load_entries()
