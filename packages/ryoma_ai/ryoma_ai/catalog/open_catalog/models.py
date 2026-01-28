"""
Metadata element models for Open Catalog.

These dataclasses represent the canonical metadata structure across
all database systems, following RFC-001.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ElementType(str, Enum):
    """Types of metadata elements."""

    CATALOG = "catalog"
    NAMESPACE = "namespace"  # Schema, database, topic group
    TABLE = "table"
    VIEW = "view"
    MATERIALIZED_VIEW = "materialized_view"
    COLUMN = "column"
    INDEX = "index"
    CONSTRAINT = "constraint"
    # Extensible for non-tabular systems
    TOPIC = "topic"  # Kafka
    STREAM = "stream"  # Kinesis
    FILE = "file"  # Data lake
    MODEL = "model"  # ML models


@dataclass
class MetadataElement:
    """
    Base class for all metadata entities.

    This is the minimal interface that all metadata objects must implement.
    """

    name: str
    """Short name of the element (e.g., 'customers', 'email')"""

    type: ElementType
    """Type of metadata element"""

    qualified_name: str
    """Fully qualified identifier (e.g., 'prod.public.customers')"""

    properties: Dict[str, Any] = field(default_factory=dict)
    """System-specific attributes (partitions, clustering, collation, etc.)"""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "type": self.type.value,
            "qualified_name": self.qualified_name,
            "properties": self.properties,
        }


@dataclass
class ForeignKeyRef:
    """Reference to a foreign key relationship."""

    referenced_table: str
    """Qualified name of referenced table"""

    referenced_column: str
    """Column name in referenced table"""

    constraint_name: Optional[str] = None
    """Name of the foreign key constraint (if available)"""


@dataclass
class ColumnMetadata(MetadataElement):
    """
    Metadata for a database column or field.

    Extends MetadataElement with column-specific attributes.
    """

    table_name: str
    """Name of the table this column belongs to"""

    data_type: str
    """Data type (VARCHAR, INTEGER, TIMESTAMP, etc.)"""

    nullable: bool = True
    """Whether the column accepts NULL values"""

    primary_key: bool = False
    """Whether this column is part of the primary key"""

    foreign_keys: List[ForeignKeyRef] = field(default_factory=list)
    """Foreign key relationships"""

    default_value: Optional[str] = None
    """Default value for the column"""

    max_length: Optional[int] = None
    """Maximum length for string types"""

    precision: Optional[int] = None
    """Precision for numeric/decimal types"""

    scale: Optional[int] = None
    """Scale for numeric/decimal types"""

    def __post_init__(self):
        """Set type to COLUMN after initialization."""
        self.type = ElementType.COLUMN

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        base = super().to_dict()
        base.update(
            {
                "table_name": self.table_name,
                "data_type": self.data_type,
                "nullable": self.nullable,
                "primary_key": self.primary_key,
                "foreign_keys": [
                    {
                        "referenced_table": fk.referenced_table,
                        "referenced_column": fk.referenced_column,
                        "constraint_name": fk.constraint_name,
                    }
                    for fk in self.foreign_keys
                ],
                "default_value": self.default_value,
                "max_length": self.max_length,
                "precision": self.precision,
                "scale": self.scale,
            }
        )
        return base


@dataclass
class TableMetadata(MetadataElement):
    """
    Metadata for a database table or table-like entity.

    Represents tables, views, materialized views, or similar structures.
    """

    schema_name: Optional[str] = None
    """Schema/namespace this table belongs to"""

    columns: List[ColumnMetadata] = field(default_factory=list)
    """List of columns in this table"""

    row_count: Optional[int] = None
    """Approximate number of rows"""

    size_bytes: Optional[int] = None
    """Storage size in bytes"""

    created_at: Optional[datetime] = None
    """When the table was created"""

    last_updated_at: Optional[datetime] = None
    """When the table was last modified"""

    table_type: ElementType = ElementType.TABLE
    """Type: TABLE, VIEW, or MATERIALIZED_VIEW"""

    description: Optional[str] = None
    """Human-readable description"""

    tags: List[str] = field(default_factory=list)
    """Tags applied to this table"""

    def __post_init__(self):
        """Set type based on table_type after initialization."""
        self.type = self.table_type

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        base = super().to_dict()
        base.update(
            {
                "schema_name": self.schema_name,
                "columns": [col.to_dict() for col in self.columns],
                "row_count": self.row_count,
                "size_bytes": self.size_bytes,
                "created_at": self.created_at.isoformat() if self.created_at else None,
                "last_updated_at": (
                    self.last_updated_at.isoformat() if self.last_updated_at else None
                ),
                "table_type": self.table_type.value,
                "description": self.description,
                "tags": self.tags,
            }
        )
        return base


@dataclass
class NamespaceMetadata(MetadataElement):
    """
    Metadata for a schema, database, or namespace.

    Represents logical groupings of tables (e.g., 'public' schema in Postgres).
    """

    catalog_name: Optional[str] = None
    """Parent catalog this namespace belongs to"""

    tables: List[TableMetadata] = field(default_factory=list)
    """Tables in this namespace"""

    namespace_type: str = "schema"
    """Type of namespace (schema, database, etc.)"""

    description: Optional[str] = None
    """Human-readable description"""

    def __post_init__(self):
        """Set type to NAMESPACE after initialization."""
        self.type = ElementType.NAMESPACE

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        base = super().to_dict()
        base.update(
            {
                "catalog_name": self.catalog_name,
                "tables": [table.to_dict() for table in self.tables],
                "namespace_type": self.namespace_type,
                "description": self.description,
            }
        )
        return base


@dataclass
class RelationshipMetadata:
    """
    Metadata for relationships between tables.

    Represents foreign key constraints, join paths, or logical relationships.
    """

    from_table: str
    """Source table qualified name"""

    to_table: str
    """Target table qualified name"""

    from_columns: List[str]
    """Column(s) in source table"""

    to_columns: List[str]
    """Column(s) in target table"""

    relationship_type: str = "foreign_key"
    """Type: foreign_key, logical_join, etc."""

    constraint_name: Optional[str] = None
    """Name of the constraint (if applicable)"""

    confidence_score: float = 1.0
    """Confidence in this relationship (0.0-1.0)"""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "from_table": self.from_table,
            "to_table": self.to_table,
            "from_columns": self.from_columns,
            "to_columns": self.to_columns,
            "relationship_type": self.relationship_type,
            "constraint_name": self.constraint_name,
            "confidence_score": self.confidence_score,
        }


@dataclass
class SearchResult:
    """
    Result from a metadata search operation.

    Contains the matched element plus relevance metadata.
    """

    element: MetadataElement
    """The matched metadata element"""

    match_score: float = 1.0
    """Relevance score (0.0-1.0)"""

    match_reason: Optional[str] = None
    """Explanation of why this matched"""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "element": self.element.to_dict(),
            "match_score": self.match_score,
            "match_reason": self.match_reason,
        }
