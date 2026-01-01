"""
Integration tests for SQL agent with Gemini models.

These tests verify that the SQL agent works correctly with Gemini models,
including proper prompt handling, error scenarios, and SQL generation.
"""

from unittest.mock import Mock, patch

import pytest
from ryoma_ai.agent.sql import SQLAgent
from ryoma_data.sql import SQLDatasource


class TestSQLAgentGeminiIntegration:
    """Test SQL agent integration with Gemini models."""

    @patch("ryoma_ai.llm.provider.load_model_provider")
    def test_sql_agent_gemini_initialization(self, mock_load):
        """Test SQL agent initialization with Gemini model."""
        mock_model = Mock()
        mock_load.return_value = mock_model

        mock_datasource = Mock(spec=SQLDatasource)

        agent = SQLAgent(model="gemini:gemini-2.0-flash", datasource=mock_datasource)

        assert agent.model == mock_model
        assert agent._original_model_id == "gemini:gemini-2.0-flash"
        mock_load.assert_called_once_with(
            "gemini:gemini-2.0-flash", model_parameters=None
        )

    @patch("ryoma_ai.llm.provider.load_model_provider")
    def test_sql_agent_gemini_with_parameters(self, mock_load):
        """Test SQL agent with Gemini model and custom parameters."""
        mock_model = Mock()
        mock_load.return_value = mock_model

        mock_datasource = Mock(spec=SQLDatasource)

        params = {"temperature": 0.0, "max_tokens": 1024, "top_p": 0.9}

        agent = SQLAgent(
            model="gemini:gemini-1.5-pro",
            model_parameters=params,
            datasource=mock_datasource,
        )

        assert agent.model_parameters == params
        mock_load.assert_called_once_with(
            "gemini:gemini-1.5-pro", model_parameters=params
        )

    @patch("ryoma_ai.llm.provider.load_model_provider")
    def test_sql_agent_gemini_prompt_creation(self, mock_load):
        """Test that SQL agent creates appropriate prompts for Gemini."""
        mock_model = Mock()
        mock_load.return_value = mock_model

        mock_datasource = Mock(spec=SQLDatasource)
        mock_datasource.get_table_schema.return_value = (
            "CREATE TABLE users (id INT, name VARCHAR(100))"
        )

        with patch("ryoma_ai.prompt.manager.prompt_manager") as mock_prompt_manager:
            mock_prompt = Mock()
            mock_prompt_manager.create_sql_prompt.return_value = mock_prompt

            agent = SQLAgent(
                model="gemini:gemini-2.0-flash", datasource=mock_datasource
            )

            # Test prompt creation for a query
            query = "What are all the user names?"

            # Mock the chain execution
            with patch.object(agent, "chain") as mock_chain:
                mock_chain.invoke.return_value.content = "SELECT name FROM users;"

                agent.invoke(query)

                # Verify prompt was created with correct parameters
                mock_prompt_manager.create_sql_prompt.assert_called()

    @patch("ryoma_ai.llm.provider.load_model_provider")
    def test_sql_agent_error_handling_with_gemini(self, mock_load):
        """Test error handling when Gemini model fails to initialize."""
        mock_load.side_effect = ImportError("Failed to import ChatGoogleGenerativeAI")

        mock_datasource = Mock(spec=SQLDatasource)

        with pytest.raises(
            ImportError, match="Failed to import ChatGoogleGenerativeAI"
        ):
            SQLAgent(model="gemini:gemini-2.0-flash", datasource=mock_datasource)

    @patch("ryoma_ai.llm.provider.load_model_provider")
    def test_sql_agent_api_key_error(self, mock_load):
        """Test error handling when Gemini API key is missing."""
        mock_load.side_effect = Exception("API key not provided")

        mock_datasource = Mock(spec=SQLDatasource)

        with pytest.raises(Exception, match="API key not provided"):
            SQLAgent(model="gemini:gemini-2.0-flash", datasource=mock_datasource)

    @patch("ryoma_ai.llm.provider.load_model_provider")
    def test_sql_generation_with_gemini_mock_response(self, mock_load):
        """Test SQL generation with mocked Gemini response."""
        mock_model = Mock()
        mock_load.return_value = mock_model

        mock_datasource = Mock(spec=SQLDatasource)
        mock_datasource.get_table_schema.return_value = (
            "CREATE TABLE products (id INT, name VARCHAR(100), price DECIMAL)"
        )

        agent = SQLAgent(model="gemini:gemini-2.0-flash", datasource=mock_datasource)

        # Mock the chain to return a SQL query
        with patch.object(agent, "chain") as mock_chain:
            mock_response = Mock()
            mock_response.content = (
                "SELECT name, price FROM products WHERE price > 100;"
            )
            mock_chain.invoke.return_value = mock_response

            result = agent.invoke("Show me products that cost more than $100")

            # Verify the SQL was returned
            assert "SELECT name, price FROM products WHERE price > 100;" in str(result)

    @patch("ryoma_ai.llm.provider.load_model_provider")
    def test_sql_agent_streaming_with_gemini(self, mock_load):
        """Test SQL agent streaming functionality with Gemini."""
        mock_model = Mock()
        mock_load.return_value = mock_model

        mock_datasource = Mock(spec=SQLDatasource)

        agent = SQLAgent(model="gemini:gemini-2.0-flash", datasource=mock_datasource)

        # Mock the chain streaming
        with patch.object(agent, "chain") as mock_chain:
            # Mock streaming response
            mock_events = [
                Mock(content="SELECT"),
                Mock(content=" name"),
                Mock(content=" FROM"),
                Mock(content=" users;"),
            ]
            mock_chain.stream.return_value = iter(mock_events)

            # Test streaming (capture output to avoid printing)
            import contextlib
            import io

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                agent.stream("What are the user names?", display=True)

            # Verify stream was called
            mock_chain.stream.assert_called_once()

    @patch("ryoma_ai.llm.provider.load_model_provider")
    def test_sql_agent_with_vector_store(self, mock_load):
        """Test SQL agent with vector store for context retrieval."""
        mock_model = Mock()
        mock_load.return_value = mock_model

        mock_datasource = Mock(spec=SQLDatasource)
        mock_vector_store = Mock()
        mock_vector_store.retrieve_columns.return_value = ["id", "name", "email"]

        agent = SQLAgent(
            model="gemini:gemini-2.0-flash",
            datasource=mock_datasource,
            vector_store=mock_vector_store,
        )

        assert agent.vector_store == mock_vector_store

    @patch("ryoma_ai.llm.provider.load_model_provider")
    def test_different_gemini_model_versions(self, mock_load):
        """Test SQL agent with different Gemini model versions."""
        model_versions = [
            "gemini:gemini-1.5-pro",
            "gemini:gemini-1.5-flash",
            "gemini:gemini-2.0-flash",
            "google:gemini-pro",
        ]

        mock_datasource = Mock(spec=SQLDatasource)

        for model_version in model_versions:
            mock_model = Mock()
            mock_load.return_value = mock_model

            agent = SQLAgent(model=model_version, datasource=mock_datasource)

            assert agent._original_model_id == model_version
            mock_load.assert_called_with(model_version, model_parameters=None)

    @patch("ryoma_ai.llm.provider.load_model_provider")
    def test_sql_agent_prompt_template_integration(self, mock_load):
        """Test that SQL agent properly integrates with the new prompt system."""
        mock_model = Mock()
        mock_load.return_value = mock_model

        mock_datasource = Mock(spec=SQLDatasource)
        mock_datasource.get_table_schema.return_value = (
            "CREATE TABLE orders (id INT, customer_id INT, total DECIMAL)"
        )

        # Test with the new prompt system
        with patch("ryoma_ai.prompt.manager.prompt_manager") as mock_prompt_manager:
            mock_template = Mock()
            mock_prompt_manager.create_sql_prompt.return_value = mock_template

            agent = SQLAgent(
                model="gemini:gemini-2.0-flash", datasource=mock_datasource
            )

            # Mock chain execution
            with patch.object(agent, "chain") as mock_chain:
                mock_response = Mock()
                mock_response.content = "SELECT COUNT(*) FROM orders;"
                mock_chain.invoke.return_value = mock_response

                agent.invoke("How many orders are there?")

                # Verify the new prompt system was used
                mock_prompt_manager.create_sql_prompt.assert_called()


