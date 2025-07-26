from typing import Dict, List, Optional, Any, Tuple
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from ryoma_ai.agent.workflow import WorkflowAgent
from ryoma_ai.agent.internals.schema_linking_agent import SchemaLinkingAgent
from ryoma_ai.agent.internals.query_planner import QueryPlannerAgent, QueryComplexity
from ryoma_ai.agent.internals.sql_error_handler import SqlErrorHandler
from ryoma_ai.agent.internals.sql_safety_validator import SqlSafetyValidator, SafetyLevel
from ryoma_ai.states import SqlAgentState
from ryoma_ai.tool.sql_tool import (
    SqlQueryTool, CreateTableTool, QueryProfileTool,
    SchemaAnalysisTool, QueryValidationTool, TableSelectionTool,
    QueryOptimizationTool, QueryExplanationTool
)
from ryoma_ai.datasource.sql import SqlDataSource


class EnhancedSqlAgent(WorkflowAgent):
    """
    Enhanced SQL Agent with multi-step reasoning, advanced error handling,
    safety validation, and intelligent schema linking.
    """

    def __init__(
        self,
        model: str,
        model_parameters: Optional[Dict] = None,
        datasource: Optional[SqlDataSource] = None,
        safety_config: Optional[Dict] = None,
        **kwargs,
    ):
        # Initialize specialized agents
        self.schema_agent = SchemaLinkingAgent(
            model=model,
            model_parameters=model_parameters,
            datasource=datasource
        )

        self.query_planner = QueryPlannerAgent(
            model=model,
            model_parameters=model_parameters,
            datasource=datasource
        )

        self.error_handler = SqlErrorHandler(datasource=datasource)
        self.safety_validator = SqlSafetyValidator(
            datasource=datasource,
            safety_config=safety_config
        )

        # Initialize enhanced tools
        tools = [
            SqlQueryTool(),
            CreateTableTool(),
            QueryProfileTool(),
            SchemaAnalysisTool(),
            QueryValidationTool(),
            TableSelectionTool(),
            QueryOptimizationTool(),
            QueryExplanationTool(),
        ]

        super().__init__(
            model=model,
            model_parameters=model_parameters,
            tools=tools,
            datasource=datasource,
            **kwargs,
        )

    def _create_workflow(self) -> StateGraph:
        """Create the enhanced SQL agent workflow with multi-step reasoning."""
        workflow = StateGraph(SqlAgentState)

        # Add nodes for each step
        workflow.add_node("analyze_question", self._analyze_question)
        workflow.add_node("schema_linking", self._schema_linking)
        workflow.add_node("query_planning", self._query_planning)
        workflow.add_node("generate_sql", self._generate_sql)
        workflow.add_node("validate_safety", self._validate_safety)
        workflow.add_node("execute_query", self._execute_query)
        workflow.add_node("handle_error", self._handle_error)
        workflow.add_node("format_response", self._format_response)

        # Define the workflow edges
        workflow.set_entry_point("analyze_question")

        workflow.add_edge("analyze_question", "schema_linking")
        workflow.add_edge("schema_linking", "query_planning")
        workflow.add_edge("query_planning", "generate_sql")
        workflow.add_edge("generate_sql", "validate_safety")

        # Conditional edges for safety validation
        workflow.add_conditional_edges(
            "validate_safety",
            self._should_execute_query,
            {
                "execute": "execute_query",
                "reject": "format_response"
            }
        )

        # Conditional edges for query execution
        workflow.add_conditional_edges(
            "execute_query",
            self._check_execution_result,
            {
                "success": "format_response",
                "error": "handle_error",
                "retry": "generate_sql"
            }
        )

        workflow.add_conditional_edges(
            "handle_error",
            self._should_retry,
            {
                "retry": "generate_sql",
                "give_up": "format_response"
            }
        )

        workflow.add_edge("format_response", END)

        return workflow

    def _analyze_question(self, state: SqlAgentState) -> SqlAgentState:
        """Analyze the user's question to understand intent and complexity."""
        question = state["original_question"]

        # Use the query planner to analyze complexity
        complexity = self.query_planner._analyze_question_complexity(question)

        state["current_step"] = "question_analysis"
        state["messages"].append(AIMessage(
            content=f"Analyzing question complexity: {complexity.value}"
        ))

        return state

    def _schema_linking(self, state: SqlAgentState) -> SqlAgentState:
        """Perform intelligent schema linking to find relevant tables."""
        question = state["original_question"]

        try:
            # Get schema analysis
            schema_analysis = self.schema_agent.analyze_schema_relationships(question)

            # Get table suggestions
            table_suggestions = self.schema_agent.suggest_table_selection(question)

            state["schema_analysis"] = schema_analysis
            state["relevant_tables"] = table_suggestions
            state["current_step"] = "schema_linking"

            tables_info = ", ".join([
                f"{t['schema']}.{t['table']} (score: {t['score']:.2f})"
                for t in table_suggestions[:3]
            ])

            state["messages"].append(AIMessage(
                content=f"Identified relevant tables: {tables_info}"
            ))

        except Exception as e:
            state["messages"].append(AIMessage(
                content=f"Schema linking failed: {str(e)}"
            ))
            state["relevant_tables"] = []

        return state

    def _query_planning(self, state: SqlAgentState) -> SqlAgentState:
        """Create a query execution plan."""
        question = state["original_question"]
        context = {
            "relevant_tables": state.get("relevant_tables", []),
            "schema_analysis": state.get("schema_analysis", {})
        }

        try:
            query_plan = self.query_planner.create_query_plan(question, context)

            state["query_plan"] = {
                "complexity": query_plan.complexity.value,
                "steps": [
                    {
                        "id": step.step_id,
                        "description": step.description,
                        "depends_on": step.depends_on
                    }
                    for step in query_plan.steps
                ],
                "optimization_notes": query_plan.optimization_notes
            }
            state["current_step"] = "query_planning"

            state["messages"].append(AIMessage(
                content=f"Created query plan with {len(query_plan.steps)} steps"
            ))

        except Exception as e:
            state["messages"].append(AIMessage(
                content=f"Query planning failed: {str(e)}"
            ))

        return state

    def _generate_sql(self, state: SqlAgentState) -> SqlAgentState:
        """Generate SQL query based on the analysis and planning."""
        question = state["original_question"]
        context = {
            "relevant_tables": state.get("relevant_tables", []),
            "query_plan": state.get("query_plan", {}),
            "retry_count": state.get("retry_count", 0)
        }

        # Use the chat agent to generate SQL
        prompt = self._create_sql_generation_prompt(question, context)

        try:
            response = self._invoke_llm(prompt)
            sql_query = self._extract_sql_from_response(response)

            state["generated_sql"] = sql_query
            state["current_step"] = "sql_generation"

            state["messages"].append(AIMessage(
                content=f"Generated SQL query: {sql_query[:100]}..."
            ))

        except Exception as e:
            state["messages"].append(AIMessage(
                content=f"SQL generation failed: {str(e)}"
            ))

        return state

    def _validate_safety(self, state: SqlAgentState) -> SqlAgentState:
        """Validate the generated SQL for safety and security."""
        sql_query = state.get("generated_sql", "")

        if not sql_query:
            state["safety_check"] = {"is_safe": False, "reason": "No SQL query generated"}
            return state

        try:
            validation_result = self.safety_validator.validate_query(sql_query)

            state["safety_check"] = {
                "is_safe": validation_result.is_safe,
                "safety_level": validation_result.safety_level.value,
                "execution_allowed": validation_result.execution_allowed,
                "violations": [
                    {
                        "rule": v.rule.value,
                        "severity": v.severity.value,
                        "message": v.message
                    }
                    for v in validation_result.violations
                ],
                "sanitized_query": validation_result.sanitized_query
            }
            state["current_step"] = "safety_validation"

            if validation_result.execution_allowed:
                state["messages"].append(AIMessage(
                    content=f"Safety validation passed: {validation_result.safety_level.value}"
                ))
            else:
                state["messages"].append(AIMessage(
                    content=f"Safety validation failed: {len(validation_result.violations)} violations"
                ))

        except Exception as e:
            state["safety_check"] = {"is_safe": False, "reason": f"Validation error: {str(e)}"}
            state["messages"].append(AIMessage(
                content=f"Safety validation error: {str(e)}"
            ))

        return state

    def _execute_query(self, state: SqlAgentState) -> SqlAgentState:
        """Execute the validated SQL query."""
        sql_query = state.get("generated_sql", "")

        if not sql_query:
            state["execution_result"] = "No SQL query to execute"
            return state

        try:
            # Use the SQL query tool to execute
            tool = SqlQueryTool()
            result = tool._run(
                query=sql_query,
                datasource=self.get_datasource()
            )

            state["execution_result"] = result
            state["current_step"] = "query_execution"

            state["messages"].append(AIMessage(
                content="Query executed successfully"
            ))

        except Exception as e:
            state["error_info"] = {
                "error_message": str(e),
                "sql_query": sql_query,
                "step": "execution"
            }
            state["messages"].append(AIMessage(
                content=f"Query execution failed: {str(e)}"
            ))

        return state

    def _handle_error(self, state: SqlAgentState) -> SqlAgentState:
        """Handle errors with intelligent recovery strategies."""
        error_info = state.get("error_info", {})

        if not error_info:
            return state

        try:
            sql_error = self.error_handler.analyze_error(
                error_info["error_message"],
                error_info["sql_query"]
            )

            recovery_strategies = self.error_handler.suggest_recovery_strategies(sql_error)

            # Try automatic correction
            corrected_sql = self.error_handler.auto_correct_query(
                error_info["sql_query"],
                error_info["error_message"]
            )

            if corrected_sql:
                state["generated_sql"] = corrected_sql
                state["messages"].append(AIMessage(
                    content="Applied automatic error correction"
                ))
            else:
                # Provide manual suggestions
                suggestions = [s.description for s in recovery_strategies[:3]]
                state["messages"].append(AIMessage(
                    content=f"Error recovery suggestions: {'; '.join(suggestions)}"
                ))

            state["current_step"] = "error_handling"

        except Exception as e:
            state["messages"].append(AIMessage(
                content=f"Error handling failed: {str(e)}"
            ))

        return state

    def _format_response(self, state: SqlAgentState) -> SqlAgentState:
        """Format the final response to the user."""
        execution_result = state.get("execution_result")
        safety_check = state.get("safety_check", {})
        error_info = state.get("error_info")

        if execution_result and not error_info:
            # Successful execution
            final_answer = f"Query executed successfully:\n\n{execution_result}"
        elif not safety_check.get("execution_allowed", True):
            # Safety violation
            violations = safety_check.get("violations", [])
            violation_messages = [v["message"] for v in violations]
            final_answer = f"Query blocked for safety reasons:\n" + "\n".join(violation_messages)
        elif error_info:
            # Error occurred
            final_answer = f"Query failed with error: {error_info['error_message']}"
        else:
            final_answer = "Unable to process the query"

        state["final_answer"] = final_answer
        state["current_step"] = "completed"

        state["messages"].append(AIMessage(content=final_answer))

        return state

    def _should_execute_query(self, state: SqlAgentState) -> str:
        """Determine if the query should be executed based on safety validation."""
        safety_check = state.get("safety_check", {})
        return "execute" if safety_check.get("execution_allowed", False) else "reject"

    def _check_execution_result(self, state: SqlAgentState) -> str:
        """Check the result of query execution."""
        if state.get("error_info"):
            return "error"
        elif state.get("execution_result"):
            return "success"
        else:
            return "retry"

    def _should_retry(self, state: SqlAgentState) -> str:
        """Determine if we should retry after an error."""
        retry_count = state.get("retry_count", 0)
        max_retries = state.get("max_retries", 3)

        if retry_count < max_retries:
            state["retry_count"] = retry_count + 1
            return "retry"
        else:
            return "give_up"

    def _create_sql_generation_prompt(self, question: str, context: Dict) -> str:
        """Create a prompt for SQL generation."""
        prompt = f"Generate a SQL query to answer: {question}\n\n"

        if context.get("relevant_tables"):
            tables = context["relevant_tables"][:3]
            prompt += "Relevant tables:\n"
            for table in tables:
                prompt += f"- {table['schema']}.{table['table']}: {table.get('reasoning', '')}\n"
            prompt += "\n"

        if context.get("retry_count", 0) > 0:
            prompt += f"This is retry attempt {context['retry_count']}. Please fix any previous issues.\n\n"

        prompt += "Generate only the SQL query, no explanations."

        return prompt

    def _extract_sql_from_response(self, response: str) -> str:
        """Extract SQL query from LLM response."""
        # Simple extraction - in practice, you might use more sophisticated parsing
        lines = response.strip().split('\n')
        sql_lines = []

        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('--'):
                sql_lines.append(line)

        return ' '.join(sql_lines)

    def _invoke_llm(self, prompt: str) -> str:
        """Invoke the language model with a prompt."""
        # This would use the actual LLM invocation
        # For now, return a placeholder
        return "SELECT * FROM table WHERE condition;"

    def get_workflow_state_schema(self) -> type:
        """Return the state schema for this workflow."""
        return SqlAgentState
