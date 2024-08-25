from typing import Any

from sql_formatter.core import format_sql


def format_code(code: Any) -> str:
    """Format the code for display."""
    return format_sql(str(code))
