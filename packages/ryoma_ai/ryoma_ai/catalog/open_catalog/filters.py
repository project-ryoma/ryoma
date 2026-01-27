"""
Declarative search filters for Open Catalog.

These filters provide a system-agnostic way to refine metadata searches,
translating to system-specific queries (SQL WHERE clauses, API filters, etc.).
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class SearchFilter:
    """
    Declarative metadata filters for refining search results.

    These filters translate to system-specific query predicates,
    allowing database-agnostic metadata filtering.

    Example:
        >>> filter = SearchFilter(
        ...     has_column="email",
        ...     row_count_min=1000,
        ...     modified_after=datetime(2025, 1, 1)
        ... )
    """

    # ========================================
    # Column-based filters
    # ========================================

    has_column: Optional[str] = None
    """Filter tables that have a column matching this name"""

    has_columns: Optional[List[str]] = None
    """Filter tables that have ALL of these columns"""

    has_any_columns: Optional[List[str]] = None
    """Filter tables that have ANY of these columns"""

    # ========================================
    # Type-based filters
    # ========================================

    column_type: Optional[str] = None
    """Filter columns by data type (VARCHAR, INTEGER, etc.)"""

    column_type_in: Optional[List[str]] = None
    """Filter columns matching any of these data types"""

    has_primary_key: Optional[bool] = None
    """Filter tables that have/don't have a primary key"""

    has_foreign_keys: Optional[bool] = None
    """Filter tables that have/don't have foreign keys"""

    # ========================================
    # Size-based filters
    # ========================================

    row_count_min: Optional[int] = None
    """Minimum number of rows"""

    row_count_max: Optional[int] = None
    """Maximum number of rows"""

    size_bytes_min: Optional[int] = None
    """Minimum storage size in bytes"""

    size_bytes_max: Optional[int] = None
    """Maximum storage size in bytes"""

    # ========================================
    # Temporal filters
    # ========================================

    created_after: Optional[datetime] = None
    """Filter tables created after this timestamp"""

    created_before: Optional[datetime] = None
    """Filter tables created before this timestamp"""

    modified_after: Optional[datetime] = None
    """Filter tables modified after this timestamp"""

    modified_before: Optional[datetime] = None
    """Filter tables modified before this timestamp"""

    # ========================================
    # Tag-based filters
    # ========================================

    has_tag: Optional[str] = None
    """Filter by single tag"""

    has_tags: Optional[List[str]] = None
    """Filter by multiple tags (ALL must match)"""

    has_any_tags: Optional[List[str]] = None
    """Filter by multiple tags (ANY can match)"""

    # ========================================
    # Namespace filters
    # ========================================

    schema_name: Optional[str] = None
    """Filter by specific schema/namespace"""

    schema_pattern: Optional[str] = None
    """Filter by schema name pattern (glob-style)"""

    # ========================================
    # System-specific filters (extensible)
    # ========================================

    properties: Dict[str, Any] = field(default_factory=dict)
    """
    System-specific filters.

    Examples:
        - PostgreSQL: {"tablespace": "fast_ssd"}
        - Snowflake: {"clustering_key": "date"}
        - BigQuery: {"partitioning_field": "created_at"}
    """

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert filter to dictionary representation.

        Only includes non-None values for clarity.
        """
        result = {}

        # Column filters
        if self.has_column:
            result["has_column"] = self.has_column
        if self.has_columns:
            result["has_columns"] = self.has_columns
        if self.has_any_columns:
            result["has_any_columns"] = self.has_any_columns

        # Type filters
        if self.column_type:
            result["column_type"] = self.column_type
        if self.column_type_in:
            result["column_type_in"] = self.column_type_in
        if self.has_primary_key is not None:
            result["has_primary_key"] = self.has_primary_key
        if self.has_foreign_keys is not None:
            result["has_foreign_keys"] = self.has_foreign_keys

        # Size filters
        if self.row_count_min is not None:
            result["row_count_min"] = self.row_count_min
        if self.row_count_max is not None:
            result["row_count_max"] = self.row_count_max
        if self.size_bytes_min is not None:
            result["size_bytes_min"] = self.size_bytes_min
        if self.size_bytes_max is not None:
            result["size_bytes_max"] = self.size_bytes_max

        # Temporal filters
        if self.created_after:
            result["created_after"] = self.created_after.isoformat()
        if self.created_before:
            result["created_before"] = self.created_before.isoformat()
        if self.modified_after:
            result["modified_after"] = self.modified_after.isoformat()
        if self.modified_before:
            result["modified_before"] = self.modified_before.isoformat()

        # Tag filters
        if self.has_tag:
            result["has_tag"] = self.has_tag
        if self.has_tags:
            result["has_tags"] = self.has_tags
        if self.has_any_tags:
            result["has_any_tags"] = self.has_any_tags

        # Namespace filters
        if self.schema_name:
            result["schema_name"] = self.schema_name
        if self.schema_pattern:
            result["schema_pattern"] = self.schema_pattern

        # System-specific
        if self.properties:
            result["properties"] = self.properties

        return result

    def is_empty(self) -> bool:
        """Check if filter has any constraints."""
        return len(self.to_dict()) == 0

    def __repr__(self) -> str:
        """Human-readable representation."""
        active_filters = self.to_dict()
        if not active_filters:
            return "SearchFilter(empty)"

        filter_strs = [f"{k}={v}" for k, v in active_filters.items()]
        return f"SearchFilter({', '.join(filter_strs)})"


@dataclass
class PatternMatcher:
    """
    Helper for translating glob patterns to system-specific wildcards.

    Patterns:
        - "*customer*" → SQL: "%customer%"
        - "dim_*" → SQL: "dim_%"
        - "fact_*_daily" → SQL: "fact_%_daily"
    """

    pattern: str
    """Glob-style pattern"""

    def to_sql_like(self) -> str:
        """
        Convert glob pattern to SQL LIKE pattern.

        Translations:
            * → %  (matches any number of characters)
            ? → _  (matches exactly one character)
        """
        sql_pattern = self.pattern.replace("*", "%").replace("?", "_")
        return sql_pattern

    def to_regex(self) -> str:
        """
        Convert glob pattern to regex pattern.

        Useful for systems that support regex-based filtering.
        """
        import re

        # Escape regex special characters except * and ?
        escaped = re.escape(self.pattern)

        # Replace escaped globs with regex equivalents
        regex = escaped.replace(r"\*", ".*").replace(r"\?", ".")

        # Anchor the pattern
        return f"^{regex}$"

    def matches(self, value: str) -> bool:
        """
        Check if a value matches this pattern.

        Uses fnmatch for glob-style matching.
        """
        from fnmatch import fnmatch

        return fnmatch(value.lower(), self.pattern.lower())

    def __repr__(self) -> str:
        """Human-readable representation."""
        return f"PatternMatcher('{self.pattern}')"
