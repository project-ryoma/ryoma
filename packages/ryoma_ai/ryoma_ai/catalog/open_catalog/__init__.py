"""
Open Catalog - Database-agnostic metadata search framework.

This package provides a deterministic, zero-indexing metadata search system
that treats metadata like source code—searchable, inspectable, and verifiable.

Based on RFC-001: Open Catalog
"""

from ryoma_ai.catalog.open_catalog.protocol import OpenCatalogAdapter
from ryoma_ai.catalog.open_catalog.models import (
    MetadataElement,
    TableMetadata,
    ColumnMetadata,
    NamespaceMetadata,
    RelationshipMetadata,
    ForeignKeyRef,
    ElementType,
)
from ryoma_ai.catalog.open_catalog.filters import SearchFilter
from ryoma_ai.catalog.open_catalog.exceptions import (
    OpenCatalogError,
    TableNotFoundException,
    ColumnNotFoundException,
    SearchTimeoutError,
)

__all__ = [
    # Protocol
    "OpenCatalogAdapter",
    # Models
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
