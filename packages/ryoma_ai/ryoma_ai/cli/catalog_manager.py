"""
Catalog Manager for Ryoma AI CLI

Handles catalog indexing and search operations.
"""

from rich.console import Console
from ryoma_ai.datasource.base import DataSource
from ryoma_ai.store import CatalogStore


class CatalogManager:
    """Manages catalog indexing and search operations."""

    def __init__(self, console: Console):
        """
        Initialize the catalog manager.

        Args:
            console: Rich console for output
        """
        self.console = console
        self.catalog_store = CatalogStore()

    def index_catalog(
        self, datasource_id: str, datasource: DataSource, level: str = "table"
    ) -> bool:
        """
        Index a catalog for search.

        Args:
            datasource_id: ID of the data source
            datasource: DataSource instance
            level: Index level (catalog, schema, table, column)

        Returns:
            bool: True if indexing successful
        """
        try:
            with self.console.status(f"[yellow]Indexing catalog at {level} level..."):
                catalog_id = self.catalog_store.index_catalog(
                    data_source_id=datasource_id,
                    datasource=datasource,
                    index_level=level,
                )

            self.console.print(
                f"[green]✅ Catalog indexed with ID: {catalog_id}[/green]"
            )
            return True

        except Exception as e:
            self.console.print(f"[red]Failed to index catalog: {e}[/red]")
            return False

    def search_catalogs(self, query: str, top_k: int = 5) -> list:
        """
        Search catalogs using semantic search.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of search results
        """
        try:
            with self.console.status("[yellow]Searching catalogs..."):
                results = self.catalog_store.search_catalogs(query, top_k=top_k)

            return results

        except Exception as e:
            self.console.print(f"[red]Catalog search failed: {e}[/red]")
            return []
