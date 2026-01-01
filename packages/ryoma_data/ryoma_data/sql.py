import logging
from typing import Any, ClassVar, Dict, List, Optional

import ibis
from ibis import Table as IbisTable
from ibis.backends import CanListCatalog, CanListDatabase
from ibis.backends.sql import SQLBackend
from ryoma_data.base import BaseDataSource
from ryoma_data.metadata import Catalog, Column, Schema, Table


class DataSource(BaseDataSource):
    """
    Unified SQL datasource that uses Ibis backends directly.
    Supports all Ibis-compatible databases through a single interface.

    This class eliminates code duplication by leveraging Ibis's unified API
    across different database backends (PostgreSQL, MySQL, Snowflake, BigQuery, etc.).

    Example:
        # PostgreSQL
        ds = DataSource("postgres", host="localhost", port=5432, database="mydb")

        # MySQL
        ds = DataSource("mysql", user="root", host="localhost", database="mydb")

        # Or with connection URL
        ds = DataSource("postgres", connection_url="postgresql://localhost/mydb")
    """

    BACKEND_MAPPING: ClassVar[Dict[str, str]] = {
        "postgres": "postgres",
        "postgresql": "postgres",
        "mysql": "mysql",
        "snowflake": "snowflake",
        "bigquery": "bigquery",
        "duckdb": "duckdb",
        "sqlite": "sqlite",
    }

    def __init__(
        self,
        backend: str,
        connection_url: Optional[str] = None,
        **connection_params
    ):
        """
        Initialize Ibis datasource.

        Args:
            backend: Backend type ("postgres", "mysql", "snowflake", etc.)
            connection_url: Optional connection URL (e.g., "postgresql://localhost/db")
            **connection_params: Backend-specific connection parameters like:
                - host, port, database, user, password (PostgreSQL, MySQL)
                - account, user, password, database (Snowflake)
                - project_id, dataset_id (BigQuery)
                - path (DuckDB, SQLite)
        """
        database = connection_params.get("database")
        db_schema = connection_params.get("schema") or connection_params.get("db_schema")

        super().__init__(type="sql")

        self.backend = self._normalize_backend(backend)
        self.connection_url = connection_url
        self.connection_params = connection_params
        self.database = database
        self.db_schema = db_schema
        self.__connection = None

        # Store common parameters for convenience
        self.host = connection_params.get("host")
        self.port = connection_params.get("port")
        self.user = connection_params.get("user") or connection_params.get("username")
        self.password = connection_params.get("password")

    def _normalize_backend(self, backend: str) -> str:
        """Normalize backend name (e.g., 'postgresql' -> 'postgres')."""
        backend_lower = backend.lower()
        normalized = self.BACKEND_MAPPING.get(backend_lower, backend_lower)
        logging.debug(f"Normalized backend '{backend}' to '{normalized}'")
        return normalized

    def connect(self, **kwargs) -> Any:
        """Get or create database connection."""
        if not self.__connection:
            self.__connection = self._connect(**kwargs)
        logging.info("Database connection established")
        return self.__connection

    def _connect(self, **kwargs):
        """Connect using Ibis's unified interface."""
        logging.info(f"Connecting to {self.backend} database: {self.database}")

        try:
            # Prefer connection URL if provided
            if self.connection_url:
                logging.debug(f"Using connection URL for {self.backend}")
                return ibis.connect(self.connection_url, **kwargs)

            # Use backend-specific connect method
            backend_module = getattr(ibis, self.backend, None)
            if not backend_module:
                raise ValueError(
                    f"Unsupported Ibis backend: {self.backend}. "
                    f"Available backends: {list(self.BACKEND_MAPPING.keys())}"
                )

            connect_func = getattr(backend_module, "connect", None)
            if not connect_func:
                raise AttributeError(
                    f"Backend '{self.backend}' does not have a connect method"
                )

            # Merge connection_params with any additional kwargs
            merged_params = {**self.connection_params, **kwargs}
            logging.debug(f"Connecting to {self.backend} with params: {list(merged_params.keys())}")

            return connect_func(**merged_params)

        except ImportError as e:
            self._handle_connection_error(e, self.backend)
        except Exception as e:
            raise ConnectionError(
                f"Failed to connect to {self.backend}: {str(e)}"
            ) from e

    def _handle_connection_error(self, error: Exception, datasource_type: str):
        """Helper method to handle connection errors and provide better error messages."""
        error_msg = str(error)
        # Check if it's an ibis backend import error
        if (
            "Failed to import the" in error_msg
            and "backend due to missing dependencies" in error_msg
        ):
            # Escape square brackets to prevent Rich console from interpreting them as markup
            raise ImportError(
                f"Missing dependencies for {datasource_type}. "
                f'Please install with: pip install "ryoma_ai\\[{datasource_type}]"'
            ) from error
        else:
            # Re-raise the original error for non-import errors
            raise

    def query(self, query, result_format="pandas", **kwargs) -> IbisTable:
        """Execute SQL query and return results."""
        logging.info(f"Executing query: {query}")
        conn = self.connect()
        if not isinstance(conn, SQLBackend):
            raise Exception("Ibis connection is not a SQLBackend")
        result = conn.sql(query)
        if result_format == "arrow":
            result = result.to_pyarrow()
        elif result_format == "polars":
            result = result.to_polars()
        else:
            result = result.to_pandas()
        return result

    def get_catalog(
        self,
        catalog: Optional[str] = None,
        schema: Optional[str] = None,
        table: Optional[str] = None,
    ) -> Catalog:
        """Get catalog metadata for databases, schemas, and tables."""
        catalog = self.database if not catalog else catalog
        if table:
            schema = self.db_schema if not schema else schema
            conn = self.connect()
            table_schema = conn.get_schema(name=table, catalog=catalog, database=schema)
            table = Table(
                table_name=table,
                columns=self._build_columns_from_schema(table_schema),
            )
            databases = Schema(schema_name=schema, tables=[table])
        elif schema:
            tables = self.list_tables(catalog, schema, with_columns=True)
            databases = Schema(schema_name=schema, tables=tables)
        else:
            databases = self.list_databases(
                catalog=catalog, with_table=True, with_columns=True
            )
        return Catalog(
            catalog_name=catalog,
            schemas=databases,
        )

    def _build_columns_from_schema(self, table_schema: Dict[str, Any]) -> List[Column]:
        """
        Helper method to build a list of Column objects from a table schema.

        Args:
            table_schema: Dictionary representing the table schema.

        Returns:
            List of Column objects.
        """
        columns = []
        for name, col in table_schema.items():
            column_type = col.name if hasattr(col, "name") else str(col)
            nullable = col.nullable if hasattr(col, "nullable") else True
            columns.append(Column(name=name, type=column_type, nullable=nullable))
        return columns

    def _is_system_table(
        self, table_name: str, schema_name: Optional[str] = None
    ) -> bool:
        """
        Check if a table is a system table that should be filtered out.

        Args:
            table_name: Name of the table
            schema_name: Optional schema name

        Returns:
            True if the table is a system table, False otherwise
        """
        # PostgreSQL system tables
        pg_system_prefixes = ["pg_", "information_schema"]
        pg_system_schemas = ["information_schema", "pg_catalog", "pg_toast"]

        # MySQL system tables
        mysql_system_schemas = [
            "information_schema",
            "performance_schema",
            "mysql",
            "sys",
        ]

        # SQLite system tables
        sqlite_system_prefixes = ["sqlite_"]

        # SQL Server system tables
        sqlserver_system_schemas = ["sys", "INFORMATION_SCHEMA"]

        # Check schema-based filtering
        if schema_name:
            if (
                schema_name.lower()
                in pg_system_schemas + mysql_system_schemas + sqlserver_system_schemas
            ):
                return True

        # Check table name prefixes
        table_lower = table_name.lower()
        system_prefixes = pg_system_prefixes + sqlite_system_prefixes

        for prefix in system_prefixes:
            if table_lower.startswith(prefix):
                return True

        return False

    def list_catalogs(
        self,
        like: Optional[str] = None,
        with_schema: bool = False,
        with_table: bool = False,
        with_columns: bool = False,
    ) -> list[Catalog]:
        """List all catalogs in the database."""
        conn: CanListCatalog = self.connect()
        if not hasattr(conn, "list_catalogs"):
            raise Exception("This data source does not support listing catalogs")
        catalogs = [
            Catalog(catalog_name=catalog) for catalog in conn.list_catalogs(like=like)
        ]
        if with_schema:
            for catalog in catalogs:
                catalog.schemas = self.list_databases(catalog=catalog.catalog_name)
        if with_table:
            for catalog in catalogs:
                for schema in catalog.schemas:
                    schema.tables = self.list_tables(
                        catalog=catalog.catalog_name,
                        database=schema.schema_name,
                        with_columns=with_columns,
                    )
        return catalogs

    def list_databases(
        self,
        catalog: Optional[str] = None,
        with_table: bool = False,
        with_columns: bool = False,
        include_system_schemas: bool = False,
    ) -> list[Schema]:
        """List all databases/schemas in the catalog."""
        conn: CanListDatabase = self.connect()
        if not hasattr(conn, "list_databases"):
            raise Exception("This data source does not support listing databases")
        catalog = catalog or self.database or getattr(conn, "current_catalog", None)

        all_schemas = conn.list_databases(catalog=catalog)

        # Filter out system schemas unless explicitly requested
        if not include_system_schemas:
            # Filter based on schema name patterns
            pg_system_schemas = ["information_schema", "pg_catalog", "pg_toast"]
            mysql_system_schemas = [
                "information_schema",
                "performance_schema",
                "mysql",
                "sys",
            ]
            sqlserver_system_schemas = ["sys", "INFORMATION_SCHEMA"]
            system_schemas = (
                pg_system_schemas + mysql_system_schemas + sqlserver_system_schemas
            )

            all_schemas = [
                schema
                for schema in all_schemas
                if schema.lower() not in [s.lower() for s in system_schemas]
            ]

        databases = [Schema(schema_name=schema) for schema in all_schemas]
        if with_table:
            for schema in databases:
                schema.tables = self.list_tables(
                    catalog=catalog,
                    database=schema.schema_name,
                    with_columns=with_columns,
                )
        return databases

    def list_tables(
        self,
        catalog: Optional[str] = None,
        database: Optional[str] = None,
        with_columns: bool = False,
        include_system_tables: bool = False,
    ) -> list[Table]:
        """List all tables in the database/schema."""
        conn = self.connect()
        catalog = catalog or self.database or conn.current_database
        if database is not None:
            catalog = (catalog, database)

        all_tables = conn.list_tables(database=catalog)

        # Filter out system tables unless explicitly requested
        if not include_system_tables:
            all_tables = [
                table
                for table in all_tables
                if not self._is_system_table(table, database)
            ]

        tables = [Table(table_name=table, columns=[]) for table in all_tables]

        if with_columns:
            for table in tables:
                try:
                    table_schema = conn.get_schema(
                        name=table.table_name, catalog=catalog, database=database
                    )
                except Exception as e:
                    logging.error(
                        f"Error getting schema for table {table.table_name}: {e}"
                    )
                    continue
                table.columns = self._build_columns_from_schema(
                    table_schema=table_schema
                )
        return tables

    def get_query_plan(self, query: str) -> Any:
        """
        Get query execution plan using backend-specific EXPLAIN syntax.

        Args:
            query: SQL query to explain

        Returns:
            Query plan (format depends on backend)
        """
        # Backend-specific EXPLAIN templates
        explain_templates = {
            "postgres": "EXPLAIN {}",
            "mysql": "EXPLAIN FORMAT=JSON {}",
            "snowflake": "EXPLAIN USING JSON {}",
            "bigquery": "EXPLAIN {}",
            "duckdb": "EXPLAIN {}",
        }

        template = explain_templates.get(self.backend)
        if not template:
            logging.warning(
                f"Query plan not supported for {self.backend}, returning None"
            )
            return None

        conn = self.connect()
        explain_query = template.format(query)
        logging.debug(f"Getting query plan with: {explain_query}")

        return conn.sql(explain_query)
