from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class QueryStatus(Enum):
    """Status of a SQL query execution."""

    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class SqlErrorType(Enum):
    """Classification of SQL errors for intelligent error handling."""

    SYNTAX_ERROR = "syntax_error"
    SEMANTIC_ERROR = "semantic_error"  # Table/column not found, etc.
    PERMISSION_ERROR = "permission_error"
    DATA_ERROR = "data_error"  # Constraint violations, type mismatches
    PERFORMANCE_ERROR = "performance_error"  # Timeouts, resource limits
    CONNECTION_ERROR = "connection_error"
    CASE_SENSITIVITY_ERROR = "case_sensitivity_error"  # PostgreSQL specific
    UNKNOWN_ERROR = "unknown_error"


class DatabaseType(Enum):
    """Database types for error code mapping."""

    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    SQLSERVER = "sqlserver"
    ORACLE = "oracle"
    UNKNOWN = "unknown"


@dataclass
class RecoveryStrategy:
    """Represents a strategy for recovering from a SQL error."""

    strategy_id: str
    description: str
    corrected_sql: Optional[str]
    confidence: float  # 0.0 to 1.0
    explanation: str
    requires_user_input: bool = False
    auto_applicable: bool = True  # Can be applied automatically


@dataclass
class SqlError:
    """Comprehensive SQL error information with classification and recovery options."""

    error_type: SqlErrorType
    original_error: str
    error_code: Optional[str] = None  # Database-specific error code
    database_type: Optional[DatabaseType] = None
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    table_name: Optional[str] = None
    column_name: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    recovery_strategies: Optional[List[RecoveryStrategy]] = None

    def get_best_auto_recovery(self) -> Optional[RecoveryStrategy]:
        """Get the best recovery strategy that can be applied automatically."""
        if not self.recovery_strategies:
            return None

        auto_strategies = [
            strategy
            for strategy in self.recovery_strategies
            if strategy.auto_applicable and not strategy.requires_user_input
        ]

        if not auto_strategies:
            return None

        # Return highest confidence strategy
        return max(auto_strategies, key=lambda x: x.confidence)

    def is_retryable(self) -> bool:
        """Check if this error type is worth retrying with corrections."""
        retryable_types = {
            SqlErrorType.SYNTAX_ERROR,
            SqlErrorType.SEMANTIC_ERROR,
            SqlErrorType.CASE_SENSITIVITY_ERROR,
            SqlErrorType.DATA_ERROR,
        }
        return self.error_type in retryable_types


@dataclass
class SqlQueryResult:
    """
    Comprehensive result object for SQL query execution.
    Includes structured error information and recovery strategies.
    """

    status: QueryStatus
    data: Any = None
    query: Optional[str] = None
    execution_time_ms: Optional[float] = None
    row_count: Optional[int] = None
    column_count: Optional[int] = None
    artifact: Optional[str] = None  # Base64 encoded data for artifacts

    # Error information (populated when status is ERROR)
    error: Optional[SqlError] = None

    # Legacy fields for backward compatibility
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    error_type: Optional[str] = None

    def __post_init__(self):
        """Sync legacy error fields with SqlError object."""
        if self.error:
            self.error_message = self.error.original_error
            self.error_code = self.error.error_code
            self.error_type = self.error.error_type.value

    @property
    def is_success(self) -> bool:
        """Check if the query was successful."""
        return self.status == QueryStatus.SUCCESS

    @property
    def is_error(self) -> bool:
        """Check if the query had an error."""
        return self.status == QueryStatus.ERROR

    @property
    def is_retryable(self) -> bool:
        """Check if this error is worth retrying with corrections."""
        return self.error and self.error.is_retryable()

    def get_display_result(self) -> str:
        """Get a human-readable representation of the result."""
        if self.is_success:
            if self.data is not None:
                return str(self.data)
            else:
                return "Query executed successfully (no data returned)"
        else:
            if self.error:
                return f"Query failed: {self.error.original_error}"
            else:
                return f"Query failed: {self.error_message or 'Unknown error'}"

    def get_error_details(self) -> Dict[str, Any]:
        """Get detailed error information for error handling."""
        if self.error:
            return {
                "error_message": self.error.original_error,
                "error_code": self.error.error_code,
                "error_type": self.error.error_type.value,
                "database_type": (
                    self.error.database_type.value if self.error.database_type else None
                ),
                "table_name": self.error.table_name,
                "column_name": self.error.column_name,
                "line_number": self.error.line_number,
                "column_number": self.error.column_number,
                "context": self.error.context,
                "query": self.query,
                "is_retryable": self.is_retryable,
                "recovery_strategies_count": (
                    len(self.error.recovery_strategies)
                    if self.error.recovery_strategies
                    else 0
                ),
            }
        else:
            # Legacy fallback
            return {
                "error_message": self.error_message,
                "error_code": self.error_code,
                "error_type": self.error_type,
                "query": self.query,
            }

    def get_best_recovery_strategy(self) -> Optional[RecoveryStrategy]:
        """Get the best recovery strategy for automatic correction."""
        return self.error.get_best_auto_recovery() if self.error else None

    def get_recovery_strategies(
        self, auto_only: bool = False
    ) -> List[RecoveryStrategy]:
        """Get all available recovery strategies."""
        if not self.error or not self.error.recovery_strategies:
            return []

        if auto_only:
            return [
                strategy
                for strategy in self.error.recovery_strategies
                if strategy.auto_applicable and not strategy.requires_user_input
            ]

        return self.error.recovery_strategies
