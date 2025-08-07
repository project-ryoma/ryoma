import base64
import pickle
from abc import ABC
from typing import Any, Dict, Literal, Optional, Sequence, Type, Union

from langchain_core.tools import BaseTool
from langgraph.prebuilt import InjectedStore
from pydantic import BaseModel, Field
from ryoma_ai.datasource.sql import SqlDataSource
from ryoma_ai.models.sql import SqlQueryResult, QueryStatus
from sqlalchemy.engine import Result
from typing_extensions import Annotated


def get_datasource_from_store(store) -> SqlDataSource:
    """Helper function to extract datasource from store with consistent error handling."""
    datasource_result = store.get(("datasource",), "main")
    if not datasource_result:
        raise ValueError("No datasource available in store")
    return datasource_result.value


class QueryInput(BaseModel):
    query: str = Field(description="sql query that can be executed by the sql catalog.")
    store: Annotated[object, InjectedStore()] = Field(
        ..., description="Store containing datasource for the query."
    )

    model_config = {"arbitrary_types_allowed": True}


class SqlQueryTool(BaseTool):
    """Tool for querying a SQL catalog."""

    name: str = "sql_database_query"
    description: str = """
    Execute a SQL query against the catalog and get back the result.
    Returns a structured result object with success/failure status.
    If the query is not correct, an error message will be returned.
    If an error is returned, rewrite the query, check the query, and try again.
    """
    args_schema: Type[BaseModel] = QueryInput
    response_format: Literal["content", "content_and_artifact"] = "content_and_artifact"

    def _run(
        self,
        query: str,
        store,
        **kwargs,
    ) -> SqlQueryResult:
        """Execute the query and return a structured result object."""
        import time
        start_time = time.time()

        try:
            datasource = get_datasource_from_store(store)
            result = datasource.query(query)

            execution_time_ms = (time.time() - start_time) * 1000

            # Try to get result metadata
            row_count = None
            column_count = None
            if hasattr(result, 'shape'):
                # DataFrame-like object
                row_count = result.shape[0]
                column_count = result.shape[1]
            elif hasattr(result, '__len__'):
                # List-like object
                try:
                    row_count = len(result)
                    if row_count > 0 and hasattr(result[0], '__len__'):
                        column_count = len(result[0])
                except:
                    pass

            # Serialize the result to a base64 encoded string as the artifact
            artifact = base64.b64encode(pickle.dumps(result)).decode("utf-8")

            return SqlQueryResult(
                status=QueryStatus.SUCCESS,
                data=result,
                query=query,
                execution_time_ms=execution_time_ms,
                row_count=row_count,
                column_count=column_count,
                artifact=artifact
            )

        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000

            return SqlQueryResult(
                status=QueryStatus.ERROR,
                query=query,
                execution_time_ms=execution_time_ms,
                error_message=str(e),
                data={'raw_exception': e}
            )


class Column(BaseModel):
    column_name: str = Field(..., description="Name of the column")
    column_type: str = Field(..., description="Type of the column")
    nullable: Optional[bool] = Field(None, description="Whether the column is nullable")
    primary_key: Optional[bool] = Field(
        None, description="Whether the column is a primary key"
    )


class CreateTableInputSchema(BaseModel):
    store: Annotated[object, InjectedStore()] = Field(
        description="Store containing datasource for the query."
    )
    table_name: str = Field(..., description="Name of the table")
    table_columns: Sequence[Column] = Field(
        ..., description="List of columns in the table"
    )
    table_type: Optional[str] = Field(..., description="Type of the table")


class CreateTableTool(BaseTool):
    """Tool for creating a table in a SQL catalog."""

    name: str = "create_table"
    description: str = """
    Create a table in the catalog.
    If the table already exists, an error message will be returned.
    input arguments are table_name and table_columns.
    """
    args_schema: Type[BaseModel] = CreateTableInputSchema

    def _run(
        self,
        store,
        table_name: str,
        table_columns: Sequence[Column],
        **kwargs,
    ) -> Union[str, Sequence[Dict[str, Any]], Result]:
        """Execute the query, return the results or an error message."""
        try:
            datasource = get_datasource_from_store(store)
            columns = ",\n".join(
                f'{column.column_name} "{column.column_type}"' for column in table_columns
            )
            return datasource.query(
                "CREATE TABLE {table_name} ({columns})".format(
                    table_name=table_name, columns=columns
                )
            )
        except Exception as e:
            return f"Error creating table: {str(e)}"


