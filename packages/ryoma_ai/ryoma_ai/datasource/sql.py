import logging
from abc import abstractmethod
from typing import Any, Dict, List, Optional

from ibis import Table as IbisTable
from ibis.backends import CanListCatalog, CanListDatabase
from ibis.backends.sql import SQLBackend
from ryoma_ai.datasource.base import DataSource
from ryoma_ai.datasource.metadata import Catalog, Column, Schema, Table
from ryoma_ai.datasource.profiler import DatabaseProfiler


class SqlDataSource(DataSource):
    def __init__(
        self,
        database: Optional[str] = None,
        db_schema: Optional[str] = None,
        profiler_config: Optional[Dict] = None,
    ):
        super().__init__(type="sql")
        self.database = database
        self.db_schema = db_schema
        self.__connection = None

        # Initialize database profiler
        profiler_config = profiler_config or {}
        self.profiler = DatabaseProfiler(**profiler_config)

    def connect(self, **kwargs) -> Any:
        if not self.__connection:
            self.__connection = self._connect()
        logging.info("Database connection established")
        return self.__connection

    @abstractmethod
    def _connect(self, **kwargs) -> Any:
        raise NotImplementedError("connect is not implemented for this data source")

    def query(self, query, result_format="pandas", **kwargs) -> IbisTable:
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

    @abstractmethod
    def get_query_plan(self, query: str) -> Any:
        raise NotImplementedError(
            "get_query_plan is not implemented for this data source."
        )

    def prompt(self, schema: Optional[str] = None, table: Optional[str] = None):
        catalog = self.get_catalog(schema=schema)
        return catalog.prompt

    def profile_table(
        self, table_name: str, schema: Optional[str] = None, **kwargs
    ) -> Dict:
        """
        Profile a table with comprehensive metadata extraction.

        Args:
            table_name: Name of the table to profile
            schema: Optional schema name
            **kwargs: Additional profiling options

        Returns:
            Dictionary containing comprehensive table and column profiles
        """

        try:
            # Try Ibis-enhanced profiling first for better performance
            try:
                table_profile = self.profiler.profile_table_with_ibis(
                    self, table_name, schema
                )
                use_ibis_profiling = True
                logging.info(f"Using Ibis-enhanced profiling for table {table_name}")
            except Exception as e:
                logging.warning(
                    f"Ibis profiling failed, falling back to standard profiling: {e}"
                )
                table_profile = self.profiler.profile_table(self, table_name, schema)
                use_ibis_profiling = False

            # Get table schema to profile individual columns
            catalog = self.get_catalog(schema=schema, table=table_name)
            if not catalog.schemas:
                return {"table_profile": table_profile.model_dump()}

            table_obj = None
            for schema_obj in catalog.schemas:
                table_obj = schema_obj.get_table(table_name)
                if table_obj:
                    break

            if not table_obj:
                return {"table_profile": table_profile.model_dump()}

            # Profile each column using the appropriate method
            column_profiles = {}
            for column in table_obj.columns:
                if use_ibis_profiling:
                    column_profile = self.profiler.profile_column_with_ibis(
                        self, table_name, column.name, schema
                    )
                else:
                    column_profile = self.profiler.profile_column(
                        self, table_name, column.name, schema
                    )
                column_profiles[column.name] = column_profile.model_dump()

            return {
                "table_profile": table_profile.model_dump(),
                "column_profiles": column_profiles,
                "profiling_summary": {
                    "total_columns": len(column_profiles),
                    "profiled_at": (
                        table_profile.profiled_at.isoformat()
                        if table_profile.profiled_at
                        else None
                    ),
                    "row_count": table_profile.row_count,
                    "completeness_score": table_profile.completeness_score,
                    "profiling_method": (
                        "ibis_enhanced" if use_ibis_profiling else "standard"
                    ),
                },
            }

        except Exception as e:
            logging.error(f"Error profiling table {table_name}: {str(e)}")
            return {"error": str(e)}

    def profile_column(
        self, table_name: str, column_name: str, schema: Optional[str] = None
    ) -> Dict:
        """
        Profile a single column with detailed statistics.

        Args:
            table_name: Name of the table
            column_name: Name of the column
            schema: Optional schema name

        Returns:
            Dictionary containing column profile
        """

        try:
            # Try Ibis-enhanced profiling first
            try:
                column_profile = self.profiler.profile_column_with_ibis(
                    self, table_name, column_name, schema
                )
                logging.info(f"Using Ibis-enhanced profiling for column {column_name}")
            except Exception as e:
                logging.warning(f"Ibis column profiling failed, falling back: {e}")
                column_profile = self.profiler.profile_column(
                    self, table_name, column_name, schema
                )

            return column_profile.model_dump()
        except Exception as e:
            logging.error(f"Error profiling column {column_name}: {str(e)}")
            return {"error": str(e)}

    def get_enhanced_catalog(
        self,
        catalog: Optional[str] = None,
        schema: Optional[str] = None,
        table: Optional[str] = None,
        include_profiles: bool = True,
    ) -> Catalog:
        """
        Get catalog with enhanced profiling information.

        Args:
            catalog: Catalog name
            schema: Schema name
            table: Table name
            include_profiles: Whether to include profiling data

        Returns:
            Enhanced catalog with profiling information
        """
        # Get basic catalog
        basic_catalog = self.get_catalog(catalog, schema, table)

        if not include_profiles:
            return basic_catalog

        # Enhance with profiling data
        try:
            for schema_obj in basic_catalog.schemas or []:
                for table_obj in schema_obj.tables or []:
                    # Add table profile
                    if self.profiler:
                        table_profile = self.profiler.profile_table(
                            self, table_obj.table_name, schema_obj.schema_name
                        )
                        table_obj.profile = table_profile

                        # Add column profiles
                        for column in table_obj.columns:
                            column_profile = self.profiler.profile_column(
                                self,
                                table_obj.table_name,
                                column.name,
                                schema_obj.schema_name,
                            )
                            column.profile = column_profile

            return basic_catalog

        except Exception as e:
            logging.error(f"Error enhancing catalog with profiles: {str(e)}")
            return basic_catalog

    def find_similar_columns(
        self, reference_column: str, threshold: float = 0.8
    ) -> List[str]:
        """
        Find columns similar to the reference column using LSH.

        Args:
            reference_column: Name of the reference column
            threshold: Similarity threshold

        Returns:
            List of similar column names
        """

        return self.profiler.find_similar_columns(reference_column, threshold)
