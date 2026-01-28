"""
ReFoRCE-Optimized SQL Agent

This implementation combines insights from two key research papers:
1. "Automatic Metadata Extraction for Text-to-SQL" (arXiv:2505.19988)
2. "ReFoRCE: A Text-to-SQL Agent with Self-Refinement, Format Restriction, and Column Exploration"

Key innovations implemented:
- Database information compression via pattern-based table grouping
- Expected answer format restriction
- Iterative column exploration with execution feedback
- Self-refinement workflow with self-consistency
- Parallelization with majority-vote consensus
"""

import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional

from langchain_core.messages import AIMessage
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from ryoma_ai.agent.internals.enhanced_sql_agent import EnhancedSqlAgent
from ryoma_ai.models.agent import ColumnExplorationResult, FormatRestriction
from ryoma_ai.states import MessageState
from ryoma_ai.tool.sql_tool import SqlQueryTool
from ryoma_data.base import DataSource


class ReFoRCESqlAgent(EnhancedSqlAgent):
    """
    ReFoRCE-optimized SQL Agent implementing state-of-the-art Text-to-SQL techniques.

    Combines automatic metadata extraction with self-refinement, format restriction,
    and column exploration for enterprise-grade SQL generation.
    """

    def __init__(
        self,
        model: str,
        model_parameters: Optional[Dict] = None,
        datasource: Optional[DataSource] = None,
        safety_config: Optional[Dict] = None,
        max_parallel_threads: int = 3,
        max_refinement_iterations: int = 5,
        compression_threshold: int = 30000,  # tokens
        **kwargs,
    ):
        super().__init__(
            model=model,
            model_parameters=model_parameters,
            datasource=datasource,
            safety_config=safety_config,
            **kwargs,
        )

        self.max_parallel_threads = max_parallel_threads
        self.max_refinement_iterations = max_refinement_iterations
        self.compression_threshold = compression_threshold

    def _build_workflow(self, graph: StateGraph) -> CompiledStateGraph:
        """Create the ReFoRCE workflow with advanced optimizations."""
        workflow = StateGraph(MessageState)

        # Add nodes for ReFoRCE methodology
        workflow.add_node("compress_database_info", self._compress_database_info)
        workflow.add_node(
            "generate_format_restriction", self._generate_format_restriction
        )
        workflow.add_node("explore_columns", self._explore_columns)
        workflow.add_node("parallel_generation", self._parallel_generation)
        workflow.add_node("self_refinement", self._self_refinement)
        workflow.add_node("consensus_voting", self._consensus_voting)
        workflow.add_node("final_validation", self._final_validation)

        # Define the ReFoRCE workflow
        workflow.set_entry_point("compress_database_info")

        workflow.add_edge("compress_database_info", "generate_format_restriction")
        workflow.add_edge("generate_format_restriction", "explore_columns")
        workflow.add_edge("explore_columns", "parallel_generation")
        workflow.add_edge("parallel_generation", "self_refinement")
        workflow.add_edge("self_refinement", "consensus_voting")
        workflow.add_edge("consensus_voting", "final_validation")
        workflow.add_edge("final_validation", END)

        return workflow.compile(
            checkpointer=self.memory,
            interrupt_before=[
                "compress_database_info",
                "generate_format_restriction",
                "explore_columns",
                "parallel_generation",
                "self_refinement",
                "consensus_voting",
                "final_validation",
            ],
            store=self.store,
        )

    def _compress_database_info(self, state: MessageState) -> MessageState:
        """
        Compress database information using pattern-based table grouping.

        Implementation of database information compression from the metadata extraction paper
        and ReFoRCE's table compression technique.
        """
        try:
            if not self.get_datasource():
                state["compressed_schema"] = "No datasource available"
                return state

            # Get full catalog
            catalog = self.get_datasource().get_catalog()

            # Calculate current schema size
            schema_info = self._build_full_schema_info(catalog)
            schema_size = len(schema_info.split())  # Rough token count

            if schema_size <= self.compression_threshold:
                state["compressed_schema"] = schema_info
                state["messages"].append(
                    AIMessage(
                        content=f"Schema size ({schema_size} tokens) within limits, no compression needed"
                    )
                )
                return state

            # Apply pattern-based compression
            compressed_schema = self._apply_pattern_based_compression(catalog)

            # Apply schema linking for further reduction
            question = state["original_question"]
            relevant_tables = self.schema_agent.suggest_table_selection(
                question, max_tables=10
            )

            # Build focused schema with only relevant tables
            focused_schema = self._build_focused_schema(catalog, relevant_tables)

            # Choose the most appropriate schema
            final_schema = (
                focused_schema
                if len(focused_schema) < len(compressed_schema)
                else compressed_schema
            )

            state["compressed_schema"] = final_schema
            state["current_step"] = "database_compression"

            compression_ratio = len(final_schema) / len(schema_info)
            state["messages"].append(
                AIMessage(
                    content=f"Compressed schema from {schema_size} to {len(final_schema.split())} tokens (ratio: {compression_ratio:.2f})"
                )
            )

        except Exception as e:
            state["compressed_schema"] = "Error in compression: " + str(e)
            state["messages"].append(
                AIMessage(content=f"Database compression failed: {str(e)}")
            )

        return state

    def _generate_format_restriction(self, state: MessageState) -> MessageState:
        """
        Generate expected answer format restriction.

        Implementation of ReFoRCE's format restriction technique to guide SQL generation.
        """
        try:
            question = state["original_question"]

            # Generate format restriction using LLM
            format_prompt = self._create_format_restriction_prompt(question)
            format_response = self._invoke_llm(format_prompt)

            # Parse format response
            format_restriction = self._parse_format_restriction(format_response)

            state["format_restriction"] = format_restriction
            state["current_step"] = "format_restriction"

            state["messages"].append(
                AIMessage(
                    content=f"Generated format restriction: {format_restriction.format_description}"
                )
            )

        except Exception as e:
            # Create default format restriction
            state["format_restriction"] = FormatRestriction(
                format_description="Default CSV format",
                column_names=["result"],
                data_types=["string"],
                example_format="```csv\nresult\nvalue1\nvalue2\n```",
            )
            state["messages"].append(
                AIMessage(
                    content=f"Format restriction generation failed, using default: {str(e)}"
                )
            )

        return state

    def _explore_columns(self, state: MessageState) -> MessageState:
        """
        Perform iterative column exploration with execution feedback.

        Implementation of ReFoRCE's column exploration technique.
        """
        try:
            question = state["original_question"]
            compressed_schema = state.get("compressed_schema", "")

            # Generate exploration queries
            exploration_queries = self._generate_exploration_queries(
                question, compressed_schema
            )

            # Execute exploration queries and collect results
            exploration_results = []
            relevant_columns = []
            column_insights = {}

            for query in exploration_queries:
                try:
                    # Execute query with safety validation
                    validation_result = self.safety_validator.validate_query(query)
                    if not validation_result.execution_allowed:
                        continue

                    # Execute the query
                    tool = SqlQueryTool()
                    result = tool._run(query=query, datasource=self.get_datasource())

                    if result and "Error" not in result:
                        exploration_results.append(result)

                        # Extract column insights
                        columns = self._extract_columns_from_query(query)
                        relevant_columns.extend(columns)

                        # Analyze result for insights
                        insights = self._analyze_exploration_result(query, result)
                        column_insights.update(insights)

                except Exception as e:
                    # Log exploration error but continue
                    state["messages"].append(
                        AIMessage(content=f"Exploration query failed: {str(e)}")
                    )
                    continue

            # Remove duplicates and limit results
            relevant_columns = list(set(relevant_columns))[
                :20
            ]  # Limit to top 20 columns
            exploration_results = exploration_results[:10]  # Limit to top 10 results

            state["column_exploration"] = ColumnExplorationResult(
                exploration_queries=exploration_queries,
                exploration_results=exploration_results,
                relevant_columns=relevant_columns,
                column_insights=column_insights,
            )

            state["current_step"] = "column_exploration"
            state["messages"].append(
                AIMessage(
                    content=f"Explored {len(exploration_queries)} queries, found {len(relevant_columns)} relevant columns"
                )
            )

        except Exception as e:
            state["column_exploration"] = ColumnExplorationResult(
                exploration_queries=[],
                exploration_results=[],
                relevant_columns=[],
                column_insights={},
            )
            state["messages"].append(
                AIMessage(content=f"Column exploration failed: {str(e)}")
            )

        return state

    def _parallel_generation(self, state: MessageState) -> MessageState:
        """
        Generate multiple SQL candidates in parallel.

        Implementation of ReFoRCE's parallelization technique.
        """
        try:
            question = state["original_question"]
            compressed_schema = state.get("compressed_schema", "")
            format_restriction = state.get("format_restriction")
            column_exploration = state.get("column_exploration")

            # Create multiple generation contexts with slight variations
            generation_contexts = self._create_generation_contexts(
                question, compressed_schema, format_restriction, column_exploration
            )

            # Generate SQL candidates in parallel
            with ThreadPoolExecutor(max_workers=self.max_parallel_threads) as executor:
                futures = [
                    executor.submit(self._generate_sql_candidate, context)
                    for context in generation_contexts
                ]

                candidates = []
                for future in futures:
                    try:
                        candidate = future.result(timeout=60)  # 60 second timeout
                        if candidate:
                            candidates.append(candidate)
                    except Exception as e:
                        state["messages"].append(
                            AIMessage(content=f"Parallel generation error: {str(e)}")
                        )

            state["parallel_candidates"] = candidates
            state["current_step"] = "parallel_generation"

            state["messages"].append(
                AIMessage(
                    content=f"Generated {len(candidates)} SQL candidates in parallel"
                )
            )

        except Exception as e:
            state["parallel_candidates"] = []
            state["messages"].append(
                AIMessage(content=f"Parallel generation failed: {str(e)}")
            )

        return state

    def _self_refinement(self, state: MessageState) -> MessageState:
        """
        Apply self-refinement with self-consistency checks.

        Implementation of ReFoRCE's self-refinement workflow.
        """
        try:
            candidates = state.get("parallel_candidates", [])
            if not candidates:
                return state

            refined_candidates = []

            for candidate in candidates:
                refined_candidate = self._refine_sql_candidate(
                    candidate,
                    state["original_question"],
                    state.get("format_restriction"),
                    state.get("column_exploration"),
                )

                if refined_candidate:
                    refined_candidates.append(refined_candidate)

            state["parallel_candidates"] = refined_candidates
            state["self_refinement_iterations"] = (
                state.get("self_refinement_iterations", 0) + 1
            )
            state["current_step"] = "self_refinement"

            state["messages"].append(
                AIMessage(
                    content=f"Refined {len(refined_candidates)} candidates (iteration {state['self_refinement_iterations']})"
                )
            )

        except Exception as e:
            state["messages"].append(
                AIMessage(content=f"Self-refinement failed: {str(e)}")
            )

        return state

    def _consensus_voting(self, state: MessageState) -> MessageState:
        """
        Apply majority-vote consensus mechanism.

        Implementation of ReFoRCE's voting mechanism.
        """
        try:
            candidates = state.get("parallel_candidates", [])
            if not candidates:
                state["consensus_result"] = None
                state["confidence_score"] = 0.0
                return state

            # Execute all candidates and collect results
            candidate_results = []
            for candidate in candidates:
                try:
                    # Validate safety first
                    validation_result = self.safety_validator.validate_query(
                        candidate["sql"]
                    )
                    if not validation_result.execution_allowed:
                        continue

                    # Execute query
                    tool = SqlQueryTool()
                    result = tool._run(
                        query=candidate["sql"], datasource=self.get_datasource()
                    )

                    if result and "Error" not in result:
                        candidate_results.append(
                            {
                                "sql": candidate["sql"],
                                "result": result,
                                "result_hash": self._hash_result(result),
                            }
                        )

                except Exception:
                    continue

            if not candidate_results:
                state["consensus_result"] = None
                state["confidence_score"] = 0.0
                return state

            # Count identical results
            result_counts = Counter(cr["result_hash"] for cr in candidate_results)

            if not result_counts:
                state["consensus_result"] = None
                state["confidence_score"] = 0.0
                return state

            # Find most common result
            most_common_hash, count = result_counts.most_common(1)[0]

            # Get the SQL that produced the most common result
            consensus_candidate = next(
                cr for cr in candidate_results if cr["result_hash"] == most_common_hash
            )

            # Calculate confidence score
            confidence_score = count / len(candidate_results)

            state["consensus_result"] = consensus_candidate["sql"]
            state["execution_result"] = consensus_candidate["result"]
            state["confidence_score"] = confidence_score
            state["current_step"] = "consensus_voting"

            state["messages"].append(
                AIMessage(
                    content=f"Consensus reached with {count}/{len(candidate_results)} agreement (confidence: {confidence_score:.2f})"
                )
            )

        except Exception as e:
            state["consensus_result"] = None
            state["confidence_score"] = 0.0
            state["messages"].append(
                AIMessage(content=f"Consensus voting failed: {str(e)}")
            )

        return state

    def _final_validation(self, state: MessageState) -> MessageState:
        """Final validation and result formatting."""
        try:
            consensus_result = state.get("consensus_result")
            execution_result = state.get("execution_result")
            confidence_score = state.get("confidence_score", 0.0)

            if consensus_result and execution_result and confidence_score > 0.5:
                # High confidence result
                final_answer = f"Query executed successfully with high confidence ({confidence_score:.2f}):\n\n{execution_result}"
            elif consensus_result and execution_result:
                # Low confidence result
                final_answer = f"Query executed with moderate confidence ({confidence_score:.2f}):\n\n{execution_result}\n\nNote: Consider manual review due to low confidence."
            else:
                # No consensus reached
                final_answer = "Unable to reach consensus on query results. Manual intervention recommended."

            state["final_answer"] = final_answer
            state["generated_sql"] = consensus_result
            state["current_step"] = "completed"

            state["messages"].append(AIMessage(content=final_answer))

        except Exception as e:
            state["final_answer"] = f"Final validation failed: {str(e)}"
            state["messages"].append(AIMessage(content=state["final_answer"]))

        return state

    # Helper methods for ReFoRCE implementation
    def _build_full_schema_info(self, catalog) -> str:
        """Build complete schema information string."""
        schema_info = f"Database: {catalog.catalog_name}\n\n"

        for schema in catalog.schemas:
            schema_info += f"Schema: {schema.schema_name}\n"
            for table in schema.tables:
                schema_info += f"  Table: {table.table_name}\n"
                for column in table.columns:
                    schema_info += f"    - {column.name}: {column.type}"
                    if not column.nullable:
                        schema_info += " (NOT NULL)"
                    schema_info += "\n"
                schema_info += "\n"

        return schema_info

    def _apply_pattern_based_compression(self, catalog) -> str:
        """Apply pattern-based table grouping compression."""
        compressed_info = f"Database: {catalog.catalog_name} (Compressed)\n\n"

        for schema in catalog.schemas:
            # Group tables by common prefixes/suffixes
            table_groups = self._group_tables_by_pattern(schema.tables)

            compressed_info += f"Schema: {schema.schema_name}\n"

            for pattern, tables in table_groups.items():
                if len(tables) > 1:
                    # Use representative table for the group
                    representative = tables[0]
                    compressed_info += (
                        f"  Table Group: {pattern}* ({len(tables)} tables)\n"
                    )
                    compressed_info += (
                        f"    Representative: {representative.table_name}\n"
                    )
                    for column in representative.columns[:5]:  # Limit columns
                        compressed_info += f"      - {column.name}: {column.type}\n"
                    if len(representative.columns) > 5:
                        compressed_info += f"      ... (+{len(representative.columns) - 5} more columns)\n"
                else:
                    # Single table, include normally
                    table = tables[0]
                    compressed_info += f"  Table: {table.table_name}\n"
                    for column in table.columns[:10]:  # Limit columns
                        compressed_info += f"    - {column.name}: {column.type}\n"
                    if len(table.columns) > 10:
                        compressed_info += (
                            f"    ... (+{len(table.columns) - 10} more columns)\n"
                        )

                compressed_info += "\n"

        return compressed_info

    def _group_tables_by_pattern(self, tables) -> Dict[str, List]:
        """Group tables by common naming patterns."""
        groups = {}

        for table in tables:
            # Extract pattern (common prefix/suffix)
            pattern = self._extract_table_pattern(table.table_name)

            if pattern not in groups:
                groups[pattern] = []
            groups[pattern].append(table)

        return groups

    def _extract_table_pattern(self, table_name: str) -> str:
        """Extract naming pattern from table name."""
        # Remove common date patterns
        pattern = re.sub(r"\d{4}\d{2}\d{2}", "YYYYMMDD", table_name)
        pattern = re.sub(r"\d{4}_\d{2}_\d{2}", "YYYY_MM_DD", pattern)
        pattern = re.sub(r"\d{8}", "YYYYMMDD", pattern)

        # Remove other numeric patterns
        pattern = re.sub(r"\d+", "N", pattern)

        return pattern

    def _build_focused_schema(self, catalog, relevant_tables) -> str:
        """Build schema focused on relevant tables only."""
        focused_info = f"Database: {catalog.catalog_name} (Focused)\n\n"

        relevant_table_names = {t["table"] for t in relevant_tables}

        for schema in catalog.schemas:
            schema_tables = [
                t for t in schema.tables if t.table_name in relevant_table_names
            ]

            if schema_tables:
                focused_info += f"Schema: {schema.schema_name}\n"
                for table in schema_tables:
                    focused_info += f"  Table: {table.table_name}\n"
                    for column in table.columns:
                        focused_info += f"    - {column.name}: {column.type}\n"
                    focused_info += "\n"

        return focused_info

    def _create_format_restriction_prompt(self, question: str) -> str:
        """Create prompt for format restriction generation."""
        return f"""
        Analyze this question and determine the expected answer format:

        Question: {question}

        Provide the expected answer format in CSV format. Consider:
        1. What columns should be in the result?
        2. What data types are expected?
        3. How should the result be structured?

        Respond with:
        - Format description (brief explanation)
        - Column names (comma-separated)
        - Data types (comma-separated)
        - Example format (CSV format with headers)

        Format your response as:
        DESCRIPTION: [brief description]
        COLUMNS: [column1,column2,...]
        TYPES: [type1,type2,...]
        EXAMPLE:
        ```csv
        column1,column2
        value1,value2
        ```
        """

    def _parse_format_restriction(self, response: str) -> FormatRestriction:
        """Parse format restriction from LLM response."""
        try:
            # Extract components using regex
            desc_match = re.search(r"DESCRIPTION:\s*(.+)", response)
            cols_match = re.search(r"COLUMNS:\s*(.+)", response)
            types_match = re.search(r"TYPES:\s*(.+)", response)
            example_match = re.search(
                r"EXAMPLE:\s*```csv\n(.+?)\n```", response, re.DOTALL
            )

            description = desc_match.group(1).strip() if desc_match else "CSV format"
            columns = (
                [c.strip() for c in cols_match.group(1).split(",")]
                if cols_match
                else ["result"]
            )
            types = (
                [t.strip() for t in types_match.group(1).split(",")]
                if types_match
                else ["string"]
            )
            example = (
                example_match.group(1).strip() if example_match else "result\nvalue"
            )

            return FormatRestriction(
                format_description=description,
                column_names=columns,
                data_types=types,
                example_format=f"```csv\n{example}\n```",
            )
        except Exception:
            # Return default format on parsing error
            return FormatRestriction(
                format_description="Default CSV format",
                column_names=["result"],
                data_types=["string"],
                example_format="```csv\nresult\nvalue\n```",
            )

    def _generate_exploration_queries(self, question: str, schema: str) -> List[str]:
        """Generate column exploration queries."""
        exploration_prompt = f"""
        Given this question and database schema, generate 5-8 simple SQL queries to explore relevant columns and understand the data:

        Question: {question}
        Schema: {schema}

        Generate queries that:
        1. Explore distinct values in key columns
        2. Check data ranges and distributions
        3. Understand relationships between tables
        4. Sample data from relevant tables

        Each query should be simple, safe, and use LIMIT to avoid large results.
        Return only the SQL queries, one per line.
        """

        try:
            response = self._invoke_llm(exploration_prompt)
            queries = self._extract_sql_queries_from_response(response)
            return queries[:8]  # Limit to 8 queries
        except Exception:
            return []

    def _extract_sql_queries_from_response(self, response: str) -> List[str]:
        """Extract SQL queries from LLM response."""
        queries = []

        # Look for SQL code blocks
        sql_blocks = re.findall(r"```sql\n(.*?)\n```", response, re.DOTALL)
        for block in sql_blocks:
            queries.append(block.strip())

        # Also look for lines that look like SQL
        lines = response.split("\n")
        for line in lines:
            line = line.strip()
            if (
                line.upper().startswith(("SELECT", "WITH"))
                and ";" in line
                and len(line) > 10
            ):
                queries.append(line)

        return queries

    def _extract_columns_from_query(self, query: str) -> List[str]:
        """Extract column names referenced in a query."""
        columns = []

        # Simple regex to find column references
        # This is a simplified approach - a full SQL parser would be better
        column_patterns = [
            r"SELECT\s+(.+?)\s+FROM",
            r"WHERE\s+(\w+)",
            r"GROUP BY\s+(\w+)",
            r"ORDER BY\s+(\w+)",
        ]

        for pattern in column_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                if isinstance(match, str):
                    # Clean up column names
                    cols = [c.strip().strip("\"'`") for c in match.split(",")]
                    columns.extend([c for c in cols if c and c != "*"])

        return list(set(columns))

    def _analyze_exploration_result(self, query: str, result: str) -> Dict[str, Any]:
        """Analyze exploration query result for insights."""
        insights = {}

        try:
            # Extract insights based on query type and result
            if "DISTINCT" in query.upper():
                # Count distinct values
                lines = result.strip().split("\n")
                if len(lines) > 1:  # Has header
                    insights["distinct_values"] = len(lines) - 1

            if "COUNT" in query.upper():
                # Extract count information
                lines = result.strip().split("\n")
                if len(lines) > 1:
                    try:
                        count = int(lines[1])
                        insights["row_count"] = count
                    except ValueError:
                        pass

            # Store sample data
            insights["sample_data"] = result[:500]  # First 500 chars

        except Exception:
            pass

        return insights

    def _create_generation_contexts(
        self,
        question: str,
        schema: str,
        format_restriction: Optional[FormatRestriction],
        column_exploration: Optional[ColumnExplorationResult],
    ) -> List[Dict[str, Any]]:
        """Create multiple generation contexts for parallel processing."""
        base_context = {
            "question": question,
            "schema": schema,
            "format_restriction": format_restriction,
            "column_exploration": column_exploration,
        }

        # Create variations for parallel generation
        contexts = []

        # Context 1: Full information
        contexts.append(
            {**base_context, "approach": "comprehensive", "focus": "accuracy"}
        )

        # Context 2: Simplified approach
        contexts.append({**base_context, "approach": "simplified", "focus": "clarity"})

        # Context 3: Performance-focused
        contexts.append(
            {**base_context, "approach": "optimized", "focus": "performance"}
        )

        return contexts[: self.max_parallel_threads]

    def _generate_sql_candidate(
        self, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate a single SQL candidate."""
        try:
            prompt = self._create_sql_generation_prompt_from_context(context)
            response = self._invoke_llm(prompt)
            sql = self._extract_sql_from_response(response)

            if sql:
                return {
                    "sql": sql,
                    "context": context,
                    "approach": context.get("approach", "default"),
                }
        except Exception:
            pass

        return None

    def _create_sql_generation_prompt_from_context(
        self, context: Dict[str, Any]
    ) -> str:
        """Create SQL generation prompt from context."""
        question = context["question"]
        schema = context["schema"]
        format_restriction = context.get("format_restriction")
        column_exploration = context.get("column_exploration")
        approach = context.get("approach", "comprehensive")

        prompt = f"Generate a SQL query to answer this question:\n\nQuestion: {question}\n\nSchema:\n{schema}\n\n"

        if format_restriction:
            prompt += f"Expected format: {format_restriction.format_description}\n"
            prompt += (
                f"Expected columns: {', '.join(format_restriction.column_names)}\n\n"
            )

        if column_exploration and column_exploration.exploration_results:
            prompt += "Column exploration insights:\n"
            for i, result in enumerate(column_exploration.exploration_results[:3]):
                prompt += f"Exploration {i + 1}: {result[:200]}...\n"
            prompt += "\n"

        if approach == "simplified":
            prompt += "Focus on creating a simple, clear query.\n"
        elif approach == "optimized":
            prompt += "Focus on query performance and efficiency.\n"
        else:
            prompt += "Focus on comprehensive accuracy.\n"

        prompt += "Return only the SQL query without explanations."

        return prompt

    def _refine_sql_candidate(
        self,
        candidate: Dict[str, Any],
        question: str,
        format_restriction: Optional[FormatRestriction],
        column_exploration: Optional[ColumnExplorationResult],
    ) -> Optional[Dict[str, Any]]:
        """Refine a SQL candidate through self-consistency checks."""
        try:
            sql = candidate["sql"]

            # Validate the SQL
            validation_result = self.safety_validator.validate_query(sql)
            if not validation_result.execution_allowed:
                return None

            # Try to execute and check for errors
            try:
                tool = SqlQueryTool()
                result = tool._run(query=sql, datasource=self.get_datasource())

                if result and "Error" not in result:
                    # Check if result matches expected format
                    if self._validate_result_format(result, format_restriction):
                        return {
                            **candidate,
                            "refined": True,
                            "execution_result": result,
                        }
                    else:
                        # Try to fix format issues
                        refined_sql = self._fix_format_issues(sql, format_restriction)
                        if refined_sql != sql:
                            return {**candidate, "sql": refined_sql, "refined": True}

            except Exception:
                # Try error correction
                corrected_sql = self.error_handler.auto_correct_query(
                    sql, str(Exception)
                )
                if corrected_sql:
                    return {**candidate, "sql": corrected_sql, "refined": True}

        except Exception:
            pass

        return None

    def _validate_result_format(
        self, result: str, format_restriction: Optional[FormatRestriction]
    ) -> bool:
        """Validate if result matches expected format."""
        if not format_restriction:
            return True

        try:
            lines = result.strip().split("\n")
            if len(lines) < 2:  # Need at least header and one data row
                return False

            header = lines[0].split(",")
            expected_columns = format_restriction.column_names

            # Check if columns match (allowing for reasonable variations)
            return len(header) == len(expected_columns)

        except Exception:
            return False

    def _fix_format_issues(
        self, sql: str, format_restriction: Optional[FormatRestriction]
    ) -> str:
        """Attempt to fix format issues in SQL."""
        if not format_restriction:
            return sql

        # Simple fixes - in practice, this would be more sophisticated
        # For now, just return the original SQL
        return sql

    def _hash_result(self, result: str) -> str:
        """Create a hash of the result for comparison."""
        import hashlib

        # Normalize the result for comparison
        normalized = result.strip().lower()
        # Remove extra whitespace
        normalized = re.sub(r"\s+", " ", normalized)

        return hashlib.md5(normalized.encode()).hexdigest()

    def get_workflow_state_schema(self) -> type:
        """Return the state schema for this workflow."""
        return MessageState
