"""
Open Catalog - Database-agnostic metadata search framework.

This package provides a deterministic, zero-indexing metadata search system
that treats metadata like source code—searchable, inspectable, and verifiable.

The search methods are built directly into DataSource:
- datasource.search_tables(pattern="*customer*")
- datasource.search_columns(pattern="*email*")
- datasource.inspect_table("customers")
- datasource.get_sample_data("customers", limit=10)

Based on RFC-001: Open Catalog
"""

from ryoma_ai.catalog.open_catalog.exceptions import (
    ColumnNotFoundException,
    OpenCatalogError,
    SearchTimeoutError,
    TableNotFoundException,
)
from ryoma_ai.catalog.open_catalog.filters import SearchFilter
from ryoma_ai.catalog.open_catalog.models import (
    ColumnMetadata,
    ElementType,
    ForeignKeyRef,
    MetadataElement,
    NamespaceMetadata,
    RelationshipMetadata,
    TableMetadata,
)

__all__ = [
    # Models (for type hints and advanced usage)
    "MetadataElement",
    "TableMetadata",
    "ColumnMetadata",
    "NamespaceMetadata",
    "RelationshipMetadata",
    "ForeignKeyRef",
    "ElementType",
    # Filters
    "SearchFilter",
    # Exceptions
    "OpenCatalogError",
    "TableNotFoundException",
    "ColumnNotFoundException",
    "SearchTimeoutError",
]
