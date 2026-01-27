"""
SQLite Open Catalog adapter - Reference implementation.

This adapter demonstrates how to implement the OpenCatalogAdapter protocol
for SQLite databases. It serves as a template for other adapters.
"""

import logging
from typing import Any, Dict, List, Literal, Optional

from ryoma_data.base import DataSource
from ryoma_ai.catalog.open_catalog.exceptions import (
    ColumnNotFoundException,
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


class SQLiteOpenCatalogAdapter:
    """
    Reference implementation of OpenCatalogAdapter for SQLite.

    This adapter uses SQLite's built-in metadata tables (sqlite_master,
    pragma_table_info, pragma_foreign_key_list) to implement deterministic
    metadata search without indexing.

    Example:
        >>> from ryoma_data.sql import SqlDataSource
        >>> datasource = SqlDataSource(uri="sqlite:///example.db")
        >>> adapter = SQLiteOpenCatalogAdapter(datasource)
        >>>
        >>> # Search for customer tables
        >>> tables = adapter.search_tables(pattern="*customer*")
        >>> for table in tables:
        ...     print(table.name, table.row_count)
    """

    def __init__(self, datasource: DataSource):
        """
        Initialize SQLite adapter.

        Args:
            datasource: DataSource instance for the SQLite database
        """
        self.datasource = datasource
        self._table_cache: Dict[str, TableMetadata] = {}
        logger.info("Initialized SQLiteOpenCatalogAdapter")

    def search_tables(
        self,
        pattern: Optional[str] = None,
        schema: Optional[str] = None,
        filters: Optional[SearchFilter] = None,
        limit: int = 100,
    ) -> List[TableMetadata]:
        """
        Search for tables in SQLite using sqlite_master.

        SQLite doesn't have schemas in the same way as other databases,
        so the schema parameter is ignored.
        """
        logger.debug(f"Searching tables: pattern={pattern}, filters={filters}")

        # Build base query
        query = """
            SELECT
                name,
                sql
            FROM sqlite_master
            WHERE type='table'
            AND name NOT LIKE 'sqlite_%'  -- Exclude system tables
        """

        conditions = []
        params = {}

        # Apply pattern filter
        if pattern:
            matcher = PatternMatcher(pattern)
            sql_pattern = matcher.to_sql_like()
            conditions.append("name LIKE :pattern")
            params["pattern"] = sql_pattern

        # Apply column existence filter
        if filters and filters.has_column:
            # Check if table has the specified column
            conditions.append(
                f"""
                EXISTS (
                    SELECT 1
                    FROM pragma_table_info(sqlite_master.name)
                    WHERE name = :column_name
                )
                """
            )
            params["column_name"] = filters.has_column

        # Add conditions to query
        if conditions:
            query += " AND " + " AND ".join(conditions)

        query += f" LIMIT {limit}"

        # Execute query
        try:
            results = self.datasource.query(query, params=params)
        except Exception as e:
            logger.error(f"Failed to search tables: {e}")
            return []

        # Convert results to TableMetadata
        tables = []
        for row in results:
            table_name = row["name"] if isinstance(row, dict) else row[0]

            # Get full metadata if not cached
            if table_name not in self._table_cache:
                try:
                    table_metadata = self._fetch_table_metadata(table_name)
                    self._table_cache[table_name] = table_metadata
                except Exception as e:
                    logger.warning(f"Failed to fetch metadata for {table_name}: {e}")
                    continue

            # Apply filters to cached metadata
            table_metadata = self._table_cache[table_name]

            if filters:
                if not self._apply_filters(table_metadata, filters):
                    continue

            tables.append(table_metadata)

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
        """Get complete metadata for a specific table."""
        logger.debug(f"Inspecting table: {qualified_name}")

        # Remove schema prefix if present (SQLite doesn't use schemas)
        table_name = qualified_name.split(".")[-1]

        if not self.validate_table_exists(table_name):
            raise TableNotFoundException(table_name)

        # Check cache first
        if table_name in self._table_cache and not include_sample_data:
            return self._table_cache[table_name]

        # Fetch metadata
        table_metadata = self._fetch_table_metadata(table_name, include_sample_data, sample_limit)
        self._table_cache[table_name] = table_metadata

        return table_metadata

    def get_relationships(
        self,
        table: str,
        direction: Literal["incoming", "outgoing", "both"] = "both",
    ) -> List[RelationshipMetadata]:
        """Get foreign key relationships for a table."""
        logger.debug(f"Getting relationships for {table}: direction={direction}")

        if not self.validate_table_exists(table):
            raise TableNotFoundException(table)

        relationships = []

        if direction in ["outgoing", "both"]:
            # Get outgoing foreign keys (this table references others)
            fk_query = f"PRAGMA foreign_key_list({table})"
            try:
                fk_results = self.datasource.query(fk_query)
                for fk_row in fk_results:
                    relationships.append(
                        RelationshipMetadata(
                            from_table=table,
                            to_table=fk_row["table"],
                            from_columns=[fk_row["from"]],
                            to_columns=[fk_row["to"]],
                            relationship_type="foreign_key",
                        )
                    )
            except Exception as e:
                logger.warning(f"Failed to get foreign keys for {table}: {e}")

        if direction in ["incoming", "both"]:
            # Get incoming foreign keys (other tables reference this table)
            # This requires scanning all tables
            all_tables = self.search_tables(limit=1000)
            for other_table in all_tables:
                if other_table.name == table:
                    continue

                try:
                    fk_query = f"PRAGMA foreign_key_list({other_table.name})"
                    fk_results = self.datasource.query(fk_query)
                    for fk_row in fk_results:
                        if fk_row["table"] == table:
                            relationships.append(
                                RelationshipMetadata(
                                    from_table=other_table.name,
                                    to_table=table,
                                    from_columns=[fk_row["from"]],
                                    to_columns=[fk_row["to"]],
                                    relationship_type="foreign_key",
                                )
                            )
                except Exception as e:
                    logger.warning(
                        f"Failed to check foreign keys in {other_table.name}: {e}"
                    )

        logger.debug(f"Found {len(relationships)} relationships")
        return relationships

    def get_sample_data(
        self,
        table: str,
        limit: int = 10,
        columns: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Get sample rows from a table."""
        logger.debug(f"Getting sample data from {table}: limit={limit}")

        if not self.validate_table_exists(table):
            raise TableNotFoundException(table)

        # Build column list
        if columns:
            # Validate columns exist
            table_metadata = self.inspect_table(table)
            available_columns = {col.name for col in table_metadata.columns}
            for col in columns:
                if col not in available_columns:
                    raise ColumnNotFoundException(
                        table, col, list(available_columns)
                    )
            column_list = ", ".join(columns)
        else:
            column_list = "*"

        # Fetch sample data
        query = f"SELECT {column_list} FROM {table} LIMIT {min(limit, 100)}"
        try:
            results = self.datasource.query(query)
            logger.debug(f"Retrieved {len(results)} sample rows")
            return results
        except Exception as e:
            logger.error(f"Failed to get sample data: {e}")
            return []

    def get_table_count(self, schema: Optional[str] = None) -> int:
        """Get total number of tables."""
        query = """
            SELECT COUNT(*)
            FROM sqlite_master
            WHERE type='table'
            AND name NOT LIKE 'sqlite_%'
        """
        try:
            result = self.datasource.query(query)
            count = result[0][0] if result else 0
            logger.debug(f"Total tables: {count}")
            return count
        except Exception as e:
            logger.error(f"Failed to get table count: {e}")
            return 0

    def get_schemas(self) -> List[str]:
        """
        List all schemas.

        SQLite doesn't have traditional schemas, so this returns ['main'].
        """
        return ["main"]

    def validate_table_exists(self, qualified_name: str) -> bool:
        """Check if a table exists."""
        table_name = qualified_name.split(".")[-1]

        query = """
            SELECT COUNT(*)
            FROM sqlite_master
            WHERE type='table'
            AND name = :table_name
        """
        try:
            result = self.datasource.query(query, params={"table_name": table_name})
            exists = result[0][0] > 0 if result else False
            return exists
        except Exception as e:
            logger.error(f"Failed to validate table existence: {e}")
            return False

    def validate_column_exists(self, table: str, column: str) -> bool:
        """Check if a column exists in a table."""
        if not self.validate_table_exists(table):
            return False

        query = f"PRAGMA table_info({table})"
        try:
            results = self.datasource.query(query)
            column_names = {row["name"] for row in results}
            return column in column_names
        except Exception as e:
            logger.error(f"Failed to validate column existence: {e}")
            return False

    # Helper methods

    def _fetch_table_metadata(
        self,
        table_name: str,
        include_sample_data: bool = False,
        sample_limit: int = 10,
    ) -> TableMetadata:
        """Fetch complete metadata for a table."""
        # Get column information
        columns_query = f"PRAGMA table_info({table_name})"
        column_results = self.datasource.query(columns_query)

        columns = []
        for col_row in column_results:
            # Get foreign keys for this column
            fk_query = f"PRAGMA foreign_key_list({table_name})"
            fk_results = self.datasource.query(fk_query)

            foreign_keys = []
            for fk_row in fk_results:
                if fk_row["from"] == col_row["name"]:
                    foreign_keys.append(
                        ForeignKeyRef(
                            referenced_table=fk_row["table"],
                            referenced_column=fk_row["to"],
                        )
                    )

            column_metadata = ColumnMetadata(
                name=col_row["name"],
                qualified_name=f"{table_name}.{col_row['name']}",
                table_name=table_name,
                data_type=col_row["type"] or "UNKNOWN",
                nullable=not col_row["notnull"],
                primary_key=bool(col_row["pk"]),
                foreign_keys=foreign_keys,
                default_value=col_row.get("dflt_value"),
            )
            columns.append(column_metadata)

        # Get row count
        try:
            count_query = f"SELECT COUNT(*) FROM {table_name}"
            count_result = self.datasource.query(count_query)
            row_count = count_result[0][0] if count_result else None
        except Exception:
            row_count = None

        # Get sample data if requested
        sample_data = None
        if include_sample_data:
            sample_data = self.get_sample_data(table_name, limit=sample_limit)

        # Create table metadata
        table_metadata = TableMetadata(
            name=table_name,
            qualified_name=table_name,
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
            if column.data_type.upper() != data_type.upper():
                return False

        return True
