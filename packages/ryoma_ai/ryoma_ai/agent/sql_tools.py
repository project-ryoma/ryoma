"""
Centralized SQL tool definitions.

This module provides factory functions for creating SQL tool sets,
eliminating duplication across different SQL agent modes.
"""

from typing import List
from langchain_core.tools import BaseTool

from ryoma_ai.tool.sql_tool import (
    SqlQueryTool,
    CreateTableTool,
    QueryProfileTool,
    QueryExplanationTool,
    QueryOptimizationTool,
)


def get_basic_sql_tools() -> List[BaseTool]:
    """
    Get basic SQL tools for simple agent mode.

    Returns:
        List containing:
        - SqlQueryTool: Execute SQL queries
        - CreateTableTool: Create tables
        - QueryProfileTool: Profile query performance
    """
    return [
        SqlQueryTool(),
        CreateTableTool(),
        QueryProfileTool(),
    ]


def get_enhanced_sql_tools() -> List[BaseTool]:
    """
    Get enhanced SQL tools with additional capabilities.

    Returns:
        List containing basic tools plus:
        - QueryExplanationTool: Explain query execution plans
        - QueryOptimizationTool: Suggest query optimizations
    """
    basic_tools = get_basic_sql_tools()
    enhanced_tools = [
        QueryExplanationTool(),
        QueryOptimizationTool(),
    ]
    return basic_tools + enhanced_tools


def get_reforce_sql_tools() -> List[BaseTool]:
    """
    Get ReFoRCE SQL tools.

    Currently uses the same tools as enhanced mode.
    ReFoRCE uses reflection and forcing in its prompting strategy
    rather than different tools.

    Returns:
        List of SQL tools for ReFoRCE mode
    """
    return get_enhanced_sql_tools()
