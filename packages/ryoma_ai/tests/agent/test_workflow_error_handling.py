"""
Tests for workflow agent error handling and model initialization.

These tests verify that the workflow agent properly handles model initialization
failures and provides helpful error messages to users.
"""

from unittest.mock import Mock, patch

import pytest
from ryoma_ai.agent.workflow import WorkflowAgent


class TestWorkflowAgentErrorHandling:
    """Test workflow agent error handling scenarios."""

    def test_gemini_model_initialization_success(self):
        """Test successful Gemini model initialization."""
        model_id = "gemini:gemini-2.0-flash"

        with patch("ryoma_ai.llm.provider.load_model_provider") as mock_load:
            mock_model = Mock()
            mock_model.bind_tools.return_value = mock_model
            mock_load.return_value = mock_model

            agent = WorkflowAgent(tools=[], model=model_id)

            # Verify model was loaded and stored
            assert agent.model == mock_model
            assert agent._original_model_id == model_id
            mock_load.assert_called_once_with(model_id, model_parameters=None)

    def test_model_initialization_failure_error_message(self):
        """Test that model initialization failure provides helpful error message."""
        model_id = "gemini:invalid-model"

        with patch(
            "ryoma_ai.llm.provider.load_model_provider",
            side_effect=Exception("Model not found"),
        ):
            with pytest.raises(Exception, match="Model not found"):
                WorkflowAgent(tools=[], model=model_id)

    def test_chain_build_with_failed_model_initialization(self):
        """Test that _build_chain provides helpful error when model is None."""
        # Create agent with mock model first
        with patch("ryoma_ai.llm.provider.load_model_provider") as mock_load:
            mock_model = Mock()
            mock_model.bind_tools.return_value = mock_model
            mock_load.return_value = mock_model

            agent = WorkflowAgent(tools=[], model="openai:gpt-4")

            # Now simulate model being None (initialization failed)
            agent.model = None
            agent._original_model_id = "gemini:gemini-2.0-flash"

            with pytest.raises(
                ValueError, match="Unable to initialize model 'gemini:gemini-2.0-flash'"
            ):
                agent._build_chain()

    def test_chain_build_error_message_content(self):
        """Test that the error message contains all expected troubleshooting steps."""
        with patch("ryoma_ai.llm.provider.load_model_provider") as mock_load:
            mock_model = Mock()
            mock_model.bind_tools.return_value = mock_model
            mock_load.return_value = mock_model

            agent = WorkflowAgent(tools=[], model="gemini:gemini-2.0-flash")
            agent.model = None

            try:
                agent._build_chain()
                assert False, "Expected ValueError"
            except ValueError as e:
                error_message = str(e)
                # Check that all troubleshooting steps are included
                assert "Correct model format" in error_message
                assert "gemini:gemini-2.0-flash" in error_message
                assert "Required API key environment variable set" in error_message
                assert "Required dependencies installed" in error_message
                assert "Check logs above for specific error details" in error_message

    def test_model_with_parameters_initialization(self):
        """Test model initialization with custom parameters."""
        model_id = "gemini:gemini-1.5-pro"
        params = {"temperature": 0.7, "max_tokens": 1024}

        with patch("ryoma_ai.llm.provider.load_model_provider") as mock_load:
            mock_model = Mock()
            mock_model.bind_tools.return_value = mock_model
            mock_load.return_value = mock_model

            agent = WorkflowAgent(tools=[], model=model_id, model_parameters=params)

            mock_load.assert_called_once_with(model_id, model_parameters=params)
            assert agent.model_parameters == params

    def test_direct_model_object_initialization(self):
        """Test initialization with direct model object instead of string."""
        mock_model = Mock()
        mock_model.bind_tools.return_value = mock_model

        agent = WorkflowAgent(tools=[], model=mock_model)

        assert agent.model == mock_model
        assert agent._original_model_id == "Mock"  # From type(model).__name__

    def test_tools_binding_success(self):
        """Test that tools are properly bound to the model."""
        mock_tool = Mock()
        mock_tool.name = "test_tool"

        with patch("ryoma_ai.llm.provider.load_model_provider") as mock_load:
            mock_model = Mock()
            mock_bound_model = Mock()
            mock_model.bind_tools.return_value = mock_bound_model
            mock_load.return_value = mock_model

            agent = WorkflowAgent(tools=[mock_tool], model="openai:gpt-4")

            # Verify bind_tools was called with the tool
            mock_model.bind_tools.assert_called_once_with([mock_tool])
            assert agent.model == mock_bound_model

    def test_tools_binding_fallback(self):
        """Test fallback when model doesn't support bind_tools."""
        mock_tool = Mock()
        mock_tool.name = "test_tool"
        mock_tool.description = "A test tool"

        with patch("ryoma_ai.llm.provider.load_model_provider") as mock_load:
            # Create mock model without bind_tools method
            mock_model = Mock(spec=[])  # spec=[] means no methods
            mock_load.return_value = mock_model

            with patch(
                "ryoma_ai.agent.workflow.render_text_description"
            ) as mock_render:
                mock_render.return_value = "Tool descriptions"

                agent = WorkflowAgent(tools=[mock_tool], model="custom:legacy-model")

                # Verify render_text_description was used as fallback
                mock_render.assert_called_once_with([mock_tool])
                assert agent.model == mock_model

    def test_chain_building_with_prompt_template(self):
        """Test that chain building properly uses prompt templates."""
        with patch("ryoma_ai.llm.provider.load_model_provider") as mock_load:
            mock_model = Mock()
            mock_model.bind_tools.return_value = mock_model
            mock_load.return_value = mock_model

            # Mock prompt template factory
            with patch(
                "ryoma_ai.prompt.prompt_template.PromptTemplateFactory"
            ) as mock_factory_class:
                mock_factory = Mock()
                mock_template = Mock()
                mock_template.append = Mock()
                mock_factory.build_prompt.return_value = mock_template
                mock_factory_class.return_value = mock_factory

                agent = WorkflowAgent(tools=[], model="openai:gpt-4")

                agent._build_chain()

                # Verify prompt template was built and messages placeholder was added
                mock_factory.build_prompt.assert_called_once()
                mock_template.append.assert_called_once()

    def test_error_original_model_id_tracking(self):
        """Test that original model ID is properly tracked for error reporting."""
        test_cases = [
            ("gemini:gemini-2.0-flash", "gemini:gemini-2.0-flash"),
            ("openai:gpt-4-turbo", "openai:gpt-4-turbo"),
            ("anthropic:claude-3-sonnet", "anthropic:claude-3-sonnet"),
        ]

        for model_id, expected_original in test_cases:
            with patch("ryoma_ai.llm.provider.load_model_provider") as mock_load:
                mock_model = Mock()
                mock_model.bind_tools.return_value = mock_model
                mock_load.return_value = mock_model

                agent = WorkflowAgent(tools=[], model=model_id)

                assert agent._original_model_id == expected_original


