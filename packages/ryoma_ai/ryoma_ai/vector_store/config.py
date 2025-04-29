from pydantic import BaseModel
from typing import Optional

class VectorStoreConfig(BaseModel):
    type: str  # "chroma", "pgvector", "qdrant"
    collection_name: str = "ryoma_index"
    persist_path: Optional[str] = None            # for chroma
    pgvector_url: Optional[str] = None            # for pgvector
    qdrant_url: Optional[str] = None              # for qdrant