class QueryPlanTool(BaseTool):
    """Tool for getting the query plan of a SQL query."""

    name: str = "query_plan"
    description: str = """
    Get the query plan of a SQL query.
    If the query is not correct, an error message will be returned.
    """
    args_schema: Type[BaseModel] = QueryInput

    def _run(
        self,
        query: str,
        store,
        **kwargs,
    ) -> str:
        """Execute the query, return the results or an error message."""
        try:
            datasource = get_datasource_from_store(store)
            return datasource.get_query_plan(query)
        except Exception as e:
            return f"Error getting query plan: {str(e)}"


class QueryProfileTool(BaseTool):
    """Tool for getting the query profile of a SQL query."""

    name: str = "query_profile"
    description: str = """
    Get the query profile of a SQL query.
    If the query is not correct, an error message will be returned.
    """
    args_schema: Type[BaseModel] = QueryInput

    def _run(
        self,
        query: str,
        store,
        **kwargs,
    ) -> str:
        """Execute the query, return the results or an error message."""
        try:
            datasource = get_datasource_from_store(store)
            return datasource.get_query_profile(query)
        except Exception as e:
            return f"Error getting query profile: {str(e)}"


class SchemaAnalysisInput(BaseModel):
    store: Annotated[object, InjectedStore()] = Field(
        description="Store containing datasource for schema analysis."
    )
    table_name: Optional[str] = Field(None, description="Specific table to analyze")
    schema_name: Optional[str] = Field(None, description="Specific schema to analyze")

    model_config = {"arbitrary_types_allowed": True}


class SchemaAnalysisTool(BaseTool):
    """Tool for analyzing database schema and table relationships."""

    name: str = "schema_analysis"
    description: str = """
    Analyze database schema to understand table structures, relationships, and constraints.
    Can analyze a specific table, schema, or the entire database.
    Returns detailed information about columns, data types, constraints, and relationships.
    """
    args_schema: Type[BaseModel] = SchemaAnalysisInput

    def _run(
        self,
        store,
        table_name: Optional[str] = None,
        schema_name: Optional[str] = None,
        **kwargs,
    ) -> str:
        """Analyze schema and return detailed information."""
        try:
            datasource = get_datasource_from_store(store)
            if table_name:
                # Analyze specific table
                catalog = datasource.get_catalog(schema=schema_name, table=table_name)
                analysis = self._analyze_table(catalog.schemas[0].tables[0])
            elif schema_name:
                # Analyze specific schema
                catalog = datasource.get_catalog(schema=schema_name)
                analysis = self._analyze_schema(catalog.schemas[0])
            else:
                # Analyze entire database
                catalog = datasource.get_catalog()
                analysis = self._analyze_catalog(catalog)

            return analysis
        except Exception as e:
            return f"Error analyzing schema: {str(e)}"

    def _analyze_table(self, table) -> str:
        """Analyze a single table."""
        analysis = f"Table Analysis: {table.table_name}\n"
        analysis += f"Columns ({len(table.columns)}):\n"

        for col in table.columns:
            analysis += f"  - {col.name}: {col.type}"
            if not col.nullable:
                analysis += " (NOT NULL)"
            analysis += "\n"

        return analysis

    def _analyze_schema(self, schema) -> str:
        """Analyze a schema with multiple tables."""
        analysis = f"Schema Analysis: {schema.schema_name}\n"
        analysis += f"Tables ({len(schema.tables)}):\n"

        for table in schema.tables:
            analysis += f"  - {table.table_name} ({len(table.columns)} columns)\n"

        return analysis

    def _analyze_catalog(self, catalog) -> str:
        """Analyze entire catalog."""
        analysis = f"Catalog Analysis: {catalog.catalog_name}\n"
        total_tables = sum(len(schema.tables) for schema in catalog.schemas)
        analysis += f"Schemas: {len(catalog.schemas)}, Total Tables: {total_tables}\n"

        for schema in catalog.schemas:
            analysis += f"  Schema: {schema.schema_name} ({len(schema.tables)} tables)\n"

        return analysis


