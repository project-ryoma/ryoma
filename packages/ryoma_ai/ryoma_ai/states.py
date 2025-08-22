from typing import Any, Dict, List, Optional

from langgraph.graph.message import add_messages
from ryoma_ai.models.agent import ColumnExplorationResult, FormatRestriction
from typing_extensions import Annotated, TypedDict


class MessageState(TypedDict, total=False):
    messages: Annotated[list, add_messages]

    # SQL Agent fields - optional for all agents
    original_question: str
    current_step: str
    schema_analysis: Optional[Dict]
    relevant_tables: Optional[List[Dict]]
    query_plan: Optional[Dict]
    generated_sql: Optional[str]
    validation_result: Optional[Dict]
    execution_result: Optional[str]
    error_info: Optional[Dict]
    safety_check: Optional[Dict]
    final_answer: Optional[str]
    retry_count: int
    max_retries: int
    sql_approval_received: bool

    # ReFoRCE Agent fields - also optional
    compressed_schema: Optional[str]
    format_restriction: Optional[FormatRestriction]
    column_exploration: Optional[ColumnExplorationResult]
    self_refinement_iterations: int
    parallel_candidates: List[Dict[str, Any]]
    consensus_result: Optional[str]
    confidence_score: float