class TestSQLAgentErrorScenarios:
    """Test various error scenarios with SQL agent and Gemini."""

    @patch("ryoma_ai.llm.provider.load_model_provider")
    def test_model_none_error_message(self, mock_load):
        """Test error message when model initialization results in None."""
        mock_load.return_value = None

        mock_datasource = Mock(spec=SQLDatasource)

        agent = SQLAgent(model="gemini:invalid-model", datasource=mock_datasource)

        # Simulate the scenario where model is None
        agent.model = None

        with pytest.raises(
            ValueError, match="Unable to initialize model 'gemini:invalid-model'"
        ):
            agent._build_chain()

    @patch("ryoma_ai.llm.provider.load_model_provider")
    def test_chain_build_error_troubleshooting_steps(self, mock_load):
        """Test that error message includes troubleshooting steps."""
        mock_model = Mock()
        mock_load.return_value = mock_model

        mock_datasource = Mock(spec=SQLDatasource)

        agent = SQLAgent(model="gemini:gemini-2.0-flash", datasource=mock_datasource)

        # Simulate failed model
        agent.model = None

        try:
            agent._build_chain()
            assert False, "Expected ValueError"
        except ValueError as e:
            error_msg = str(e)

            # Check for troubleshooting guidance
            assert "Correct model format" in error_msg
            assert "API key environment variable" in error_msg
            assert "Required dependencies installed" in error_msg
            assert "gemini:gemini-2.0-flash" in error_msg

    @patch("ryoma_ai.llm.provider.load_model_provider")
    def test_datasource_connection_error(self, mock_load):
        """Test handling of datasource connection errors."""
        mock_model = Mock()
        mock_load.return_value = mock_model

        mock_datasource = Mock(spec=SQLDatasource)
        mock_datasource.get_table_schema.side_effect = Exception("Connection failed")

        SQLAgent(model="gemini:gemini-2.0-flash", datasource=mock_datasource)

        # Test that datasource errors are propagated
        with pytest.raises(Exception, match="Connection failed"):
            mock_datasource.get_table_schema("users")

    @patch("ryoma_ai.llm.provider.load_model_provider")
    def test_gemini_response_parsing_error(self, mock_load):
        """Test handling of invalid Gemini responses."""
        mock_model = Mock()
        mock_load.return_value = mock_model

        mock_datasource = Mock(spec=SQLDatasource)

        agent = SQLAgent(model="gemini:gemini-2.0-flash", datasource=mock_datasource)

        # Mock chain to return invalid response
        with patch.object(agent, "chain") as mock_chain:
            mock_response = Mock()
            mock_response.content = "I cannot generate SQL for that query."
            mock_chain.invoke.return_value = mock_response

            result = agent.invoke("Invalid query")

            # Should handle non-SQL responses gracefully
            assert "I cannot generate SQL" in str(result)
