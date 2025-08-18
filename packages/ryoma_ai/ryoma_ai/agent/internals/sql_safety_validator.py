from typing import Dict, List, Optional, Set, Tuple, Any
import re
from dataclasses import dataclass
from enum import IntEnum, Enum
from ryoma_ai.datasource.sql import SqlDataSource


class SafetyLevel(IntEnum):
    SAFE = 1
    WARNING = 2
    DANGEROUS = 3
    BLOCKED = 4

    @property
    def name_str(self) -> str:
        """Return the string name of the safety level."""
        return {
            1: "safe",
            2: "warning",
            3: "dangerous",
            4: "blocked"
        }[self.value]


class ValidationRule(Enum):
    NO_DROP_OPERATIONS = "no_drop_operations"
    NO_DELETE_WITHOUT_WHERE = "no_delete_without_where"
    NO_UPDATE_WITHOUT_WHERE = "no_update_without_where"
    NO_TRUNCATE_OPERATIONS = "no_truncate_operations"
    LIMIT_RESULT_SIZE = "limit_result_size"
    NO_SYSTEM_TABLES = "no_system_tables"
    NO_DANGEROUS_FUNCTIONS = "no_dangerous_functions"
    REQUIRE_EXPLICIT_COLUMNS = "require_explicit_columns"
    NO_NESTED_QUERIES_LIMIT = "no_nested_queries_limit"
    TIME_LIMIT_ENFORCEMENT = "time_limit_enforcement"


