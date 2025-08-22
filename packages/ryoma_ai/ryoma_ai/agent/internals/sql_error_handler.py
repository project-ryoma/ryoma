from typing import Dict, List, Optional, Tuple
import re
from ryoma_ai.datasource.sql import SqlDataSource
from ryoma_ai.models.sql import (
    SqlError, SqlErrorType, DatabaseType, RecoveryStrategy
)


class SqlErrorHandler:
    """
    Advanced error handler for SQL queries with automatic recovery strategies.
    Provides detailed error analysis and suggests corrections.
    """

    def __init__(self, datasource: Optional[SqlDataSource] = None):
        self.datasource = datasource
        self.error_patterns = self._initialize_error_patterns()

    def analyze_error(self, error_message: str, sql_query: str, context: Optional[Dict] = None) -> SqlError:
        """
        Analyze a SQL error and classify it with context.

        Args:
            error_message: The error message from the database
            sql_query: The SQL query that caused the error
            context: Additional context like table names, column names

        Returns:
            SqlError object with detailed analysis
        """
        error_type = self._classify_error(error_message)
        error_code = self._extract_error_code(error_message)
        line_number, column_number = self._extract_position(error_message)

        # Include sql_query in context for recovery strategies
        context = context or {}
        context['sql_query'] = sql_query

        return SqlError(
            error_type=error_type,
            original_error=error_message,
            error_code=error_code,
            line_number=line_number,
            column_number=column_number,
            context=context
        )

    def suggest_recovery_strategies(self, sql_error: SqlError) -> List[RecoveryStrategy]:
        """
        Suggest recovery strategies for a SQL error.

        Args:
            sql_error: The analyzed SQL error

        Returns:
            List of recovery strategies ordered by confidence
        """
        strategies = []

        # We need the original SQL query to generate recovery strategies
        # For now, we'll use empty string as placeholder - this should be improved
        sql_query = sql_error.context.get('sql_query', '') if sql_error.context else ''

        if sql_error.error_type == SqlErrorType.SYNTAX_ERROR:
            strategies.extend(self._handle_syntax_error(sql_error, sql_query))
        elif sql_error.error_type == SqlErrorType.SEMANTIC_ERROR:
            strategies.extend(self._handle_semantic_error(sql_error, sql_query))
        elif sql_error.error_type == SqlErrorType.PERMISSION_ERROR:
            strategies.extend(self._handle_permission_error(sql_error, sql_query))
        elif sql_error.error_type == SqlErrorType.DATA_ERROR:
            strategies.extend(self._handle_data_error(sql_error, sql_query))
        elif sql_error.error_type == SqlErrorType.PERFORMANCE_ERROR:
            strategies.extend(self._handle_performance_error(sql_error, sql_query))
        else:
            strategies.extend(self._handle_generic_error(sql_error, sql_query))

        # Sort by confidence
        strategies.sort(key=lambda x: x.confidence, reverse=True)
        return strategies

    def auto_correct_query(self, sql_query: str, error_message: str, context: Optional[Dict] = None) -> Optional[str]:
        """
        Attempt to automatically correct a SQL query based on the error.

        Args:
            sql_query: The original SQL query
            error_message: The error message
            context: Additional context

        Returns:
            Corrected SQL query if possible, None otherwise
        """
        sql_error = self.analyze_error(error_message, sql_query, context)
        strategies = self.suggest_recovery_strategies(sql_error)

        # Return the highest confidence strategy that doesn't require user input
        for strategy in strategies:
            if not strategy.requires_user_input and strategy.confidence > 0.7:
                return strategy.corrected_sql

        return None

    def _detect_database_type(self, exception: Exception, error_message: str) -> DatabaseType:
        """
        Detect database type from exception type or error message.
        """
        exception_module = exception.__class__.__module__

        # Check for PostgreSQL exceptions (both psycopg2 and psycopg3)
        if 'psycopg' in exception_module:
            return DatabaseType.POSTGRESQL

        # Check for MySQL exceptions
        if 'mysql' in exception_module.lower() or 'MySQLdb' in exception_module:
            return DatabaseType.MYSQL

        # Check for SQLite exceptions
        if 'sqlite' in exception_module.lower():
            return DatabaseType.SQLITE

        # Check for SQL Server exceptions
        if 'pyodbc' in exception_module or 'sql server' in error_message.lower():
            return DatabaseType.SQLSERVER

        # Check for Oracle exceptions
        if 'oracle' in exception_module.lower() or 'oracle' in error_message.lower():
            return DatabaseType.ORACLE

        # Fallback to error message analysis
        error_lower = error_message.lower()
        if 'postgres' in error_lower or 'postgresql' in error_lower:
            return DatabaseType.POSTGRESQL
        elif 'mysql' in error_lower:
            return DatabaseType.MYSQL
        elif 'sqlite' in error_lower:
            return DatabaseType.SQLITE
        elif 'sql server' in error_lower or 'sqlserver' in error_lower:
            return DatabaseType.SQLSERVER
        elif 'oracle' in error_lower:
            return DatabaseType.ORACLE

        return DatabaseType.UNKNOWN

    def _extract_postgres_error_code(self, exception: Exception) -> Optional[str]:
        """
        Extract PostgreSQL error code (pgcode) from exception.
        """
        # Check for pgcode attribute (available in psycopg2 and psycopg3)
        if hasattr(exception, 'pgcode'):
            return exception.pgcode

        # Fallback to error message parsing
        error_message = str(exception)
        pgcode_match = re.search(r'SQLSTATE\s+([A-Z0-9]{5})', error_message)
        if pgcode_match:
            return pgcode_match.group(1)

        return None

    def _extract_mysql_error_code(self, exception: Exception) -> Optional[str]:
        """
        Extract MySQL error code (errno) from exception.
        """
        # Check for errno attribute
        if hasattr(exception, 'errno'):
            return str(exception.errno)

        # Fallback to error message parsing
        error_message = str(exception)
        errno_match = re.search(r'\(([0-9]+),', error_message)
        if errno_match:
            return errno_match.group(1)

        return None

    def _initialize_error_patterns(self) -> Dict[SqlErrorType, List[str]]:
        """Initialize patterns for error classification."""
        return {
            SqlErrorType.SYNTAX_ERROR: [
                r"syntax error",
                r"unexpected token",
                r"missing",
                r"expected",
                r"invalid syntax",
                r"parse error"
            ],
            SqlErrorType.SEMANTIC_ERROR: [
                r"table.*doesn't exist",
                r"column.*doesn't exist",
                r"unknown table",
                r"unknown column",
                r"ambiguous column",
                r"function.*doesn't exist",
                r"column.*must appear in the group by clause",
                r"perhaps you meant to reference the column"
            ],
            SqlErrorType.PERMISSION_ERROR: [
                r"access denied",
                r"permission denied",
                r"insufficient privileges",
                r"not authorized"
            ],
            SqlErrorType.DATA_ERROR: [
                r"data too long",
                r"out of range",
                r"division by zero",
                r"invalid date",
                r"constraint violation"
            ],
            SqlErrorType.PERFORMANCE_ERROR: [
                r"timeout",
                r"query too complex",
                r"resource limit",
                r"memory limit"
            ],
            SqlErrorType.CONNECTION_ERROR: [
                r"connection",
                r"network",
                r"server",
                r"timeout"
            ]
        }

    def _classify_error(self, error_message: str) -> SqlErrorType:
        """Classify the error type based on the error message."""
        error_lower = error_message.lower()

        for error_type, patterns in self.error_patterns.items():
            for pattern in patterns:
                if re.search(pattern, error_lower):
                    return error_type

        return SqlErrorType.UNKNOWN_ERROR

    def _extract_error_code(self, error_message: str) -> Optional[str]:
        """Extract error code from error message if present."""
        # Common error code patterns
        patterns = [
            r"error (\d+)",
            r"code (\d+)",
            r"\[(\d+)\]"
        ]

        for pattern in patterns:
            match = re.search(pattern, error_message, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def _extract_position(self, error_message: str) -> Tuple[Optional[int], Optional[int]]:
        """Extract line and column position from error message."""
        line_match = re.search(r"line (\d+)", error_message, re.IGNORECASE)
        column_match = re.search(r"column (\d+)", error_message, re.IGNORECASE)

        line_number = int(line_match.group(1)) if line_match else None
        column_number = int(column_match.group(1)) if column_match else None

        return line_number, column_number

    def _handle_syntax_error(self, sql_error: SqlError, sql_query: str) -> List[RecoveryStrategy]:
        """Handle syntax errors with specific recovery strategies."""
        strategies = []
        sql = sql_query
        error_msg = sql_error.original_error.lower()

        # Missing comma
        if "expected comma" in error_msg or "missing comma" in error_msg:
            corrected_sql = self._fix_missing_comma(sql)
            strategies.append(RecoveryStrategy(
                strategy_id="fix_missing_comma",
                description="Add missing comma in SELECT clause or column list",
                corrected_sql=corrected_sql,
                confidence=0.8,
                explanation="Added missing comma between columns or expressions"
            ))

        # Missing parentheses
        if "missing" in error_msg and ("parenthes" in error_msg or "bracket" in error_msg):
            corrected_sql = self._fix_missing_parentheses(sql)
            strategies.append(RecoveryStrategy(
                strategy_id="fix_parentheses",
                description="Add missing parentheses",
                corrected_sql=corrected_sql,
                confidence=0.7,
                explanation="Added missing opening or closing parentheses"
            ))

        # Missing semicolon
        if "missing semicolon" in error_msg:
            corrected_sql = sql.rstrip() + ";"
            strategies.append(RecoveryStrategy(
                strategy_id="add_semicolon",
                description="Add missing semicolon",
                corrected_sql=corrected_sql,
                confidence=0.9,
                explanation="Added missing semicolon at end of query"
            ))

        return strategies

    def _handle_semantic_error(self, sql_error: SqlError, sql_query: str) -> List[RecoveryStrategy]:
        """Handle semantic errors like missing tables/columns."""
        strategies = []
        sql = sql_query
        error_msg = sql_error.original_error.lower()

        # Table doesn't exist
        if "table" in error_msg and ("doesn't exist" in error_msg or "not found" in error_msg):
            table_name = self._extract_table_name_from_error(error_msg)
            if table_name and self.datasource:
                similar_tables = self._find_similar_table_names(table_name)
                for similar_table in similar_tables:
                    corrected_sql = sql.replace(table_name, similar_table)
                    strategies.append(RecoveryStrategy(
                        strategy_id=f"replace_table_{similar_table}",
                        description=f"Replace '{table_name}' with '{similar_table}'",
                        corrected_sql=corrected_sql,
                        confidence=0.6,
                        explanation=f"'{similar_table}' is a similar table name that exists",
                        requires_user_input=True
                    ))

        # PostgreSQL case sensitivity hint (e.g., 'Perhaps you meant to reference the column "artist.Age"')
        if "perhaps you meant to reference the column" in error_msg or "hint:" in error_msg:
            # Use original error message to preserve case in hint extraction
            suggested_column = self._extract_postgresql_column_hint(sql_error.original_error)
            if suggested_column:
                # Extract the column name without table prefix for replacement
                column_part = suggested_column.split('.')[-1].strip('"')
                corrected_sql = self._fix_postgresql_column_case(sql, column_part, suggested_column)
                strategies.append(RecoveryStrategy(
                    strategy_id="fix_postgresql_column_case",
                    description=f"Fix column case sensitivity using PostgreSQL hint: {suggested_column}",
                    corrected_sql=corrected_sql,
                    confidence=0.9,  # High confidence since PostgreSQL provided the hint
                    explanation=f"PostgreSQL suggested using {suggested_column} instead",
                    requires_user_input=False  # Auto-fix since PostgreSQL provided the exact solution
                ))

        # Column doesn't exist
        elif "column" in error_msg and ("doesn't exist" in error_msg or "not found" in error_msg):
            column_name = self._extract_column_name_from_error(error_msg)
            if column_name and self.datasource:
                similar_columns = self._find_similar_column_names(column_name, sql)
                for similar_column in similar_columns:
                    corrected_sql = sql.replace(column_name, similar_column)
                    strategies.append(RecoveryStrategy(
                        strategy_id=f"replace_column_{similar_column}",
                        description=f"Replace '{column_name}' with '{similar_column}'",
                        corrected_sql=corrected_sql,
                        confidence=0.6,
                        explanation=f"'{similar_column}' is a similar column name that exists",
                        requires_user_input=True
                    ))

        return strategies

    def _handle_permission_error(self, sql_error: SqlError, sql_query: str) -> List[RecoveryStrategy]:
        """Handle permission errors."""
        strategies = []

        strategies.append(RecoveryStrategy(
            strategy_id="request_permissions",
            description="Request necessary permissions from database administrator",
            corrected_sql=sql_query,
            confidence=0.3,
            explanation="This query requires additional database permissions",
            requires_user_input=True
        ))

        return strategies

    def _handle_data_error(self, sql_error: SqlError, sql_query: str) -> List[RecoveryStrategy]:
        """Handle data-related errors."""
        strategies = []
        sql = sql_query
        error_msg = sql_error.original_error.lower()

        # Division by zero
        if "division by zero" in error_msg:
            corrected_sql = self._add_zero_division_check(sql)
            strategies.append(RecoveryStrategy(
                strategy_id="fix_division_by_zero",
                description="Add check for division by zero",
                corrected_sql=corrected_sql,
                confidence=0.8,
                explanation="Added CASE statement to handle division by zero"
            ))

        return strategies

    def _handle_performance_error(self, sql_error: SqlError, sql_query: str) -> List[RecoveryStrategy]:
        """Handle performance-related errors."""
        strategies = []
        sql = sql_query

        # Query timeout
        if "timeout" in sql_error.original_error.lower():
            # Add LIMIT clause if missing
            if "LIMIT" not in sql.upper():
                corrected_sql = sql.rstrip(';') + " LIMIT 1000;"
                strategies.append(RecoveryStrategy(
                    strategy_id="add_limit",
                    description="Add LIMIT clause to reduce query time",
                    corrected_sql=corrected_sql,
                    confidence=0.7,
                    explanation="Added LIMIT to prevent timeout on large result sets"
                ))

        return strategies

    def _handle_generic_error(self, sql_error: SqlError, sql_query: str) -> List[RecoveryStrategy]:
        """Handle generic or unknown errors."""
        strategies = []

        strategies.append(RecoveryStrategy(
            strategy_id="manual_review",
            description="Manual review required",
            corrected_sql=sql_query,
            confidence=0.1,
            explanation="This error requires manual analysis and correction",
            requires_user_input=True
        ))

        return strategies

    def _fix_missing_comma(self, sql: str) -> str:
        """Attempt to fix missing comma in SQL."""
        # This is a simplified implementation
        # In practice, you'd use a proper SQL parser
        lines = sql.split('\n')
        for i, line in enumerate(lines):
            if 'SELECT' in line.upper() and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line and not next_line.startswith(',') and not next_line.upper().startswith('FROM'):
                    lines[i] = line.rstrip() + ','
        return '\n'.join(lines)

    def _fix_missing_parentheses(self, sql: str) -> str:
        """Attempt to fix missing parentheses."""
        open_count = sql.count('(')
        close_count = sql.count(')')

        if open_count > close_count:
            return sql + ')' * (open_count - close_count)
        elif close_count > open_count:
            return '(' * (close_count - open_count) + sql

        return sql

    def _add_zero_division_check(self, sql: str) -> str:
        """Add division by zero check to SQL."""
        # Find division operations and wrap them
        division_pattern = r'(\w+)\s*/\s*(\w+)'

        def replace_division(match):
            numerator = match.group(1)
            denominator = match.group(2)
            return f"CASE WHEN {denominator} = 0 THEN NULL ELSE {numerator} / {denominator} END"

        return re.sub(division_pattern, replace_division, sql)

    def _extract_table_name_from_error(self, error_msg: str) -> Optional[str]:
        """Extract table name from error message."""
        patterns = [
            r"table '([^']+)'",
            r"table `([^`]+)`",
            r"table ([^\s]+)"
        ]

        for pattern in patterns:
            match = re.search(pattern, error_msg)
            if match:
                return match.group(1)

        return None

    def _extract_column_name_from_error(self, error_msg: str) -> Optional[str]:
        """Extract column name from error message."""
        patterns = [
            r"column '([^']+)'",
            r"column `([^`]+)`",
            r"column ([^\s]+)"
        ]

        for pattern in patterns:
            match = re.search(pattern, error_msg)
            if match:
                return match.group(1)

        return None

    def _find_similar_table_names(self, table_name: str) -> List[str]:
        """Find similar table names in the database."""
        if not self.datasource:
            return []

        try:
            catalog = self.datasource.get_catalog()
            all_tables = []
            for schema in catalog.schemas:
                for table in schema.tables:
                    all_tables.append(table.table_name)

            # Simple similarity based on edit distance or common substrings
            similar_tables = []
            for existing_table in all_tables:
                if self._calculate_similarity(table_name, existing_table) > 0.6:
                    similar_tables.append(existing_table)

            return similar_tables[:3]  # Return top 3 matches
        except Exception:
            return []

    def _find_similar_column_names(self, column_name: str, sql: str) -> List[str]:
        """Find similar column names in the tables used in the query."""
        if not self.datasource:
            return []

        # Extract table names from SQL (simplified)
        table_names = re.findall(r'FROM\s+(\w+)', sql, re.IGNORECASE)
        table_names.extend(re.findall(r'JOIN\s+(\w+)', sql, re.IGNORECASE))

        similar_columns = []
        try:
            for table_name in table_names:
                catalog = self.datasource.get_catalog(table=table_name)
                for schema in catalog.schemas:
                    for table in schema.tables:
                        for column in table.columns:
                            if self._calculate_similarity(column_name, column.name) > 0.6:
                                similar_columns.append(column.name)
        except Exception:
            pass

        return similar_columns[:3]

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings (simplified)."""
        str1_lower = str1.lower()
        str2_lower = str2.lower()

        # Simple similarity based on common characters
        if str1_lower == str2_lower:
            return 1.0

        common_chars = set(str1_lower) & set(str2_lower)
        total_chars = set(str1_lower) | set(str2_lower)

        if not total_chars:
            return 0.0

        return len(common_chars) / len(total_chars)

    def _extract_postgresql_column_hint(self, error_msg: str) -> Optional[str]:
        """Extract the suggested column name from PostgreSQL hint message."""
        # Pattern: 'Perhaps you meant to reference the column "artist.Age"'
        # Also handles: 'HINT:  Perhaps you meant to reference the column "artist.Age".'
        patterns = [
            r'perhaps you meant to reference the column "([^"]+)"',
            r'hint:.*perhaps you meant to reference the column "([^"]+)"'
        ]

        for pattern in patterns:
            match = re.search(pattern, error_msg, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def _fix_postgresql_column_case(self, sql: str, original_column: str, suggested_column: str) -> str:
        """Fix PostgreSQL column case sensitivity by replacing with suggested column."""
        # Handle both bare column names and table.column references

        # If suggested column has table prefix, extract the column name
        if '.' in suggested_column:
            _, column_name = suggested_column.split('.', 1)
            column_name = column_name.strip('"')

            # Replace patterns like "ORDER BY Age" with "ORDER BY \"Age\""
            # Use the exact case from the PostgreSQL hint
            patterns = [
                rf'\b{re.escape(original_column)}\b',  # Bare column name
                rf'\b\w+\.{re.escape(original_column)}\b',  # table.column
            ]

            for pattern in patterns:
                if re.search(pattern, sql, re.IGNORECASE):
                    # Replace with quoted column name, preserving case from hint
                    sql = re.sub(pattern, f'"{column_name}"', sql, flags=re.IGNORECASE)
                    break
        else:
            # Simple column name replacement with quotes, preserving case from hint
            sql = re.sub(rf'\b{re.escape(original_column)}\b', f'"{suggested_column}"', sql, flags=re.IGNORECASE)

        return sql
