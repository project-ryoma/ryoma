#!/usr/bin/env python3
"""
Unit tests for multi-agent router system.

Tests the LLM-based task classification, agent routing, and multi-agent management
functionality without requiring actual API calls.
"""

import json
import unittest
from typing import Any, Dict
from unittest.mock import Mock, patch

from ryoma_ai.agent.multi_agent_router import (
    LLMTaskRouter,
    MultiAgentRouter,
    TaskClassification,
    TaskType,
)


class MockModel:
    """Mock LLM model for testing without API keys."""

    def __init__(self, responses: Dict[str, str] = None):
        """Initialize with predefined responses for different inputs."""
        self.responses = responses or {}
        self.call_count = 0
        self.last_prompt = None

        # Add default responses for test cases that should be SQL queries
        self.default_sql_responses = {
            "show me all customers from new york": '{"task_type": "sql_query", "confidence": 0.9, "reasoning": "Database query for customer data"}',
            "what are the top 5 selling products?": '{"task_type": "sql_query", "confidence": 0.9, "reasoning": "Database query for product rankings"}',
            "find orders placed in the last 30 days": '{"task_type": "sql_query", "confidence": 0.9, "reasoning": "Database query for recent orders"}',
            "show me the data in artist table": '{"task_type": "sql_query", "confidence": 0.9, "reasoning": "Database table data retrieval"}',
        }

    def invoke(self, prompt: str):
        """Mock invoke method that returns predefined responses."""
        self.call_count += 1
        self.last_prompt = prompt

        class MockResponse:
            def __init__(self, content):
                self.content = content

        # Extract question from prompt to determine response
        question_line = ""
        for line in prompt.split("\n"):
            if "Question:" in line:
                question_line = line.replace("Question:", "").strip().strip('"').lower()
                break

        # Use predefined response if available
        if question_line in self.responses:
            return MockResponse(self.responses[question_line])

        # Check default SQL responses
        if question_line in self.default_sql_responses:
            return MockResponse(self.default_sql_responses[question_line])

        # Default classification logic
        if any(
            word in question_line
            for word in [
                "show",
                "find",
                "select",
                "table",
                "database",
                "data",
                "artist",
                "customers",
            ]
        ):
            response = '{"task_type": "sql_query", "confidence": 0.9, "reasoning": "Contains SQL/database keywords"}'
        elif any(
            word in question_line
            for word in ["write", "function", "code", "script", "python"]
        ):
            response = '{"task_type": "python_code", "confidence": 0.8, "reasoning": "Contains programming keywords"}'
        elif any(
            word in question_line
            for word in ["analyze", "correlation", "plot", "trends"]
        ):
            response = '{"task_type": "data_analysis", "confidence": 0.85, "reasoning": "Contains data analysis keywords"}'
        else:
            response = '{"task_type": "general_chat", "confidence": 0.7, "reasoning": "General conversation"}'

        return MockResponse(response)


class TestTaskType(unittest.TestCase):
    """Test TaskType enum."""

    def test_task_type_values(self):
        """Test that TaskType enum has expected values."""
        expected_types = {"sql_query", "python_code", "data_analysis", "general_chat"}
        actual_types = {task_type.value for task_type in TaskType}
        self.assertEqual(expected_types, actual_types)

    def test_task_type_creation(self):
        """Test TaskType enum creation."""
        self.assertEqual(TaskType.SQL_QUERY.value, "sql_query")
        self.assertEqual(TaskType.PYTHON_CODE.value, "python_code")
        self.assertEqual(TaskType.DATA_ANALYSIS.value, "data_analysis")
        self.assertEqual(TaskType.GENERAL_CHAT.value, "general_chat")


class TestTaskClassification(unittest.TestCase):
    """Test TaskClassification dataclass."""

    def test_task_classification_creation(self):
        """Test TaskClassification creation and attributes."""
        classification = TaskClassification(
            task_type=TaskType.SQL_QUERY,
            confidence=0.9,
            reasoning="Test reasoning",
            suggested_agent="sql",
        )

        self.assertEqual(classification.task_type, TaskType.SQL_QUERY)
        self.assertEqual(classification.confidence, 0.9)
        self.assertEqual(classification.reasoning, "Test reasoning")
        self.assertEqual(classification.suggested_agent, "sql")


