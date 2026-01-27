"""
Ibis-based Open Catalog adapter - Simplified universal implementation.

This adapter leverages Ibis's unified interface to provide Open Catalog
functionality across ALL supported databases with minimal code.
"""

import logging
from typing import Any, Dict, List, Literal, Optional

from ryoma_data.sql import DataSource as IbisDataSource
from ryoma_ai.catalog.open_catalog.exceptions import (
    ColumnNotFoundException,
    TableNotFoundException,
)
from ryoma_ai.catalog.open_catalog.filters import PatternMatcher, SearchFilter
from ryoma_ai.catalog.open_catalog.models import (
    ColumnMetadata,
    ElementType,
    RelationshipMetadata,
    TableMetadata,
)

logger = logging.getLogger(__name__)


class IbisOpenCatalogAdapter:
    """
    Universal Open Catalog adapter using Ibis.

    Works with ANY Ibis-supported database: PostgreSQL, MySQL, Snowflake,
    BigQuery, DuckDB, SQLite, ClickHouse, and more.

    Example:
        >>> from ryoma_data.sql import DataSource
        >>> datasource = DataSource("postgres", host="localhost", database="mydb")
        >>> adapter = IbisOpenCatalogAdapter(datasource)
        >>> tables = adapter.search_tables(pattern="*customer*")
    """

    def __init__(self, datasource: IbisDataSource):
        """Initialize adapter with Ibis datasource."""
        self.datasource = datasource
        self._conn = None

    @property
    def conn(self):
        """Lazy connection to database."""
        if self._conn is None:
            self._conn = self.datasource.connect()
        return self._conn

    def search_tables(
        self,
        pattern: Optional[str] = None,
        schema: Optional[str] = None,
        filters: Optional[SearchFilter] = None,
        limit: int = 100,
    ) -> List[TableMetadata]:
        """Search tables using Ibis's list_tables()."""
        # Get all table names
        table_names = self.conn.list_tables(database=schema) if schema else self.conn.list_tables()

        # Apply pattern matching
        if pattern:
            matcher = PatternMatcher(pattern)
            table_names = [t for t in table_names if matcher.matches(t)]

        # Fetch and filter metadata
        tables = []
        for table_name in table_names[:limit]:
            try:
                table_meta = self._build_table_metadata(table_name, schema)

                # Apply filters
                if filters and not self._matches_filters(table_meta, filters):
                    continue

                tables.append(table_meta)
            except Exception as e:
                logger.debug(f"Skipping {table_name}: {e}")

        return tables

    def search_columns(
        self,
        pattern: Optional[str] = None,
        table: Optional[str] = None,
        data_type: Optional[str] = None,
        filters: Optional[SearchFilter] = None,
        limit: int = 100,
    ) -> List[ColumnMetadata]:
        """Search columns across tables."""
        columns = []

        if table:
            # Search within specific table
            table_meta = self.inspect_table(table)
            columns = [
                col for col in table_meta.columns
                if self._matches_column(col, pattern, data_type)
            ]
        else:
            # Search across all tables
            for table_meta in self.search_tables(limit=1000):
                for col in table_meta.columns:
                    if self._matches_column(col, pattern, data_type):
                        columns.append(col)
                        if len(columns) >= limit:
                            return columns

        return columns[:limit]

    def inspect_table(
        self,
        qualified_name: str,
        include_sample_data: bool = False,
        sample_limit: int = 10,
    ) -> TableMetadata:
        """Get complete metadata for a table."""
        schema, table_name = self._parse_qualified_name(qualified_name)

        if not self.validate_table_exists(qualified_name):
            raise TableNotFoundException(qualified_name)

        table_meta = self._build_table_metadata(
            table_name, schema, include_sample_data, sample_limit
        )
        return table_meta

    def get_relationships(
        self,
        table: str,
        direction: Literal["incoming", "outgoing", "both"] = "both",
    ) -> List[RelationshipMetadata]:
        """
        Get foreign key relationships.

        Note: Ibis doesn't have unified FK introspection, so this returns
        empty for now. Backend-specific implementations can override.
        """
        logger.debug(f"FK relationships not yet implemented for Ibis adapter")
        return []

    def get_sample_data(
        self,
        table: str,
        limit: int = 10,
        columns: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Get sample rows from table."""
        schema, table_name = self._parse_qualified_name(table)

        # Get Ibis table object
        table_obj = self.conn.table(table_name, database=schema)

        # Select specific columns if requested
        if columns:
            table_obj = table_obj.select(columns)

        # Execute and convert to records
        result = table_obj.limit(min(limit, 100)).execute()
        return result.to_dict("records")

    def get_table_count(self, schema: Optional[str] = None) -> int:
        """Get total number of tables."""
        tables = self.conn.list_tables(database=schema) if schema else self.conn.list_tables()
        return len(tables)

    def get_schemas(self) -> List[str]:
        """List all schemas/databases."""
        try:
            if hasattr(self.conn, "list_databases"):
                return list(self.conn.list_databases())
        except Exception:
            pass

        # Fallback to current database
        return [self.datasource.database] if self.datasource.database else []

    def validate_table_exists(self, qualified_name: str) -> bool:
        """Check if table exists."""
        schema, table_name = self._parse_qualified_name(qualified_name)

        try:
            tables = self.conn.list_tables(database=schema) if schema else self.conn.list_tables()
            return table_name in tables
        except Exception:
            return False

    def validate_column_exists(self, table: str, column: str) -> bool:
        """Check if column exists in table."""
        schema, table_name = self._parse_qualified_name(table)

        try:
            table_schema = self.conn.get_schema(table_name, database=schema)
            return column in table_schema.names
        except Exception:
            return False

    # ========================================
    # Helper Methods
    # ========================================

    def _build_table_metadata(
        self,
        table_name: str,
        schema: Optional[str] = None,
        include_sample_data: bool = False,
        sample_limit: int = 10,
    ) -> TableMetadata:
        """Build TableMetadata from Ibis schema."""
        # Get schema from Ibis
        table_schema = self.conn.get_schema(table_name, database=schema)

        # Convert to ColumnMetadata
        columns = [
            ColumnMetadata(
                name=col_name,
                qualified_name=f"{table_name}.{col_name}",
                table_name=table_name,
                data_type=str(col_type),
                nullable=col_type.nullable,
                primary_key=False,  # Not available in Ibis
                foreign_keys=[],     # Not available in Ibis
            )
            for col_name, col_type in table_schema.items()
        ]

        # Get row count (best effort)
        row_count = None
        try:
            table_obj = self.conn.table(table_name, database=schema)
            row_count = table_obj.count().execute()
        except Exception:
            pass

        # Build qualified name
        qualified_name = f"{schema}.{table_name}" if schema else table_name

        # Create table metadata
        table_meta = TableMetadata(
            name=table_name,
            qualified_name=qualified_name,
            schema_name=schema,
            columns=columns,
            row_count=row_count,
            table_type=ElementType.TABLE,
        )

        # Add sample data if requested
        if include_sample_data:
            try:
                sample_data = self.get_sample_data(qualified_name, limit=sample_limit)
                table_meta.properties["sample_data"] = sample_data
            except Exception as e:
                logger.debug(f"Could not get sample data: {e}")

        return table_meta

    def _matches_filters(self, table: TableMetadata, filters: SearchFilter) -> bool:
        """Check if table matches SearchFilter criteria."""
        # Column filters
        if filters.has_column:
            if not any(col.name == filters.has_column for col in table.columns):
                return False

        if filters.has_columns:
            table_columns = {col.name for col in table.columns}
            if not all(col in table_columns for col in filters.has_columns):
                return False

        if filters.has_any_columns:
            table_columns = {col.name for col in table.columns}
            if not any(col in table_columns for col in filters.has_any_columns):
                return False

        # Size filters
        if filters.row_count_min and (table.row_count is None or table.row_count < filters.row_count_min):
            return False

        if filters.row_count_max and (table.row_count is None or table.row_count > filters.row_count_max):
            return False

        return True

    def _matches_column(
        self, col: ColumnMetadata, pattern: Optional[str], data_type: Optional[str]
    ) -> bool:
        """Check if column matches search criteria."""
        if pattern:
            matcher = PatternMatcher(pattern)
            if not matcher.matches(col.name):
                return False

        if data_type and data_type.lower() not in col.data_type.lower():
            return False

        return True

    def _parse_qualified_name(self, qualified_name: str) -> tuple[Optional[str], str]:
        """Parse 'schema.table' or 'table' into (schema, table)."""
        parts = qualified_name.split(".")
        if len(parts) == 2:
            return parts[0], parts[1]
        return None, qualified_name
