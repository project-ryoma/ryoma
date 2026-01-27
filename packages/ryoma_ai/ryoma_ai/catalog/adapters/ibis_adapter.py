"""
Ibis-based Open Catalog adapter - Universal implementation.

This adapter leverages Ibis's unified interface to provide Open Catalog
functionality across ALL supported databases (PostgreSQL, MySQL, Snowflake,
BigQuery, DuckDB, SQLite, etc.) with a single implementation.

This is the recommended adapter for production use.
"""

import logging
from typing import Any, Dict, List, Literal, Optional

from ibis.backends import CanListCatalog, CanListDatabase
from ryoma_data.sql import DataSource as IbisDataSource
from ryoma_ai.catalog.open_catalog.exceptions import (
    ColumnNotFoundException,
    MetadataUnavailableError,
    TableNotFoundException,
)
from ryoma_ai.catalog.open_catalog.filters import PatternMatcher, SearchFilter
from ryoma_ai.catalog.open_catalog.models import (
    ColumnMetadata,
    ElementType,
    ForeignKeyRef,
    RelationshipMetadata,
    TableMetadata,
)

logger = logging.getLogger(__name__)


class IbisOpenCatalogAdapter:
    """
    Universal Open Catalog adapter using Ibis.

    This adapter works with ANY database supported by Ibis:
    - PostgreSQL
    - MySQL / MariaDB
    - Snowflake
    - BigQuery
    - DuckDB
    - SQLite
    - ClickHouse
    - And more...

    By leveraging Ibis's unified metadata interface, we get cross-database
    support with a single implementation.

    Example:
        >>> from ryoma_data.sql import DataSource
        >>> # Works with ANY Ibis backend
        >>> datasource = DataSource("postgres", host="localhost", database="mydb")
        >>> adapter = IbisOpenCatalogAdapter(datasource)
        >>>
        >>> # Or with Snowflake
        >>> datasource = DataSource("snowflake", account="myaccount", ...)
        >>> adapter = IbisOpenCatalogAdapter(datasource)
        >>>
        >>> # Same API for all databases
        >>> tables = adapter.search_tables(pattern="*customer*")
    """

    def __init__(self, datasource: IbisDataSource):
        """
        Initialize Ibis adapter.

        Args:
            datasource: IbisDataSource instance (works with any Ibis backend)
        """
        self.datasource = datasource
        self.connection = None
        self._table_cache: Dict[str, TableMetadata] = {}
        self._backend_type = datasource.backend

        logger.info(f"Initialized IbisOpenCatalogAdapter for {self._backend_type}")

    def _get_connection(self):
        """Get or create Ibis connection."""
        if not self.connection:
            self.connection = self.datasource.connect()
        return self.connection

    def search_tables(
        self,
        pattern: Optional[str] = None,
        schema: Optional[str] = None,
        filters: Optional[SearchFilter] = None,
        limit: int = 100,
    ) -> List[TableMetadata]:
        """
        Search for tables using Ibis's list_tables().

        This works across all Ibis backends uniformly.
        """
        logger.debug(
            f"Searching tables: pattern={pattern}, schema={schema}, filters={filters}"
        )

        conn = self._get_connection()

        # Get list of tables from Ibis
        try:
            # Ibis provides list_tables() for all backends
            if hasattr(conn, "list_tables"):
                if schema:
                    table_names = conn.list_tables(database=schema)
                else:
                    table_names = conn.list_tables()
            else:
                raise MetadataUnavailableError(
                    resource="tables",
                    reason=f"Backend '{self._backend_type}' doesn't support table listing",
                    recoverable=False,
                )
        except Exception as e:
            logger.error(f"Failed to list tables: {e}")
            raise MetadataUnavailableError(
                resource="tables",
                reason=str(e),
                recoverable=True,
            )

        # Apply pattern filter
        if pattern:
            matcher = PatternMatcher(pattern)
            table_names = [t for t in table_names if matcher.matches(t)]

        # Fetch metadata for each table (with caching)
        tables = []
        for table_name in table_names[:limit]:
            try:
                # Get full metadata
                table_metadata = self._fetch_table_metadata(table_name, schema)

                # Apply filters
                if filters:
                    if not self._apply_filters(table_metadata, filters):
                        continue

                tables.append(table_metadata)

            except Exception as e:
                logger.warning(f"Failed to fetch metadata for {table_name}: {e}")
                continue

        logger.debug(f"Found {len(tables)} tables")
        return tables

    def search_columns(
        self,
        pattern: Optional[str] = None,
        table: Optional[str] = None,
        data_type: Optional[str] = None,
        filters: Optional[SearchFilter] = None,
        limit: int = 100,
    ) -> List[ColumnMetadata]:
        """Search for columns across tables or within a specific table."""
        logger.debug(
            f"Searching columns: pattern={pattern}, table={table}, type={data_type}"
        )

        columns = []

        if table:
            # Search within specific table
            if not self.validate_table_exists(table):
                raise TableNotFoundException(table)

            table_metadata = self.inspect_table(table)
            for col in table_metadata.columns:
                if self._matches_column_search(col, pattern, data_type):
                    columns.append(col)
        else:
            # Search across all tables
            all_tables = self.search_tables(limit=1000)
            for table_metadata in all_tables:
                for col in table_metadata.columns:
                    if self._matches_column_search(col, pattern, data_type):
                        columns.append(col)
                        if len(columns) >= limit:
                            break
                if len(columns) >= limit:
                    break

        logger.debug(f"Found {len(columns)} columns")
        return columns[:limit]

    def inspect_table(
        self,
        qualified_name: str,
        include_sample_data: bool = False,
        sample_limit: int = 10,
    ) -> TableMetadata:
        """
        Get complete metadata for a specific table using Ibis's get_schema().

        Works uniformly across all Ibis backends.
        """
        logger.debug(f"Inspecting table: {qualified_name}")

        # Parse qualified name (handle schema.table)
        parts = qualified_name.split(".")
        if len(parts) == 2:
            schema, table_name = parts
        else:
            schema = None
            table_name = qualified_name

        if not self.validate_table_exists(qualified_name):
            raise TableNotFoundException(qualified_name)

        # Check cache
        cache_key = f"{schema}.{table_name}" if schema else table_name
        if cache_key in self._table_cache and not include_sample_data:
            return self._table_cache[cache_key]

        # Fetch metadata
        table_metadata = self._fetch_table_metadata(
            table_name, schema, include_sample_data, sample_limit
        )
        self._table_cache[cache_key] = table_metadata

        return table_metadata

    def get_relationships(
        self,
        table: str,
        direction: Literal["incoming", "outgoing", "both"] = "both",
    ) -> List[RelationshipMetadata]:
        """
        Get foreign key relationships for a table.

        Note: Ibis doesn't have a unified API for foreign keys across all backends,
        so this may not work for all databases. Falls back to empty list for
        unsupported backends.
        """
        logger.debug(f"Getting relationships for {table}: direction={direction}")

        if not self.validate_table_exists(table):
            raise TableNotFoundException(table)

        relationships = []

        # Try to get foreign keys (backend-specific)
        try:
            conn = self._get_connection()

            # Some backends support foreign key introspection
            # This is backend-specific, so we'll implement it when needed
            logger.warning(
                f"Foreign key introspection not yet implemented for {self._backend_type}"
            )

        except Exception as e:
            logger.warning(f"Failed to get relationships: {e}")

        return relationships

    def get_sample_data(
        self,
        table: str,
        limit: int = 10,
        columns: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Get sample rows using Ibis's table API."""
        logger.debug(f"Getting sample data from {table}: limit={limit}")

        if not self.validate_table_exists(table):
            raise TableNotFoundException(table)

        try:
            conn = self._get_connection()

            # Get table object from Ibis
            table_obj = conn.table(table)

            # Select columns if specified
            if columns:
                # Validate columns exist
                available_columns = table_obj.columns
                for col in columns:
                    if col not in available_columns:
                        raise ColumnNotFoundException(
                            table, col, list(available_columns)
                        )
                table_obj = table_obj.select(columns)

            # Limit and execute
            result = table_obj.limit(min(limit, 100)).execute()

            # Convert to list of dicts
            return result.to_dict("records")

        except Exception as e:
            logger.error(f"Failed to get sample data: {e}")
            return []

    def get_table_count(self, schema: Optional[str] = None) -> int:
        """Get total number of tables using Ibis's list_tables()."""
        try:
            conn = self._get_connection()

            if hasattr(conn, "list_tables"):
                if schema:
                    tables = conn.list_tables(database=schema)
                else:
                    tables = conn.list_tables()
                count = len(tables)
            else:
                count = 0

            logger.debug(f"Total tables: {count}")
            return count

        except Exception as e:
            logger.error(f"Failed to get table count: {e}")
            return 0

    def get_schemas(self) -> List[str]:
        """
        List all schemas/databases using Ibis's list_databases().

        Works for backends that support multiple schemas (Postgres, MySQL, etc.)
        """
        try:
            conn = self._get_connection()

            # Check if backend supports listing databases
            if isinstance(conn, (CanListDatabase, CanListCatalog)):
                if hasattr(conn, "list_databases"):
                    return list(conn.list_databases())
                elif hasattr(conn, "list_catalogs"):
                    return list(conn.list_catalogs())

            # Fallback: return current database/schema
            if self.datasource.database:
                return [self.datasource.database]

            return []

        except Exception as e:
            logger.error(f"Failed to list schemas: {e}")
            return []

    def validate_table_exists(self, qualified_name: str) -> bool:
        """Check if a table exists using Ibis's list_tables()."""
        try:
            # Parse qualified name
            parts = qualified_name.split(".")
            if len(parts) == 2:
                schema, table_name = parts
            else:
                schema = None
                table_name = qualified_name

            conn = self._get_connection()

            if hasattr(conn, "list_tables"):
                if schema:
                    tables = conn.list_tables(database=schema)
                else:
                    tables = conn.list_tables()
                return table_name in tables

            # Fallback: try to get schema
            try:
                conn.get_schema(table_name, database=schema)
                return True
            except Exception:
                return False

        except Exception as e:
            logger.error(f"Failed to validate table existence: {e}")
            return False

    def validate_column_exists(self, table: str, column: str) -> bool:
        """Check if a column exists using Ibis's get_schema()."""
        try:
            # Parse table name
            parts = table.split(".")
            if len(parts) == 2:
                schema, table_name = parts
            else:
                schema = None
                table_name = table

            conn = self._get_connection()
            table_schema = conn.get_schema(table_name, database=schema)

            return column in table_schema.names

        except Exception as e:
            logger.error(f"Failed to validate column existence: {e}")
            return False

    # Helper methods

    def _fetch_table_metadata(
        self,
        table_name: str,
        schema: Optional[str] = None,
        include_sample_data: bool = False,
        sample_limit: int = 10,
    ) -> TableMetadata:
        """Fetch complete metadata for a table using Ibis."""
        conn = self._get_connection()

        # Get table schema from Ibis
        try:
            table_schema = conn.get_schema(table_name, database=schema)
        except Exception as e:
            raise MetadataUnavailableError(
                resource=table_name,
                reason=f"Failed to get schema: {str(e)}",
                recoverable=True,
            )

        # Convert Ibis schema to ColumnMetadata
        columns = []
        for col_name, col_type in table_schema.items():
            column_metadata = ColumnMetadata(
                name=col_name,
                qualified_name=f"{table_name}.{col_name}",
                table_name=table_name,
                data_type=str(col_type),
                nullable=col_type.nullable,
                primary_key=False,  # Ibis doesn't expose PK info uniformly
                foreign_keys=[],  # Would need backend-specific logic
            )
            columns.append(column_metadata)

        # Try to get row count (may not work for all backends)
        row_count = None
        try:
            table_obj = conn.table(table_name)
            row_count = table_obj.count().execute()
        except Exception as e:
            logger.debug(f"Could not get row count for {table_name}: {e}")

        # Get sample data if requested
        sample_data = None
        if include_sample_data:
            try:
                sample_data = self.get_sample_data(table_name, limit=sample_limit)
            except Exception as e:
                logger.warning(f"Could not get sample data: {e}")

        # Create qualified name
        qualified_name = f"{schema}.{table_name}" if schema else table_name

        # Create table metadata
        table_metadata = TableMetadata(
            name=table_name,
            qualified_name=qualified_name,
            schema_name=schema,
            columns=columns,
            row_count=row_count,
            table_type=ElementType.TABLE,
        )

        if sample_data:
            table_metadata.properties["sample_data"] = sample_data

        return table_metadata

    def _apply_filters(
        self,
        table: TableMetadata,
        filters: SearchFilter,
    ) -> bool:
        """Check if a table matches the given filters."""
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

        # Type filters
        if filters.has_primary_key is not None:
            has_pk = any(col.primary_key for col in table.columns)
            if has_pk != filters.has_primary_key:
                return False

        if filters.has_foreign_keys is not None:
            has_fk = any(col.foreign_keys for col in table.columns)
            if has_fk != filters.has_foreign_keys:
                return False

        # Size filters
        if filters.row_count_min is not None:
            if table.row_count is None or table.row_count < filters.row_count_min:
                return False

        if filters.row_count_max is not None:
            if table.row_count is None or table.row_count > filters.row_count_max:
                return False

        return True

    def _matches_column_search(
        self,
        column: ColumnMetadata,
        pattern: Optional[str],
        data_type: Optional[str],
    ) -> bool:
        """Check if a column matches search criteria."""
        if pattern:
            matcher = PatternMatcher(pattern)
            if not matcher.matches(column.name):
                return False

        if data_type:
            if data_type.lower() not in column.data_type.lower():
                return False

        return True