class TestLLMTaskRouter(unittest.TestCase):
    """Test LLM-based task router."""

    def setUp(self):
        """Set up test fixtures."""
        self.router = LLMTaskRouter()
        self.mock_model = MockModel()
        self.router.model = self.mock_model

    def test_classify_sql_query(self):
        """Test classification of SQL queries."""
        test_cases = [
            "Show me all customers from New York",
            "What are the top 5 selling products?",
            "Find orders placed in the last 30 days",
            "show me the data in artist table",
        ]

        for question in test_cases:
            with self.subTest(question=question):
                classification = self.router.classify_task(question)
                self.assertEqual(classification.task_type, TaskType.SQL_QUERY)
                self.assertEqual(classification.suggested_agent, "sql")
                self.assertGreater(classification.confidence, 0.0)

    def test_classify_python_code(self):
        """Test classification of Python code requests."""
        test_cases = [
            "Write a function to calculate fibonacci numbers",
            "Create a script to read CSV files",
            "Python code to send HTTP requests",
        ]

        for question in test_cases:
            with self.subTest(question=question):
                classification = self.router.classify_task(question)
                self.assertEqual(classification.task_type, TaskType.PYTHON_CODE)
                self.assertEqual(classification.suggested_agent, "python")
                self.assertGreater(classification.confidence, 0.0)

    def test_classify_data_analysis(self):
        """Test classification of data analysis requests."""
        test_cases = [
            "Analyze sales trends over time",
            "Create a correlation matrix",
            "Plot the distribution of customer ages",
        ]

        for question in test_cases:
            with self.subTest(question=question):
                classification = self.router.classify_task(question)
                self.assertEqual(classification.task_type, TaskType.DATA_ANALYSIS)
                self.assertEqual(classification.suggested_agent, "pandas")
                self.assertGreater(classification.confidence, 0.0)

    def test_classify_general_chat(self):
        """Test classification of general chat requests."""
        test_cases = [
            "What can you help me with?",
            "Explain machine learning concepts",
            "Best practices for data analysis",
        ]

        for question in test_cases:
            with self.subTest(question=question):
                classification = self.router.classify_task(question)
                self.assertEqual(classification.task_type, TaskType.GENERAL_CHAT)
                self.assertEqual(classification.suggested_agent, "chat")
                self.assertGreater(classification.confidence, 0.0)

    def test_custom_responses(self):
        """Test router with custom predefined responses."""
        custom_responses = {
            "test question": '{"task_type": "sql_query", "confidence": 0.95, "reasoning": "Custom test response"}'
        }

        router = LLMTaskRouter()
        router.model = MockModel(custom_responses)

        classification = router.classify_task("test question")
        self.assertEqual(classification.task_type, TaskType.SQL_QUERY)
        self.assertEqual(classification.confidence, 0.95)
        self.assertEqual(classification.reasoning, "Custom test response")

    def test_invalid_json_handling(self):
        """Test handling of invalid JSON responses."""
        invalid_responses = {"test": "invalid json response"}

        router = LLMTaskRouter()
        router.model = MockModel(invalid_responses)

        # Should raise an exception due to invalid JSON
        with self.assertRaises(json.JSONDecodeError):
            router.classify_task("test")

    def test_prompt_formatting(self):
        """Test that prompts are formatted correctly."""
        question = "test question"
        self.router.classify_task(question)

        # Check that the prompt contains the question
        self.assertIn(question, self.mock_model.last_prompt)
        # Check that the prompt contains instructions
        self.assertIn("JSON", self.mock_model.last_prompt)
        self.assertIn("task_type", self.mock_model.last_prompt)


