"""
Exceptions for Open Catalog operations.

Provides clear, actionable error messages for metadata search failures.
"""

from typing import List, Optional


class OpenCatalogError(Exception):
    """Base exception for all Open Catalog operations."""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        """Format error message with details."""
        if not self.details:
            return self.message

        details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
        return f"{self.message} ({details_str})"


class TableNotFoundException(OpenCatalogError):
    """
    Raised when a table doesn't exist in the catalog.

    Includes fuzzy match suggestions to help users find what they're looking for.
    """

    def __init__(
        self,
        table_name: str,
        suggested_tables: Optional[List[str]] = None,
        schema: Optional[str] = None,
    ):
        self.table_name = table_name
        self.suggested_tables = suggested_tables or []
        self.schema = schema

        message = f"Table '{table_name}' not found"
        if schema:
            message += f" in schema '{schema}'"

        if self.suggested_tables:
            suggestions = ", ".join(self.suggested_tables[:5])
            message += f"\n\nDid you mean one of these?\n  - {suggestions}"

        details = {
            "table_name": table_name,
            "schema": schema,
            "suggestions_count": len(self.suggested_tables),
        }

        super().__init__(message, details)


class ColumnNotFoundException(OpenCatalogError):
    """
    Raised when a column doesn't exist in a table.

    Includes list of available columns to help users correct their query.
    """

    def __init__(
        self,
        table_name: str,
        column_name: str,
        available_columns: Optional[List[str]] = None,
    ):
        self.table_name = table_name
        self.column_name = column_name
        self.available_columns = available_columns or []

        message = f"Column '{column_name}' not found in table '{table_name}'"

        if self.available_columns:
            columns = ", ".join(self.available_columns)
            message += f"\n\nAvailable columns:\n  {columns}"

        details = {
            "table_name": table_name,
            "column_name": column_name,
            "available_columns_count": len(self.available_columns),
        }

        super().__init__(message, details)


class SearchTimeoutError(OpenCatalogError):
    """
    Raised when a search operation exceeds the timeout threshold.

    Suggests ways to narrow the search scope.
    """

    def __init__(self, query: str, timeout_ms: int, hint: Optional[str] = None):
        self.query = query
        self.timeout_ms = timeout_ms

        message = f"Search timed out after {timeout_ms}ms for query: {query}"

        if hint:
            message += f"\n\nHint: {hint}"
        else:
            message += "\n\nTry:\n"
            message += "  - Adding more specific filters\n"
            message += "  - Narrowing the search pattern\n"
            message += "  - Limiting the search to a specific schema"

        details = {"query": query, "timeout_ms": timeout_ms}

        super().__init__(message, details)


class InvalidPatternError(OpenCatalogError):
    """
    Raised when a search pattern is malformed or invalid.

    Provides guidance on valid pattern syntax.
    """

    def __init__(self, pattern: str, reason: str):
        self.pattern = pattern
        self.reason = reason

        message = f"Invalid search pattern: {pattern}\n"
        message += f"Reason: {reason}\n\n"
        message += "Valid patterns:\n"
        message += "  - '*customer*' (contains 'customer')\n"
        message += "  - 'dim_*' (starts with 'dim_')\n"
        message += "  - '*_daily' (ends with '_daily')\n"
        message += "  - 'fact_?_summary' (single character wildcard)"

        details = {"pattern": pattern, "reason": reason}

        super().__init__(message, details)


class AdapterNotImplementedError(OpenCatalogError):
    """
    Raised when an adapter doesn't implement a required operation.

    Indicates which operations are supported by the current adapter.
    """

    def __init__(
        self,
        operation: str,
        adapter_name: str,
        supported_operations: Optional[List[str]] = None,
    ):
        self.operation = operation
        self.adapter_name = adapter_name
        self.supported_operations = supported_operations or []

        message = f"Operation '{operation}' not implemented by {adapter_name} adapter"

        if self.supported_operations:
            operations = ", ".join(self.supported_operations)
            message += f"\n\nSupported operations:\n  {operations}"

        details = {
            "operation": operation,
            "adapter_name": adapter_name,
            "supported_operations_count": len(self.supported_operations),
        }

        super().__init__(message, details)


class MetadataUnavailableError(OpenCatalogError):
    """
    Raised when metadata cannot be retrieved from the source system.

    This could be due to permissions, connectivity, or system limitations.
    """

    def __init__(
        self,
        resource: str,
        reason: str,
        recoverable: bool = True,
    ):
        self.resource = resource
        self.reason = reason
        self.recoverable = recoverable

        message = f"Metadata unavailable for: {resource}\n"
        message += f"Reason: {reason}"

        if recoverable:
            message += "\n\nThis may be a temporary issue. Try again later."
        else:
            message += "\n\nThis resource's metadata cannot be accessed."

        details = {"resource": resource, "reason": reason, "recoverable": recoverable}

        super().__init__(message, details)


class TooManyResultsError(OpenCatalogError):
    """
    Raised when a search returns more results than the limit allows.

    Suggests ways to narrow the search.
    """

    def __init__(
        self,
        result_count: int,
        limit: int,
        query: str,
    ):
        self.result_count = result_count
        self.limit = limit
        self.query = query

        message = f"Search returned {result_count} results, exceeding limit of {limit}\n"
        message += f"Query: {query}\n\n"
        message += "Try:\n"
        message += "  - Adding more specific search patterns\n"
        message += "  - Using filters to narrow results\n"
        message += "  - Searching within a specific schema"

        details = {"result_count": result_count, "limit": limit, "query": query}

        super().__init__(message, details)
