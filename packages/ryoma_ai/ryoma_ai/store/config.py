"""
Configuration for store backends.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class StoreConfig(BaseModel):
    """Configuration for store backend."""
    
    type: str = Field(
        default="memory",
        description="Type of store: memory, postgres, redis"
    )
    
    connection_string: Optional[str] = Field(
        default=None,
        description="Connection string for database stores"
    )
    
    options: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional store-specific options"
    )
    
    def to_factory_params(self) -> Dict[str, Any]:
        """Convert config to parameters for StoreFactory."""
        params = {"store_type": self.type}
        
        if self.connection_string:
            params["store_config"] = {
                "connection_string": self.connection_string,
                **self.options
            }
        elif self.options:
            params["store_config"] = self.options
            
        return params