class TestMultiAgentManager(unittest.TestCase):
    """Test multi-agent manager."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = MultiAgentRouter(model="test-model")
        # Mock the router to avoid actual LLM calls
        self.manager.router = Mock()

    def test_manager_initialization(self):
        """Test manager initialization."""
        self.assertEqual(self.manager.model, "test-model")
        self.assertIsNone(self.manager.datasource)
        self.assertIsInstance(self.manager.execution_context, dict)
        self.assertIn("conversation_history", self.manager.execution_context)
        self.assertIn("shared_variables", self.manager.execution_context)
        self.assertIn("current_datasource", self.manager.execution_context)

    def test_get_capabilities(self):
        """Test getting agent capabilities."""
        capabilities = self.manager.get_capabilities()

        # Check that all expected agent types are present
        expected_agents = {
            "SQL Agent",
            "Python Agent",
            "Data Analysis Agent",
            "Chat Agent",
        }
        self.assertEqual(set(capabilities.keys()), expected_agents)

        # Check that each agent has required fields
        for agent_name, agent_info in capabilities.items():
            with self.subTest(agent=agent_name):
                self.assertIn("capabilities", agent_info)
                self.assertIn("examples", agent_info)
                self.assertIsInstance(agent_info["capabilities"], list)
                self.assertIsInstance(agent_info["examples"], list)
                self.assertGreater(len(agent_info["capabilities"]), 0)
                self.assertGreater(len(agent_info["examples"]), 0)

    def test_execution_context(self):
        """Test execution context management."""
        context = self.manager.execution_context

        # Test initial state
        self.assertEqual(len(context["conversation_history"]), 0)
        self.assertEqual(len(context["shared_variables"]), 0)
        self.assertIsNone(context["current_datasource"])

        # Test context switching
        test_data = {"key": "value"}
        self.manager.switch_agent_context("sql", "python", test_data)
        self.assertEqual(context["shared_variables"]["key"], "value")

    def test_get_current_stats(self):
        """Test getting usage statistics."""
        stats = self.manager.get_current_stats()

        # Check initial stats
        self.assertEqual(stats["total_queries"], 0)
        self.assertEqual(stats["agent_usage"], {})
        self.assertEqual(stats["active_agents"], [])

        # Simulate some conversation history
        self.manager.execution_context["conversation_history"] = [
            {"agent_type": "sql"},
            {"agent_type": "python"},
            {"agent_type": "sql"},
        ]

        stats = self.manager.get_current_stats()
        self.assertEqual(stats["total_queries"], 3)
        self.assertEqual(stats["agent_usage"]["sql"], 2)
        self.assertEqual(stats["agent_usage"]["python"], 1)

    @patch("ryoma_ai.agent.multi_agent_router.SqlAgent")
    @patch("ryoma_ai.agent.multi_agent_router.PythonAgent")
    def test_agent_creation(self, mock_python_agent, mock_sql_agent):
        """Test agent creation with mocked dependencies."""
        # Test SQL agent creation
        sql_agent = self.manager._create_agent("sql")
        mock_sql_agent.assert_called_once()

        # Test Python agent creation
        python_agent = self.manager._create_agent("python")
        mock_python_agent.assert_called_once()

    def test_agent_caching(self):
        """Test that agents are cached properly."""
        with patch.object(self.manager, "_create_agent") as mock_create:
            # Create different mock agents for each call
            mock_agent1 = Mock()
            mock_agent2 = Mock()
            mock_create.side_effect = [mock_agent1, mock_agent2]

            # First call should create agent
            agent1 = self.manager.get_agent("sql")
            self.assertEqual(mock_create.call_count, 1)

            # Second call should use cached agent
            agent2 = self.manager.get_agent("sql")
            self.assertEqual(mock_create.call_count, 1)
            self.assertIs(agent1, agent2)

            # Different config should create new agent
            agent3 = self.manager.get_agent("sql", sql_mode="basic")
            self.assertEqual(mock_create.call_count, 2)
            self.assertIsNot(agent1, agent3)
            self.assertIs(agent3, mock_agent2)


class TestMultiAgentIntegration(unittest.TestCase):
    """Integration tests for multi-agent system."""

    def setUp(self):
        """Set up integration test fixtures."""
        self.manager = MultiAgentRouter(model="test-model")
        self.manager.router.model = MockModel()

    def test_route_and_execute_workflow(self):
        """Test the complete routing workflow."""
        # Mock the router classification
        mock_classification = TaskClassification(
            task_type=TaskType.SQL_QUERY,
            confidence=0.9,
            reasoning="Test classification",
            suggested_agent="sql",
        )
        self.manager.router.classify_task = Mock(return_value=mock_classification)

        # Mock agent creation
        mock_agent = Mock()
        self.manager._create_agent = Mock(return_value=mock_agent)

        # Test routing
        question = "Show me all customers"
        agent, classification, context = self.manager.route_and_execute(question)

        # Verify results
        self.assertEqual(agent, mock_agent)
        self.assertEqual(classification, mock_classification)
        self.assertIn("conversation_history", context)

        # Verify conversation history is updated
        history = context["conversation_history"]
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["input"], question)
        self.assertEqual(history[0]["classification"], mock_classification)
        self.assertEqual(history[0]["agent_type"], "sql")


if __name__ == "__main__":
    unittest.main()
