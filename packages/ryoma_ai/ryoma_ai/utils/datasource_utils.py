"""
DataSource Utilities

Provides type guards and utilities for working with different datasource types,
allowing ryoma_ai to work with the base DataSource interface while supporting
SQL-specific features when available.
"""

from typing import TypeGuard

from ryoma_data.base import BaseDataSource
from ryoma_data.sql import DataSource as SqlDataSource


def is_sql_datasource(datasource: BaseDataSource) -> TypeGuard[SqlDataSource]:
    """
    Type guard to check if a datasource is a SQL datasource.

    Args:
        datasource: The datasource to check

    Returns:
        True if the datasource is a SQL datasource, False otherwise
    """
    return isinstance(datasource, SqlDataSource)


def ensure_sql_datasource(datasource: BaseDataSource) -> SqlDataSource:
    """
    Runtime check to ensure a datasource is a SQL datasource.

    Args:
        datasource: The datasource to check

    Returns:
        The datasource cast to SqlDataSource

    Raises:
        TypeError: If the datasource is not a SQL datasource
    """
    if not is_sql_datasource(datasource):
        raise TypeError(
            f"Expected SQL datasource, got {type(datasource).__name__}. "
            f"This operation requires a SQL datasource."
        )
    return datasource


def get_datasource_capabilities(datasource: BaseDataSource) -> dict:
    """
    Detect and return the capabilities of a datasource.

    Args:
        datasource: The datasource to inspect

    Returns:
        Dictionary with capability flags:
            - is_sql: Whether this is a SQL datasource
            - supports_schemas: Whether schemas are supported
            - datasource_type: String name of the datasource type
    """
    capabilities = {
        "is_sql": is_sql_datasource(datasource),
        "datasource_type": type(datasource).__name__,
    }

    # Check for SQL-specific capabilities
    if is_sql_datasource(datasource):
        capabilities["supports_schemas"] = True
        capabilities["supports_queries"] = True
        capabilities["supports_profiling"] = True
    else:
        capabilities["supports_schemas"] = hasattr(datasource, "get_catalog")
        capabilities["supports_queries"] = False
        capabilities["supports_profiling"] = hasattr(datasource, "profile_table")

    return capabilities
