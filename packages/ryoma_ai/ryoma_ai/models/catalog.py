from typing import Dict, Any
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class CatalogIndex:
    """Catalog index metadata."""

    catalog_id: str
    data_source_id: str
    catalog_name: str
    indexed_at: datetime
    schema_count: int
    table_count: int
    column_count: int
    index_level: str  # catalog, schema, table, column

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        data['indexed_at'] = self.indexed_at.isoformat()
        return data

    @classmethod
    def from_dict(cls,
                  data: Dict[str, Any]) -> 'CatalogIndex':
        """Create from dictionary loaded from storage."""
        data['indexed_at'] = datetime.fromisoformat(data['indexed_at'])
        return cls(**data)