class TestWorkflowAgentIntegration:
    """Integration tests for workflow agent with realistic scenarios."""

    def test_gemini_sql_agent_workflow(self):
        """Test complete workflow with Gemini model for SQL generation."""
        with patch("ryoma_ai.llm.provider.load_model_provider") as mock_load:
            mock_model = Mock()
            mock_model.bind_tools.return_value = mock_model
            mock_load.return_value = mock_model

            # Mock SQL tools
            mock_sql_tool = Mock()
            mock_sql_tool.name = "sql_executor"
            mock_sql_tool.description = "Execute SQL queries"

            agent = WorkflowAgent(
                tools=[mock_sql_tool],
                model="gemini:gemini-2.0-flash",
                model_parameters={"temperature": 0.0},
            )

            # Verify initialization
            assert agent.model == mock_model
            assert agent._original_model_id == "gemini:gemini-2.0-flash"
            assert agent.model_parameters == {"temperature": 0.0}

            # Test workflow property (lazy initialization)
            workflow = agent.workflow
            assert workflow is not None

    def test_error_handling_with_missing_dependencies(self):
        """Test error handling when model dependencies are missing."""
        with patch(
            "ryoma_ai.llm.provider.load_model_provider",
            side_effect=ImportError("Failed to import ChatGoogleGenerativeAI"),
        ):
            with pytest.raises(
                ImportError, match="Failed to import ChatGoogleGenerativeAI"
            ):
                WorkflowAgent(tools=[], model="gemini:gemini-2.0-flash")

    def test_error_handling_with_invalid_api_key(self):
        """Test error handling when API key is invalid."""
        with patch(
            "ryoma_ai.llm.provider.load_model_provider",
            side_effect=Exception("Invalid API key"),
        ):
            with pytest.raises(Exception, match="Invalid API key"):
                WorkflowAgent(tools=[], model="gemini:gemini-2.0-flash")

    @patch("ryoma_ai.llm.provider.load_model_provider")
    def test_workflow_memory_initialization(self, mock_load):
        """Test that workflow agent properly initializes memory."""
        mock_model = Mock()
        mock_model.bind_tools.return_value = mock_model
        mock_load.return_value = mock_model

        agent = WorkflowAgent(tools=[], model="openai:gpt-4")

        # Check that memory saver was created
        assert agent.memory is not None
        assert hasattr(agent.memory, "storage")  # MemorySaver should have storage

    @patch("ryoma_ai.llm.provider.load_model_provider")
    def test_workflow_config_initialization(self, mock_load):
        """Test that workflow agent properly initializes configuration."""
        mock_model = Mock()
        mock_model.bind_tools.return_value = mock_model
        mock_load.return_value = mock_model

        agent = WorkflowAgent(
            tools=[], model="openai:gpt-4", user_id="test_user", thread_id="test_thread"
        )

        # Check configuration
        assert "configurable" in agent.config
        assert agent.config["configurable"]["user_id"] == "test_user"
        assert agent.config["configurable"]["thread_id"] == "test_thread"
