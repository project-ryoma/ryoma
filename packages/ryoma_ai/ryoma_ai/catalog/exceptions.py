"""
Exception classes for catalog operations.
"""

from typing import Optional


class CatalogIndexError(Exception):
    """Raised when catalog indexing operations fail."""

    def __init__(
        self, operation: str, catalog_id: str, cause: Optional[Exception] = None
    ):
        message = f"Failed to {operation} catalog '{catalog_id}'"
        super().__init__(message)
        self.operation = operation
        self.catalog_id = catalog_id
        self.cause = cause
