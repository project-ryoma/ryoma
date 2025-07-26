from enum import Enum

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass


class AgentType(Enum):
    ryoma = "ryoma_ai"
    chat = "chat"
    base = "base"
    embedding = "embedding"
    workflow = "workflow"
    custom = "custom"

@dataclass
class ColumnExplorationResult:
    """Result from column exploration phase."""
    exploration_queries: List[str]
    exploration_results: List[str]
    relevant_columns: List[str]
    column_insights: Dict[str, Any]


@dataclass
class FormatRestriction:
    """Expected answer format restriction."""
    format_description: str
    column_names: List[str]
    data_types: List[str]
    example_format: str