class QueryValidationInput(BaseModel):
    query: str = Field(description="SQL query to validate")
    datasource: Annotated[SqlDataSource, InjectedStore()] = Field(
        description="sql data source for validation context"
    )
    check_syntax: bool = Field(True, description="Check SQL syntax")
    check_safety: bool = Field(True, description="Check for potentially dangerous operations")

    model_config = {"arbitrary_types_allowed": True}


class QueryValidationTool(BaseTool):
    """Tool for validating SQL queries before execution."""

    name: str = "query_validation"
    description: str = """
    Validate SQL queries for syntax correctness and safety.
    Checks for dangerous operations like DROP, DELETE without WHERE, etc.
    Returns validation results and suggestions for improvement.
    """
    args_schema: Type[BaseModel] = QueryValidationInput

    def _run(
        self,
        query: str,
        datasource: SqlDataSource,
        check_syntax: bool = True,
        check_safety: bool = True,
        **kwargs,
    ) -> str:
        """Validate the query and return results."""
        validation_results = []

        if check_syntax:
            syntax_result = self._check_syntax(query)
            validation_results.append(f"Syntax Check: {syntax_result}")

        if check_safety:
            safety_result = self._check_safety(query)
            validation_results.append(f"Safety Check: {safety_result}")

        return "\n".join(validation_results)

    def _check_syntax(self, query: str) -> str:
        """Basic syntax validation."""
        query_upper = query.upper().strip()

        # Basic checks
        if not query_upper:
            return "FAIL - Empty query"

        # Check for balanced parentheses
        if query.count('(') != query.count(')'):
            return "FAIL - Unbalanced parentheses"

        # Check for basic SQL keywords
        sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER']
        if not any(keyword in query_upper for keyword in sql_keywords):
            return "FAIL - No valid SQL keywords found"

        return "PASS - Basic syntax appears valid"

    def _check_safety(self, query: str) -> str:
        """Check for potentially dangerous operations."""
        query_upper = query.upper().strip()
        warnings = []

        # Check for dangerous operations
        if 'DROP TABLE' in query_upper or 'DROP DATABASE' in query_upper:
            warnings.append("WARNING - DROP operation detected")

        if 'DELETE FROM' in query_upper and 'WHERE' not in query_upper:
            warnings.append("WARNING - DELETE without WHERE clause")

        if 'UPDATE' in query_upper and 'WHERE' not in query_upper:
            warnings.append("WARNING - UPDATE without WHERE clause")

        if 'TRUNCATE' in query_upper:
            warnings.append("WARNING - TRUNCATE operation detected")

        if warnings:
            return "; ".join(warnings)
        else:
            return "PASS - No safety concerns detected"


class TableSelectionInput(BaseModel):
    question: str = Field(description="Natural language question to find relevant tables for")
    datasource: Annotated[SqlDataSource, InjectedStore()] = Field(
        description="sql data source to search tables in"
    )
    max_tables: int = Field(5, description="Maximum number of tables to return")

    model_config = {"arbitrary_types_allowed": True}


