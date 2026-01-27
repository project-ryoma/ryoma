"""
Protocol definition for Open Catalog adapters.

Defines the interface that all database-specific adapters must implement
to provide unified metadata access across systems.
"""

from typing import Any, Dict, List, Literal, Optional, Protocol

from ryoma_ai.catalog.open_catalog.filters import SearchFilter
from ryoma_ai.catalog.open_catalog.models import (
    ColumnMetadata,
    RelationshipMetadata,
    SearchResult,
    TableMetadata,
)


class OpenCatalogAdapter(Protocol):
    """
    Protocol for database-agnostic metadata access.

    All Open Catalog adapters must implement this interface to provide
    deterministic, zero-indexing metadata search across different systems.

    Based on RFC-001: Open Catalog

    Example:
        >>> adapter = PostgresOpenCatalogAdapter(datasource)
        >>> tables = adapter.search_tables(pattern="*customer*", limit=10)
        >>> for table in tables:
        ...     print(table.name, table.row_count)
    """

    def search_tables(
        self,
        pattern: Optional[str] = None,
        schema: Optional[str] = None,
        filters: Optional[SearchFilter] = None,
        limit: int = 100,
    ) -> List[TableMetadata]:
        """
        Search for tables matching a pattern and filters.

        This is the primary discovery operation, equivalent to:
            find . -name "*pattern*"  # In filesystem
            rg "pattern"              # In code search

        Args:
            pattern: Glob-style pattern for table names
                     Examples: "*customer*", "dim_*", "fact_*_daily"
                     If None, matches all tables
            schema: Optional schema name to limit search scope
            filters: Additional filters (has_column, row_count, etc.)
            limit: Maximum number of results to return (default: 100)

        Returns:
            List of TableMetadata objects matching the search criteria

        Raises:
            SearchTimeoutError: If search exceeds timeout
            TooManyResultsError: If results exceed limit significantly

        Example:
            >>> # Find all customer-related tables with email column
            >>> filter = SearchFilter(has_column="email")
            >>> tables = adapter.search_tables(
            ...     pattern="*customer*",
            ...     filters=filter,
            ...     limit=10
            ... )
        """
        ...

    def search_columns(
        self,
        pattern: Optional[str] = None,
        table: Optional[str] = None,
        data_type: Optional[str] = None,
        filters: Optional[SearchFilter] = None,
        limit: int = 100,
    ) -> List[ColumnMetadata]:
        """
        Search for columns across tables.

        Useful for finding where specific fields exist (e.g., "email", "id").

        Args:
            pattern: Glob-style pattern for column names
                     Examples: "*email*", "created_*", "is_*"
            table: Optional table name to limit search to specific table
            data_type: Optional data type filter (VARCHAR, INTEGER, etc.)
            filters: Additional filters
            limit: Maximum number of results to return (default: 100)

        Returns:
            List of ColumnMetadata objects matching the search criteria

        Raises:
            TableNotFoundException: If specified table doesn't exist
            SearchTimeoutError: If search exceeds timeout

        Example:
            >>> # Find all email columns across all tables
            >>> columns = adapter.search_columns(
            ...     pattern="*email*",
            ...     limit=20
            ... )
            >>>
            >>> # Find all columns in customers table
            >>> columns = adapter.search_columns(table="customers")
        """
        ...

    def inspect_table(
        self,
        qualified_name: str,
        include_sample_data: bool = False,
        sample_limit: int = 10,
    ) -> TableMetadata:
        """
        Get complete metadata for a specific table.

        This is the "zoom in" operation after narrowing search results.
        Provides full schema, statistics, and optionally sample data.

        Args:
            qualified_name: Fully qualified table name
                           (e.g., "schema.table" or "database.schema.table")
            include_sample_data: Whether to fetch sample rows
            sample_limit: Number of sample rows to fetch (default: 10)

        Returns:
            TableMetadata with complete schema information

        Raises:
            TableNotFoundException: If table doesn't exist

        Example:
            >>> # Get full schema for customers table
            >>> table = adapter.inspect_table("public.customers")
            >>> print(f"Columns: {[col.name for col in table.columns]}")
            >>> print(f"Rows: {table.row_count}")
            >>>
            >>> # Include sample data for verification
            >>> table = adapter.inspect_table(
            ...     "public.customers",
            ...     include_sample_data=True,
            ...     sample_limit=5
            ... )
        """
        ...

    def get_relationships(
        self,
        table: str,
        direction: Literal["incoming", "outgoing", "both"] = "both",
    ) -> List[RelationshipMetadata]:
        """
        Get foreign key relationships for a table.

        Discovers how tables connect to each other via foreign keys,
        enabling intelligent join suggestions.

        Args:
            table: Qualified table name
            direction: Which relationships to include:
                      - "incoming": Tables that reference this table
                      - "outgoing": Tables this table references
                      - "both": All relationships (default)

        Returns:
            List of RelationshipMetadata objects

        Raises:
            TableNotFoundException: If table doesn't exist

        Example:
            >>> # Find all tables that reference customers
            >>> relationships = adapter.get_relationships(
            ...     "customers",
            ...     direction="incoming"
            ... )
            >>> for rel in relationships:
            ...     print(f"{rel.from_table} -> {rel.to_table}")
        """
        ...

    def get_sample_data(
        self,
        table: str,
        limit: int = 10,
        columns: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get sample rows from a table.

        Useful for verifying data format, checking values, or understanding
        what kind of data a column contains.

        Args:
            table: Qualified table name
            limit: Number of rows to fetch (default: 10, max: 100)
            columns: Optional list of columns to fetch (None = all columns)

        Returns:
            List of dictionaries representing rows

        Raises:
            TableNotFoundException: If table doesn't exist
            ColumnNotFoundException: If specified column doesn't exist

        Example:
            >>> # Get 5 sample rows from customers
            >>> rows = adapter.get_sample_data("customers", limit=5)
            >>> for row in rows:
            ...     print(row["email"])
            >>>
            >>> # Get specific columns only
            >>> rows = adapter.get_sample_data(
            ...     "customers",
            ...     columns=["email", "created_at"],
            ...     limit=10
            ... )
        """
        ...

    def get_table_count(self, schema: Optional[str] = None) -> int:
        """
        Get total number of tables in the catalog.

        Useful for understanding catalog size and deciding on search strategies.

        Args:
            schema: Optional schema name to limit count

        Returns:
            Number of tables

        Example:
            >>> # Total tables in database
            >>> total = adapter.get_table_count()
            >>> print(f"Database has {total} tables")
            >>>
            >>> # Tables in specific schema
            >>> public_tables = adapter.get_table_count(schema="public")
        """
        ...

    def get_schemas(self) -> List[str]:
        """
        List all available schemas/namespaces.

        Useful for understanding the catalog structure and limiting search scope.

        Returns:
            List of schema names

        Example:
            >>> schemas = adapter.get_schemas()
            >>> print(f"Available schemas: {schemas}")
        """
        ...

    def validate_table_exists(self, qualified_name: str) -> bool:
        """
        Check if a table exists without fetching full metadata.

        Faster than inspect_table when you only need existence check.

        Args:
            qualified_name: Fully qualified table name

        Returns:
            True if table exists, False otherwise

        Example:
            >>> if adapter.validate_table_exists("public.customers"):
            ...     print("Table exists")
        """
        ...

    def validate_column_exists(self, table: str, column: str) -> bool:
        """
        Check if a column exists in a table.

        Useful for validating assumptions before generating queries.

        Args:
            table: Qualified table name
            column: Column name

        Returns:
            True if column exists, False otherwise

        Example:
            >>> if adapter.validate_column_exists("customers", "email"):
            ...     print("Can safely use email column")
        """
        ...

    # Optional: Advanced features (can raise NotImplementedError)

    def get_table_statistics(self, table: str) -> Dict[str, Any]:
        """
        Get advanced statistics for a table (optional).

        May include cardinality estimates, null percentages, distribution stats.

        Args:
            table: Qualified table name

        Returns:
            Dictionary of statistics (format varies by system)

        Raises:
            AdapterNotImplementedError: If adapter doesn't support statistics

        Example:
            >>> stats = adapter.get_table_statistics("customers")
            >>> print(stats.get("null_percentage", {}))
        """
        ...

    def search_with_ranking(
        self,
        query: str,
        top_k: int = 10,
    ) -> List[SearchResult]:
        """
        Advanced search with relevance ranking (optional).

        Uses token scoring, fuzzy matching, or other ranking heuristics
        to order results by relevance.

        Args:
            query: Natural language query
            top_k: Number of top results to return

        Returns:
            List of SearchResult objects with match_score

        Raises:
            AdapterNotImplementedError: If adapter doesn't support ranking

        Example:
            >>> results = adapter.search_with_ranking(
            ...     "customer email address",
            ...     top_k=5
            ... )
            >>> for result in results:
            ...     print(f"{result.element.name}: {result.match_score}")
        """
        ...
