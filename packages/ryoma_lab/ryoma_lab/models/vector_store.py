from datetime import datetime
from typing import Optional

import reflex as rx


class DocumentProject(rx.Model, table=True):
    """
    Represents a document project/workspace that uses vector storage.
    Multiple projects can exist, each with their own document collections.
    The actual vector store configuration comes from rxconfig.py.
    """

    project_name: str  # Unique identifier for the project/workspace
    description: Optional[str] = None  # Human-readable description
    document_count: int = 0  # Number of documents indexed
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool = True
