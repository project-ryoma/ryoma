import logging
from typing import Dict, List, Optional, Any, Tuple
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph.state import CompiledStateGraph

from ryoma_ai.agent.workflow import WorkflowAgent
from ryoma_ai.agent.internals.schema_linking_agent import SchemaLinkingAgent
from ryoma_ai.agent.internals.query_planner import QueryPlannerAgent, QueryComplexity
from ryoma_ai.agent.internals.sql_error_handler import SqlErrorHandler
from ryoma_ai.agent.internals.sql_safety_validator import SqlSafetyValidator, SafetyLevel
from ryoma_ai.states import MessageState
from ryoma_ai.tool.sql_tool import (
    SqlQueryTool, CreateTableTool, QueryProfileTool,
    SchemaAnalysisTool, QueryValidationTool,
    QueryOptimizationTool, QueryExplanationTool
)
from ryoma_ai.datasource.sql import SqlDataSource


logger = logging.getLogger(__name__)

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
        # Initialize enhanced tools
        tools = [
            SqlQueryTool(),
            CreateTableTool(),
            QueryProfileTool(),
            SchemaAnalysisTool(),
            QueryValidationTool(),
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

        # Initialize specialized agents AFTER parent constructor so self.store exists
        self.schema_agent = SchemaLinkingAgent(
            model=model,
            model_parameters=model_parameters,
            datasource=datasource,
            store=self.store  # Pass store so it can access datasource dynamically
        )

        self.query_planner = QueryPlannerAgent(
            model=model,
            model_parameters=model_parameters,
            datasource=datasource,
            store=self.store  # Pass store so it can access datasource dynamically
        )

        self.error_handler = SqlErrorHandler(datasource=datasource)
        self.safety_validator = SqlSafetyValidator(
            datasource=datasource,
            safety_config=safety_config
        )

    def _build_workflow(self,
                        graph: StateGraph) -> CompiledStateGraph:
        """Create the enhanced SQL agent workflow with multi-step reasoning."""
        workflow = StateGraph(MessageState)

        # Add nodes for each step
        workflow.add_node("initialize_state", self._initialize_state)
        workflow.add_node("analyze_question", self._analyze_question)
        workflow.add_node("schema_linking", self._schema_linking)
        workflow.add_node("query_planning", self._query_planning)
        workflow.add_node("generate_sql", self._generate_sql)
        workflow.add_node("validate_safety", self._validate_safety)
        workflow.add_node("execute_query", self._execute_query)
        workflow.add_node("handle_error", self._handle_error)
        workflow.add_node("format_response", self._format_response)

        # Define the workflow edges
        workflow.set_entry_point("initialize_state")
        workflow.add_edge("initialize_state", "analyze_question")

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

        return workflow.compile(
            checkpointer=self.memory,
            store=self.store
        )

    def _initialize_state(self, state) -> MessageState:
        """Initialize the MessageState with proper defaults and extract question from messages."""
        # Get the messages from input state
        messages = state.get("messages", [])

        # Extract the question from the last human message
        original_question = ""
        if messages:
            human_messages = [msg for msg in messages if isinstance(msg, HumanMessage)]
            if human_messages:
                original_question = human_messages[-1].content

        # Create a properly initialized MessageState
        initialized_state = {
            "messages": messages,
            "original_question": original_question,
            "current_step": "initialized",
            "schema_analysis": None,
            "relevant_tables": None,
            "query_plan": None,
            "generated_sql": None,
            "validation_result": None,
            "execution_result": None,
            "error_info": None,
            "safety_check": None,
            "final_answer": None,
            "retry_count": 0,
            "max_retries": 3
        }

        return initialized_state

    def _analyze_question(self,
                          state: MessageState) -> MessageState:
        """Analyze the user's question to understand intent and complexity."""
        # Extract question from messages if original_question is empty
        logger.debug("Step 1: Start analyzing question: %s", state["original_question"])
        question = state.get("original_question", "")
        if not question and state.get("messages"):
            # Find the last human message
            human_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
            if human_messages:
                question = human_messages[-1].content
                state["original_question"] = question

        # Use the query planner to analyze complexity
        complexity = self.query_planner._analyze_question_complexity(question)

        state["current_step"] = "question_analysis"
        state["messages"].append(AIMessage(
            content=f"Analyzing question complexity: {complexity.value}"
        ))

        return state

    def _schema_linking(self,
                        state: MessageState) -> MessageState:
        """Perform intelligent schema linking to find relevant tables."""
        question = state["original_question"]
        logger.debug("Step 2: Start linking schema for question: %s", question)

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

    def _query_planning(self,
                        state: MessageState) -> MessageState:
        """Create a query execution plan."""
        question = state["original_question"]
        logger.debug("Step 3: Creating query plan for question: %s", question)
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

    def _generate_sql(self,
                      state: MessageState) -> MessageState:
        """Generate SQL query based on the analysis and planning."""
        question = state["original_question"]
        logger.debug("Step 4: Generating SQL for question: %s", question)
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

    def _validate_safety(self,
                         state: MessageState) -> MessageState:
        """Validate the generated SQL for safety and security."""
        sql_query = state.get("generated_sql", "")
        logger.debug("Step 5: Validating safety of SQL query: %s", sql_query)

        # Extract SQL content from message object if needed
        if hasattr(sql_query, 'content'):
            sql_content = sql_query.content
            print('here1')
        elif isinstance(sql_query, str):
            sql_content = sql_query
            print('here2')
        else:
            sql_content = str(sql_query)
            print('here3')

        print("SQL Content for Safety Validation:", sql_content)  # Debug print

        if not sql_content:
            state["safety_check"] = {"is_safe": False, "reason": "No SQL query generated"}
            return state

        try:
            validation_result = self.safety_validator.validate_query(sql_content)
            logger.debug("Safety validation result: %s", validation_result)

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

    def _execute_query(self,
                       state: MessageState) -> MessageState:
        """Execute the validated SQL query."""
        sql_query = state.get("generated_sql", "")
        print("SQL Query for Execution:", sql_query)  # Debug print
        logger.debug("Step 6: Executing SQL query: %s", sql_query)

        if not sql_query:
            state["execution_result"] = "No SQL query to execute"
            return state

        try:
            # Use the SQL query tool to execute
            tool = SqlQueryTool()
            result = tool._run(
                query=sql_query,
                store=self.store
            )
            print("result of query execution:", result)

            if result.is_success:
                state["execution_result"] = result.data
                state["current_step"] = "query_execution"

                state["messages"].append(AIMessage(
                    content=f"Query executed successfully ({result.row_count} rows returned)"
                ))
            else:
                # Handle query execution error
                state["error_info"] = {
                    "error_message": result.error_message,
                    "error_code": result.error_code,
                    "error_type": result.error_type,
                    "sql_query": sql_query,
                    "step": "execution"
                }
                state["messages"].append(AIMessage(
                    content=f"Query execution failed: {result.error_message}"
                ))
                return state

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

    def _handle_error(self,
                      state: MessageState) -> MessageState:
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
                error_info.get("error_message", "")
            )

            if corrected_sql:
                state["generated_sql"] = corrected_sql
                state["messages"].append(AIMessage(
                    content="Applied automatic error correction"
                ))
                # Clear error info since we're retrying with corrected SQL
                state["error_info"] = None
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

    def _format_response(self,
                         state: MessageState) -> MessageState:
        """Format the final response to the user."""
        execution_result = state.get("execution_result")
        safety_check = state.get("safety_check", {})
        error_info = state.get("error_info")
        logger.debug("Step 7: Formatting final response")

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

    def _should_execute_query(self,
                              state: MessageState) -> str:
        """Determine if the query should be executed based on safety validation."""
        safety_check = state.get("safety_check", {})
        return "execute" if safety_check.get("execution_allowed", False) else "reject"

    def _check_execution_result(self,
                                state: MessageState) -> str:
        """Check the result of query execution."""
        if state.get("error_info"):
            return "error"
        elif state.get("execution_result"):
            return "success"
        else:
            return "retry"

    def _should_retry(self,
                      state: MessageState) -> str:
        """Determine if we should retry after an error."""
        retry_count = state.get("retry_count", 0)
        max_retries = state.get("max_retries", 3)

        if retry_count < max_retries:
            state["retry_count"] = retry_count + 1
            return "retry"
        else:
            return "give_up"

    def _create_sql_generation_prompt(self,
                                      question: str,
                                      context: Dict) -> str:
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

    def _extract_sql_from_response(self,
                                   response: str) -> str:
        """Extract SQL query from LLM response."""
        # Simple extraction - in practice, you might use more sophisticated parsing
        lines = response.strip().split('\n')
        sql_lines = []

        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('--'):
                sql_lines.append(line)

        return ' '.join(sql_lines)

    def _invoke_llm(self,
                    prompt: str) -> str:
        message = self.model.invoke(prompt)
        if isinstance(message, list) and message:
            message = message[0]
        if isinstance(message, BaseMessage):
            message = message.content
        print("here, llm message:", message)
        return str(message)

    def get_workflow_state_schema(self) -> type:
        """Return the state schema for this workflow."""
        return MessageState
