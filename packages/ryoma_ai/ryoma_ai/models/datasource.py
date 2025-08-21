"""
Data source Registration Model
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class DataSourceRegistration:
    """Data source registration information."""

    id: str
    name: str
    type: str
    config: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    description: Optional[str] = None
    tags: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls,
                  data: Dict[str, Any]) -> 'DataSourceRegistration':
        """Create from dictionary loaded from storage."""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)
