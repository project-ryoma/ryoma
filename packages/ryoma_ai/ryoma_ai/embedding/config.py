from typing import Dict, Optional

from pydantic import BaseModel


class EmbeddingConfig(BaseModel):
    type: str  # e.g. "openai", "huggingface", "cohere"
    model: Optional[str] = None  # e.g. "text-embedding-3-small"
    api_key: Optional[str] = None
    endpoint: Optional[str] = None  # e.g. custom URL for local or hosted model
    parameters: Optional[Dict[str, str]] = None  # custom model kwargs