class TableSelectionTool(BaseTool):
    """Tool for intelligently selecting relevant tables for a query."""

    name: str = "table_selection"
    description: str = """
    Analyze a natural language question and suggest the most relevant tables
    from the database schema. Uses table names, column names, and relationships
    to determine relevance.
    """
    args_schema: Type[BaseModel] = TableSelectionInput

    def _run(
        self,
        question: str,
        datasource: SqlDataSource,
        max_tables: int = 5,
        **kwargs,
    ) -> str:
        """Select relevant tables based on the question."""
        try:
            catalog = datasource.get_catalog()
            relevant_tables = self._find_relevant_tables(question, catalog, max_tables)

            if not relevant_tables:
                return "No relevant tables found for the given question."

            result = f"Relevant tables for: '{question}'\n\n"
            for i, (table_info, score) in enumerate(relevant_tables, 1):
                result += f"{i}. {table_info['schema']}.{table_info['table']} (relevance: {score:.2f})\n"
                result += f"   Columns: {', '.join(table_info['columns'][:5])}"
                if len(table_info['columns']) > 5:
                    result += f" ... (+{len(table_info['columns']) - 5} more)"
                result += "\n\n"

            return result
        except Exception as e:
            return f"Error selecting tables: {str(e)}"

    def _find_relevant_tables(self, question: str, catalog, max_tables: int):
        """Find tables relevant to the question."""
        question_lower = question.lower()
        question_words = set(question_lower.split())

        table_scores = []

        for schema in catalog.schemas:
            for table in schema.tables:
                score = 0
                table_info = {
                    'schema': schema.schema_name,
                    'table': table.table_name,
                    'columns': [col.name for col in table.columns]
                }

                # Score based on table name
                table_name_words = set(table.table_name.lower().replace('_', ' ').split())
                score += len(question_words.intersection(table_name_words)) * 3

                # Score based on column names
                for col in table.columns:
                    col_words = set(col.name.lower().replace('_', ' ').split())
                    score += len(question_words.intersection(col_words)) * 2

                # Boost score for common business terms
                business_terms = {
                    'customer': ['customer', 'client', 'user'],
                    'order': ['order', 'purchase', 'transaction'],
                    'product': ['product', 'item', 'goods'],
                    'sales': ['sales', 'revenue', 'amount'],
                    'date': ['date', 'time', 'when']
                }

                for term_category, terms in business_terms.items():
                    if any(term in question_lower for term in terms):
                        if any(term in table.table_name.lower() for term in terms):
                            score += 2
                        if any(any(term in col.name.lower() for term in terms) for col in table.columns):
                            score += 1

                if score > 0:
                    table_scores.append((table_info, score))

        # Sort by score and return top results
        table_scores.sort(key=lambda x: x[1], reverse=True)
        return table_scores[:max_tables]


class QueryOptimizationInput(BaseModel):
    query: str = Field(description="SQL query to optimize")
    datasource: Annotated[SqlDataSource, InjectedStore()] = Field(
        description="sql data source for optimization context"
    )

    model_config = {"arbitrary_types_allowed": True}


class QueryOptimizationTool(BaseTool):
    """Tool for suggesting SQL query optimizations."""

    name: str = "query_optimization"
    description: str = """
    Analyze a SQL query and suggest optimizations for better performance.
    Provides recommendations for indexing, query structure, and best practices.
    """
    args_schema: Type[BaseModel] = QueryOptimizationInput

    def _run(
        self,
        query: str,
        datasource: SqlDataSource,
        **kwargs,
    ) -> str:
        """Analyze query and suggest optimizations."""
        try:
            suggestions = []
            query_upper = query.upper()

            # Check for SELECT *
            if 'SELECT *' in query_upper:
                suggestions.append("• Avoid SELECT * - specify only needed columns for better performance")

            # Check for missing WHERE clauses in large operations
            if any(op in query_upper for op in ['DELETE', 'UPDATE']) and 'WHERE' not in query_upper:
                suggestions.append("• Add WHERE clause to limit affected rows")

            # Check for LIKE with leading wildcards
            if 'LIKE \'%' in query or 'LIKE "%' in query:
                suggestions.append("• Avoid LIKE patterns starting with % - consider full-text search or different indexing")

            # Check for OR conditions that could use UNION
            if query.count(' OR ') > 2:
                suggestions.append("• Consider using UNION instead of multiple OR conditions for better index usage")

            # Check for subqueries that could be JOINs
            if 'IN (SELECT' in query_upper:
                suggestions.append("• Consider replacing IN (SELECT...) with JOIN for better performance")

            # Check for ORDER BY without LIMIT
            if 'ORDER BY' in query_upper and 'LIMIT' not in query_upper:
                suggestions.append("• Consider adding LIMIT clause when using ORDER BY to avoid sorting large result sets")

            # Check for functions in WHERE clauses
            function_patterns = ['UPPER(', 'LOWER(', 'SUBSTRING(', 'DATE(']
            if any(pattern in query_upper for pattern in function_patterns):
                suggestions.append("• Avoid functions in WHERE clauses - consider computed columns or functional indexes")

            if not suggestions:
                suggestions.append("• Query appears to follow good practices")

            result = f"Query Optimization Suggestions:\n\n"
            result += "\n".join(suggestions)

            return result
        except Exception as e:
            return f"Error analyzing query for optimization: {str(e)}"


class QueryExplanationInput(BaseModel):
    query: str = Field(description="SQL query to explain")
    datasource: Annotated[SqlDataSource, InjectedStore()] = Field(
        description="sql data source for context"
    )

    model_config = {"arbitrary_types_allowed": True}


