import reflex as rx
from aita.datasource.catalog import Catalog


class CatalogState(rx.State):

    catalogs: list[Catalog] = []