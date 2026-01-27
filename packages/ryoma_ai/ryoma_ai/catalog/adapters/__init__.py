"""
Open Catalog adapters for different database systems.

The IbisOpenCatalogAdapter is the recommended universal adapter that works
with ALL Ibis-supported databases (PostgreSQL, MySQL, Snowflake, BigQuery,
DuckDB, SQLite, etc.) using a single implementation.

For reference implementations and examples, see the `reference/` package.
"""

from ryoma_ai.catalog.adapters.ibis_adapter import IbisOpenCatalogAdapter

__all__ = ["IbisOpenCatalogAdapter"]