class QueryExplanationTool(BaseTool):
    """Tool for explaining what a SQL query does in natural language."""

    name: str = "query_explanation"
    description: str = """
    Explain a SQL query in plain English, describing what data it retrieves,
    what operations it performs, and how it works step by step.
    """
    args_schema: Type[BaseModel] = QueryExplanationInput

    def _run(
        self,
        query: str,
        datasource: SqlDataSource,
        **kwargs,
    ) -> str:
        """Explain the query in natural language."""
        try:
            explanation = self._parse_and_explain_query(query)
            return explanation
        except Exception as e:
            return f"Error explaining query: {str(e)}"

    def _parse_and_explain_query(self, query: str) -> str:
        """Parse and explain the SQL query."""
        query_clean = query.strip()
        query_upper = query_clean.upper()

        explanation = "Query Explanation:\n\n"

        # Determine query type
        if query_upper.startswith('SELECT'):
            explanation += self._explain_select_query(query_clean)
        elif query_upper.startswith('INSERT'):
            explanation += "This is an INSERT query that adds new data to a table.\n"
        elif query_upper.startswith('UPDATE'):
            explanation += "This is an UPDATE query that modifies existing data in a table.\n"
        elif query_upper.startswith('DELETE'):
            explanation += "This is a DELETE query that removes data from a table.\n"
        elif query_upper.startswith('CREATE'):
            explanation += "This is a CREATE query that creates a new database object.\n"
        else:
            explanation += "This query performs database operations.\n"

        # Add complexity analysis
        complexity = self._analyze_complexity(query_clean)
        explanation += f"\nComplexity: {complexity}\n"

        return explanation

    def _explain_select_query(self, query: str) -> str:
        """Explain a SELECT query in detail."""
        explanation = "This SELECT query retrieves data from the database.\n\n"

        query_upper = query.upper()

        # Analyze SELECT clause
        if 'SELECT *' in query_upper:
            explanation += "• Selects ALL columns from the table(s)\n"
        elif 'SELECT DISTINCT' in query_upper:
            explanation += "• Selects unique/distinct values (removes duplicates)\n"
        else:
            explanation += "• Selects specific columns\n"

        # Analyze FROM clause
        if ' FROM ' in query_upper:
            explanation += "• Retrieves data from specified table(s)\n"

        # Analyze JOIN operations
        join_types = ['INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'FULL JOIN', 'CROSS JOIN']
        joins_found = [join for join in join_types if join in query_upper]
        if joins_found:
            explanation += f"• Combines data from multiple tables using {', '.join(joins_found)}\n"

        # Analyze WHERE clause
        if ' WHERE ' in query_upper:
            explanation += "• Filters results based on specified conditions\n"

        # Analyze GROUP BY
        if ' GROUP BY ' in query_upper:
            explanation += "• Groups results by specified columns for aggregation\n"

        # Analyze HAVING clause
        if ' HAVING ' in query_upper:
            explanation += "• Filters grouped results based on aggregate conditions\n"

        # Analyze ORDER BY
        if ' ORDER BY ' in query_upper:
            if ' DESC' in query_upper:
                explanation += "• Sorts results in descending order\n"
            else:
                explanation += "• Sorts results in ascending order\n"

        # Analyze LIMIT
        if ' LIMIT ' in query_upper:
            explanation += "• Limits the number of results returned\n"

        return explanation

    def _analyze_complexity(self, query: str) -> str:
        """Analyze query complexity."""
        query_upper = query.upper()
        complexity_score = 0

        # Count complexity factors
        if 'JOIN' in query_upper:
            complexity_score += query_upper.count('JOIN') * 2

        if 'SUBQUERY' in query_upper or '(SELECT' in query_upper:
            complexity_score += 3

        if 'GROUP BY' in query_upper:
            complexity_score += 2

        if 'HAVING' in query_upper:
            complexity_score += 2

        if 'UNION' in query_upper:
            complexity_score += 3

        # Determine complexity level
        if complexity_score == 0:
            return "Simple - Basic query with minimal operations"
        elif complexity_score <= 3:
            return "Moderate - Query with some joins or grouping"
        elif complexity_score <= 7:
            return "Complex - Query with multiple joins, subqueries, or advanced operations"
        else:
            return "Very Complex - Query with many advanced operations and joins"
