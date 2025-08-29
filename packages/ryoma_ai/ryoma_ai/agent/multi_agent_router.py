#!/usr/bin/env python3
"""
Multi-Agent Router for CLI - LLM-Based Intent Classification

Uses LLM inference to intelligently route questions to appropriate specialized agents.
"""

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from ryoma_ai.agent.chat_agent import ChatAgent
from ryoma_ai.agent.factory import AgentFactory
from ryoma_ai.agent.pandas_agent import PandasAgent
from ryoma_ai.agent.python_agent import PythonAgent
from ryoma_ai.agent.sql import SqlAgent
from ryoma_ai.llm.provider import load_model_provider
from ryoma_ai.models.agent import SqlAgentMode


class TaskType(Enum):
    """Task types for intelligent routing."""

    SQL_QUERY = "sql_query"
    PYTHON_CODE = "python_code"
    DATA_ANALYSIS = "data_analysis"
    GENERAL_CHAT = "general_chat"


@dataclass
class TaskClassification:
    """Result of LLM-based task classification."""

    task_type: TaskType
    confidence: float
    reasoning: str
    suggested_agent: str


class LLMTaskRouter:
    """LLM-based intelligent task router."""

    def __init__(self, model: str = "gpt-4o", model_parameters: Optional[Dict] = None):
        self.model = load_model_provider(model, "chat", model_parameters or {})

        # Classification prompt template
        self.classification_prompt = """You are an intelligent task router that determines which specialized agent should handle a user's question.

Available agents and their capabilities:

1. **SQL Agent** - Handles database queries and data retrieval
   - Natural language to SQL conversion
   - Database exploration (show tables, describe schema)
   - Data filtering, aggregation, joins
   - Examples: "Show me all customers", "What are the top 5 products?", "Find orders from last month"

2. **Python Agent** - Executes Python code and scripts
   - Python code execution and debugging
   - Algorithm implementation
   - Script creation and automation
   - Examples: "Write a function to calculate fibonacci", "Create a CSV reader", "Python code to sort a list"

3. **Data Analysis Agent** - Performs statistical analysis and visualization
   - Statistical analysis using pandas/numpy
   - Data visualization with matplotlib/plotly
   - Trend analysis and insights
   - Examples: "Analyze sales trends", "Create a correlation matrix", "Plot distribution of values"

4. **General Chat Agent** - Handles conversations and general questions
   - General questions and explanations
   - Help and guidance
   - Conceptual discussions
   - Examples: "How do databases work?", "Explain machine learning", "What are best practices?"

Analyze the user's question and respond with a JSON object containing:
- "task_type": one of ["sql_query", "python_code", "data_analysis", "general_chat"]
- "confidence": float between 0.0 and 1.0
- "reasoning": brief explanation of your decision

Question: "{question}"

Response (JSON only):"""

    def classify_task(self, user_input: str) -> TaskClassification:
        """Use LLM to classify the task type."""
        # Get LLM classification
        prompt = self.classification_prompt.format(question=user_input)
        response = self.model.invoke(prompt)

        # Extract JSON from response
        response_text = (
            response.content if hasattr(response, "content") else str(response)
        )

        # Try to extract JSON if wrapped in other text
        start_idx = response_text.find("{")
        end_idx = response_text.rfind("}") + 1
        if start_idx != -1 and end_idx != 0:
            json_str = response_text[start_idx:end_idx]
        else:
            json_str = response_text

        result = json.loads(json_str)

        task_type = TaskType(result.get("task_type", "general_chat"))
        confidence = float(result.get("confidence", 0.5))
        reasoning = result.get("reasoning", "LLM classification")

        # Map task type to agent
        agent_mapping = {
            TaskType.SQL_QUERY: "sql",
            TaskType.PYTHON_CODE: "python",
            TaskType.DATA_ANALYSIS: "pandas",
            TaskType.GENERAL_CHAT: "chat",
        }

        return TaskClassification(
            task_type=task_type,
            confidence=confidence,
            reasoning=reasoning,
            suggested_agent=agent_mapping[task_type],
        )