@dataclass
class SafetyViolation:
    """Represents a safety violation in a SQL query."""
    rule: ValidationRule
    severity: SafetyLevel
    message: str
    line_number: Optional[int] = None
    column_position: Optional[int] = None
    suggested_fix: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of SQL safety validation."""
    is_safe: bool
    safety_level: SafetyLevel
    violations: List[SafetyViolation]
    sanitized_query: Optional[str] = None
    execution_allowed: bool = True


class SqlSafetyValidator:
    """
    Comprehensive SQL safety validator that checks queries for dangerous operations
    and enforces security policies.
    """

    def __init__(
        self,
        datasource: Optional[SqlDataSource] = None,
        safety_config: Optional[Dict[str, Any]] = None
    ):
        self.datasource = datasource
        self.safety_config = safety_config or self._default_safety_config()
        self.enabled_rules = set(ValidationRule)
        self.system_tables = self._get_system_tables()

    def validate_query(self, sql_query: str, context: Optional[Dict] = None) -> ValidationResult:
        """
        Validate a SQL query for safety and security issues.

        Args:
            sql_query: The SQL query to validate
            context: Additional context like user permissions, table access

        Returns:
            ValidationResult with safety assessment and violations
        """
        violations = []

        # Run all enabled validation rules
        for rule in self.enabled_rules:
            rule_violations = self._apply_rule(rule, sql_query, context)
            violations.extend(rule_violations)

        # Determine overall safety level
        safety_level = self._calculate_safety_level(violations)

        # Determine if execution should be allowed
        execution_allowed = safety_level not in [SafetyLevel.DANGEROUS, SafetyLevel.BLOCKED]

        # Generate sanitized query if possible
        sanitized_query = self._sanitize_query(sql_query, violations) if violations else None

        return ValidationResult(
            is_safe=safety_level == SafetyLevel.SAFE,
            safety_level=safety_level,
            violations=violations,
            sanitized_query=sanitized_query,
            execution_allowed=execution_allowed
        )

    def enable_rule(self, rule: ValidationRule):
        """Enable a specific validation rule."""
        self.enabled_rules.add(rule)

    def disable_rule(self, rule: ValidationRule):
        """Disable a specific validation rule."""
        self.enabled_rules.discard(rule)

    def set_safety_config(self, config: Dict[str, Any]):
        """Update safety configuration."""
        self.safety_config.update(config)

    def _default_safety_config(self) -> Dict[str, Any]:
        """Default safety configuration."""
        return {
            "max_result_rows": 10000,
            "max_nested_queries": 3,
            "max_execution_time_seconds": 300,
            "allowed_functions": [
                "COUNT", "SUM", "AVG", "MAX", "MIN", "UPPER", "LOWER",
                "SUBSTRING", "CONCAT", "DATE", "NOW", "COALESCE"
            ],
            "blocked_functions": [
                "LOAD_FILE", "INTO OUTFILE", "SYSTEM", "EXEC", "EXECUTE"
            ],
            "protected_tables": [
                "information_schema", "mysql", "performance_schema", "sys"
            ]
        }

    def _get_system_tables(self) -> Set[str]:
        """Get list of system tables that should be protected."""
        return set(self.safety_config.get("protected_tables", []))

    def _apply_rule(self, rule: ValidationRule, sql_query: str, context: Optional[Dict]) -> List[SafetyViolation]:
        """Apply a specific validation rule to the query."""
        violations = []

        if rule == ValidationRule.NO_DROP_OPERATIONS:
            violations.extend(self._check_drop_operations(sql_query))
        elif rule == ValidationRule.NO_DELETE_WITHOUT_WHERE:
            violations.extend(self._check_delete_without_where(sql_query))
        elif rule == ValidationRule.NO_UPDATE_WITHOUT_WHERE:
            violations.extend(self._check_update_without_where(sql_query))
        elif rule == ValidationRule.NO_TRUNCATE_OPERATIONS:
            violations.extend(self._check_truncate_operations(sql_query))
        elif rule == ValidationRule.LIMIT_RESULT_SIZE:
            violations.extend(self._check_result_size_limit(sql_query))
        elif rule == ValidationRule.NO_SYSTEM_TABLES:
            violations.extend(self._check_system_tables(sql_query))
        elif rule == ValidationRule.NO_DANGEROUS_FUNCTIONS:
            violations.extend(self._check_dangerous_functions(sql_query))
        elif rule == ValidationRule.REQUIRE_EXPLICIT_COLUMNS:
            violations.extend(self._check_explicit_columns(sql_query))
        elif rule == ValidationRule.NO_NESTED_QUERIES_LIMIT:
            violations.extend(self._check_nested_queries_limit(sql_query))

        return violations

    def _check_drop_operations(self, sql_query: str) -> List[SafetyViolation]:
        """Check for DROP operations."""
        violations = []
        query_upper = sql_query.upper()

        drop_patterns = [
            (r'\bDROP\s+TABLE\b', "DROP TABLE operation detected"),
            (r'\bDROP\s+DATABASE\b', "DROP DATABASE operation detected"),
            (r'\bDROP\s+SCHEMA\b', "DROP SCHEMA operation detected"),
            (r'\bDROP\s+INDEX\b', "DROP INDEX operation detected"),
            (r'\bDROP\s+VIEW\b', "DROP VIEW operation detected")
        ]

        for pattern, message in drop_patterns:
            if re.search(pattern, query_upper):
                violations.append(SafetyViolation(
                    rule=ValidationRule.NO_DROP_OPERATIONS,
                    severity=SafetyLevel.BLOCKED,
                    message=message,
                    suggested_fix="Remove DROP operation or use a safer alternative"
                ))

        return violations

    def _check_delete_without_where(self, sql_query: str) -> List[SafetyViolation]:
        """Check for DELETE operations without WHERE clause."""
        violations = []
        query_upper = sql_query.upper()

        # Find DELETE statements
        delete_matches = re.finditer(r'\bDELETE\s+FROM\s+\w+', query_upper)

        for match in delete_matches:
            # Check if there's a WHERE clause after this DELETE
            remaining_query = query_upper[match.end():]
            if not re.search(r'\bWHERE\b', remaining_query.split(';')[0]):
                violations.append(SafetyViolation(
                    rule=ValidationRule.NO_DELETE_WITHOUT_WHERE,
                    severity=SafetyLevel.DANGEROUS,
                    message="DELETE operation without WHERE clause - will delete all rows",
                    suggested_fix="Add WHERE clause to limit which rows are deleted"
                ))

        return violations

    def _check_update_without_where(self, sql_query: str) -> List[SafetyViolation]:
        """Check for UPDATE operations without WHERE clause."""
        violations = []
        query_upper = sql_query.upper()

        # Find UPDATE statements
        update_matches = re.finditer(r'\bUPDATE\s+\w+\s+SET\b', query_upper)

        for match in update_matches:
            # Check if there's a WHERE clause after this UPDATE
            remaining_query = query_upper[match.end():]
            if not re.search(r'\bWHERE\b', remaining_query.split(';')[0]):
                violations.append(SafetyViolation(
                    rule=ValidationRule.NO_UPDATE_WITHOUT_WHERE,
                    severity=SafetyLevel.DANGEROUS,
                    message="UPDATE operation without WHERE clause - will update all rows",
                    suggested_fix="Add WHERE clause to limit which rows are updated"
                ))

        return violations

    def _check_truncate_operations(self, sql_query: str) -> List[SafetyViolation]:
        """Check for TRUNCATE operations."""
        violations = []
        query_upper = sql_query.upper()

        if re.search(r'\bTRUNCATE\s+TABLE\b', query_upper):
            violations.append(SafetyViolation(
                rule=ValidationRule.NO_TRUNCATE_OPERATIONS,
                severity=SafetyLevel.DANGEROUS,
                message="TRUNCATE operation detected - will delete all data",
                suggested_fix="Use DELETE with WHERE clause for safer data removal"
            ))

        return violations

    def _check_result_size_limit(self, sql_query: str) -> List[SafetyViolation]:
        """Check if query has appropriate result size limits."""
        violations = []
        query_upper = sql_query.upper()

        # Check if SELECT query has LIMIT clause
        if re.search(r'\bSELECT\b', query_upper) and not re.search(r'\bLIMIT\b', query_upper):
            max_rows = self.safety_config.get("max_result_rows", 10000)
            violations.append(SafetyViolation(
                rule=ValidationRule.LIMIT_RESULT_SIZE,
                severity=SafetyLevel.WARNING,
                message=f"Query without LIMIT clause may return large result set",
                suggested_fix=f"Add LIMIT {max_rows} to prevent excessive memory usage"
            ))

        return violations

    def _check_system_tables(self, sql_query: str) -> List[SafetyViolation]:
        """Check for access to system tables."""
        violations = []
        query_lower = sql_query.lower()

        for system_table in self.system_tables:
            if system_table.lower() in query_lower:
                violations.append(SafetyViolation(
                    rule=ValidationRule.NO_SYSTEM_TABLES,
                    severity=SafetyLevel.BLOCKED,
                    message=f"Access to system table '{system_table}' is not allowed",
                    suggested_fix="Use application tables instead of system tables"
                ))

        return violations

    def _check_dangerous_functions(self, sql_query: str) -> List[SafetyViolation]:
        """Check for dangerous SQL functions."""
        violations = []
        query_upper = sql_query.upper()

        blocked_functions = self.safety_config.get("blocked_functions", [])

        for func in blocked_functions:
            if re.search(rf'\b{func}\s*\(', query_upper):
                violations.append(SafetyViolation(
                    rule=ValidationRule.NO_DANGEROUS_FUNCTIONS,
                    severity=SafetyLevel.BLOCKED,
                    message=f"Dangerous function '{func}' is not allowed",
                    suggested_fix=f"Remove or replace '{func}' function"
                ))

        return violations

    def _check_explicit_columns(self, sql_query: str) -> List[SafetyViolation]:
        """Check for SELECT * usage."""
        violations = []
        query_upper = sql_query.upper()

        if re.search(r'\bSELECT\s+\*\b', query_upper):
            violations.append(SafetyViolation(
                rule=ValidationRule.REQUIRE_EXPLICIT_COLUMNS,
                severity=SafetyLevel.WARNING,
                message="SELECT * usage detected - may impact performance",
                suggested_fix="Specify explicit column names instead of using *"
            ))

        return violations

    def _check_nested_queries_limit(self, sql_query: str) -> List[SafetyViolation]:
        """Check for excessive nested queries."""
        violations = []

        # Count nested SELECT statements
        nested_count = sql_query.upper().count('(SELECT')
        max_nested = self.safety_config.get("max_nested_queries", 3)

        if nested_count > max_nested:
            violations.append(SafetyViolation(
                rule=ValidationRule.NO_NESTED_QUERIES_LIMIT,
                severity=SafetyLevel.WARNING,
                message=f"Query has {nested_count} nested queries (limit: {max_nested})",
                suggested_fix="Consider breaking down into multiple simpler queries"
            ))

        return violations

    def _calculate_safety_level(self, violations: List[SafetyViolation]) -> SafetyLevel:
        """Calculate overall safety level based on violations."""
        if not violations:
            return SafetyLevel.SAFE

        max_severity = max(violation.severity for violation in violations)
        return max_severity

    def _sanitize_query(self, sql_query: str, violations: List[SafetyViolation]) -> Optional[str]:
        """Attempt to sanitize the query by applying suggested fixes."""
        sanitized = sql_query

        for violation in violations:
            if violation.suggested_fix and violation.severity != SafetyLevel.BLOCKED:
                # Apply simple fixes
                if violation.rule == ValidationRule.LIMIT_RESULT_SIZE:
                    if "LIMIT" not in sanitized.upper():
                        max_rows = self.safety_config.get("max_result_rows", 10000)
                        sanitized = sanitized.rstrip(';') + f" LIMIT {max_rows};"

                elif violation.rule == ValidationRule.REQUIRE_EXPLICIT_COLUMNS:
                    # This would require more complex parsing to fix properly
                    pass

        return sanitized if sanitized != sql_query else None

    def create_safety_report(self, validation_result: ValidationResult) -> str:
        """Create a human-readable safety report."""
        report = f"SQL Safety Validation Report\n"
        report += f"{'=' * 40}\n\n"

        report += f"Overall Safety Level: {validation_result.safety_level.name_str.upper()}\n"
        report += f"Execution Allowed: {'Yes' if validation_result.execution_allowed else 'No'}\n"
        report += f"Total Violations: {len(validation_result.violations)}\n\n"

        if validation_result.violations:
            report += "Violations Found:\n"
            for i, violation in enumerate(validation_result.violations, 1):
                report += f"{i}. {violation.message}\n"
                report += f"   Rule: {violation.rule.value}\n"
                report += f"   Severity: {violation.severity.name_str.upper()}\n"
                if violation.suggested_fix:
                    report += f"   Suggested Fix: {violation.suggested_fix}\n"
                report += "\n"

        if validation_result.sanitized_query:
            report += "Sanitized Query Available:\n"
            report += f"{validation_result.sanitized_query}\n"

        return report

    def get_safety_recommendations(self, sql_query: str) -> List[str]:
        """Get general safety recommendations for SQL queries."""
        recommendations = []
        query_upper = sql_query.upper()

        # General recommendations
        recommendations.append("Always use parameterized queries to prevent SQL injection")
        recommendations.append("Limit result sets with appropriate WHERE clauses and LIMIT")
        recommendations.append("Use explicit column names instead of SELECT *")
        recommendations.append("Test queries on small datasets before running on production")

        # Query-specific recommendations
        if "JOIN" in query_upper:
            recommendations.append("Ensure proper indexing on join columns for performance")

        if "ORDER BY" in query_upper:
            recommendations.append("Consider adding LIMIT when using ORDER BY to avoid sorting large datasets")

        if re.search(r'\b(DELETE|UPDATE|INSERT)\b', query_upper):
            recommendations.append("Always backup data before running modification queries")
            recommendations.append("Test modification queries with WHERE 1=0 first to check syntax")

        return recommendations
