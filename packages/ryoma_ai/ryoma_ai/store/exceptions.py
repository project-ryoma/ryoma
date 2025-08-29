"""
Exception classes for store operations.
"""

from typing import Optional


class StoreException(Exception):
    """Base exception for all store-related errors."""

    def __init__(self, message: str, cause: Optional[Exception] = None):
        super().__init__(message)
        self.cause = cause


class DataSourceNotFoundError(StoreException):
    """Raised when a requested data source is not found in the store."""

    def __init__(self, data_source_id: str, cause: Optional[Exception] = None):
        message = f"Data source with ID '{data_source_id}' not found"
        super().__init__(message, cause)
        self.data_source_id = data_source_id


class CatalogNotFoundError(StoreException):
    """Raised when a requested catalog is not found in the store."""

    def __init__(
        self,
        catalog_id: str,
        data_source_id: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        if data_source_id:
            message = (
                f"Catalog '{catalog_id}' not found for data source '{data_source_id}'"
            )
        else:
            message = f"Catalog '{catalog_id}' not found"
        super().__init__(message, cause)
        self.catalog_id = catalog_id
        self.data_source_id = data_source_id


class DataSourceConnectionError(StoreException):
    """Raised when data source connection fails."""

    def __init__(
        self,
        data_source_id: str,
        connection_error: str,
        cause: Optional[Exception] = None,
    ):
        message = (
            f"Failed to connect to data source '{data_source_id}': {connection_error}"
        )
        super().__init__(message, cause)
        self.data_source_id = data_source_id
        self.connection_error = connection_error