class MultiAgentRouter:
    """Manages multiple agent instances following Claude Code patterns."""

    def __init__(self, model: str, datasource=None, meta_store=None, vector_store=None, **kwargs):
        self.model = model
        self.datasource = datasource
        self.meta_store = meta_store
        self.vector_store = vector_store
        self.model_parameters = kwargs.get("model_parameters")

        # Agent registry (lazy initialization)
        self._agents: Dict[str, Any] = {}
        self.router = LLMTaskRouter(model, self.model_parameters)

        # Shared execution context
        self.execution_context = {
            "conversation_history": [],
            "shared_variables": {},
            "current_datasource": datasource,
        }

    def get_agent(self, agent_type: str, **config_overrides) -> Any:
        """Get or create agent instance (lazy initialization)."""
        cache_key = f"{agent_type}_{hash(str(sorted(config_overrides.items())))}"

        if cache_key not in self._agents:
            self._agents[cache_key] = self._create_agent(agent_type, **config_overrides)

        return self._agents[cache_key]

    def _create_agent(self, agent_type: str, **config_overrides) -> Any:
        """Create agent using factory pattern with unified stores."""
        base_config = {
            "model": self.model,
            "model_parameters": self.model_parameters,
            "datasource": self.datasource,
            "store": self.meta_store,  # Pass unified meta store
            "vector_store": self.vector_store,  # Pass unified vector store
        }
        base_config.update(config_overrides)

        if agent_type == "sql":
            mode = SqlAgentMode(config_overrides.get("sql_mode", "enhanced"))
            return SqlAgent(
                model=base_config["model"],
                mode=mode,
                datasource=base_config["datasource"],
                store=base_config["store"],
                vector_store=base_config["vector_store"],
            )
        elif agent_type == "python":
            return PythonAgent(
                model=base_config["model"],
                model_parameters=base_config.get("model_parameters"),
                store=base_config["store"],
                vector_store=base_config["vector_store"],
            )
        elif agent_type == "pandas":
            return PandasAgent(
                model=base_config["model"],
                model_parameters=base_config.get("model_parameters"),
                datasource=base_config["datasource"],
                store=base_config["store"],
                vector_store=base_config["vector_store"],
            )
        elif agent_type == "chat":
            return ChatAgent(
                model=base_config["model"],
                model_parameters=base_config.get("model_parameters"),
                datasource=base_config["datasource"],
                store=base_config["store"],
                vector_store=base_config["vector_store"],
            )
        else:
            # Fallback using AgentFactory
            return AgentFactory.create_agent(agent_type, **base_config)

    def route_and_execute(
        self, user_input: str, **config_overrides
    ) -> tuple[Any, TaskClassification, Any]:
        """Route question to appropriate agent and return results."""
        # Classify the task
        classification = self.router.classify_task(user_input)

        # Get appropriate agent
        agent = self.get_agent(classification.suggested_agent, **config_overrides)

        # Update execution context
        self.execution_context["conversation_history"].append(
            {
                "input": user_input,
                "classification": classification,
                "agent_type": classification.suggested_agent,
            }
        )

        return agent, classification, self.execution_context

    def get_capabilities(self) -> Dict[str, Dict[str, List[str]]]:
        """Return capabilities for all agent types."""
        return {
            "SQL Agent": {
                "capabilities": [
                    "Natural language to SQL conversion",
                    "Database schema exploration",
                    "Data retrieval and filtering",
                    "Aggregations and joins",
                    "Database operations with approval workflow",
                ],
                "examples": [
                    "Show me all customers from New York",
                    "What are the top 5 selling products?",
                    "Find orders placed in the last 30 days",
                ],
            },
            "Python Agent": {
                "capabilities": [
                    "Python script execution",
                    "Function creation and testing",
                    "Algorithm implementation",
                    "Data processing scripts",
                ],
                "examples": [
                    "Write a function to calculate fibonacci numbers",
                    "Create a script to read CSV files",
                    "Python code to send HTTP requests",
                ],
            },
            "Data Analysis Agent": {
                "capabilities": [
                    "Statistical analysis with pandas",
                    "Data visualization",
                    "Trend analysis",
                    "Data exploration and insights",
                ],
                "examples": [
                    "Analyze sales trends over time",
                    "Create a correlation matrix",
                    "Plot the distribution of customer ages",
                ],
            },
            "Chat Agent": {
                "capabilities": [
                    "General questions and conversations",
                    "Explanations and help",
                    "Information retrieval",
                    "Context-aware responses",
                ],
                "examples": [
                    "What can you help me with?",
                    "Explain machine learning concepts",
                    "Best practices for data analysis",
                ],
            },
        }

    def switch_agent_context(
        self, from_agent: str, to_agent: str, context_data: Dict = None
    ):
        """Switch between agents while preserving relevant context."""
        if context_data:
            self.execution_context["shared_variables"].update(context_data)

        # Agent-specific context switching logic can be added here
        # For example, passing SQL results to pandas agent for analysis

    def get_current_stats(self) -> Dict[str, Any]:
        """Get statistics about agent usage."""
        history = self.execution_context["conversation_history"]
        agent_counts = {}

        for entry in history:
            agent_type = entry["agent_type"]
            agent_counts[agent_type] = agent_counts.get(agent_type, 0) + 1

        return {
            "total_queries": len(history),
            "agent_usage": agent_counts,
            "active_agents": list(self._agents.keys()),
        }
