"""
Tests for model provider initialization and error handling.

These tests verify that the model provider correctly handles different model formats,
provides appropriate error messages, and successfully initializes supported models.
"""

import os
from unittest.mock import Mock, patch

import pytest
from ryoma_ai.llm.provider import load_model_provider


class TestModelProvider:
    """Test model provider initialization and error handling."""

    def test_gemini_model_format_parsing(self):
        """Test that Gemini model format is correctly parsed."""
        model_id = "gemini:gemini-2.0-flash"

        with patch("ryoma_ai.llm.provider.ChatGoogleGenerativeAI") as mock_gemini:
            mock_instance = Mock()
            mock_gemini.return_value = mock_instance

            result = load_model_provider(model_id)

            # Verify correct provider and model name were used
            mock_gemini.assert_called_once_with(model="gemini-2.0-flash", **{})
            assert result == mock_instance

    def test_gemini_with_parameters(self):
        """Test Gemini model initialization with custom parameters."""
        model_id = "gemini:gemini-1.5-pro"
        params = {"temperature": 0.7, "max_tokens": 1024}

        with patch("ryoma_ai.llm.provider.ChatGoogleGenerativeAI") as mock_gemini:
            mock_instance = Mock()
            mock_gemini.return_value = mock_instance

            result = load_model_provider(model_id, model_parameters=params)

            mock_gemini.assert_called_once_with(
                model="gemini-1.5-pro", temperature=0.7, max_tokens=1024
            )
            assert result == mock_instance

    def test_openai_model_initialization(self):
        """Test OpenAI model initialization."""
        model_id = "openai:gpt-4"

        with patch("ryoma_ai.llm.provider.ChatOpenAI") as mock_openai:
            mock_instance = Mock()
            mock_openai.return_value = mock_instance

            result = load_model_provider(model_id)

            mock_openai.assert_called_once_with(model="gpt-4", **{})
            assert result == mock_instance

    def test_anthropic_model_initialization(self):
        """Test Anthropic model initialization."""
        model_id = "anthropic:claude-3-sonnet-20240229"

        with patch("ryoma_ai.llm.provider.ChatAnthropic") as mock_anthropic:
            mock_instance = Mock()
            mock_anthropic.return_value = mock_instance

            result = load_model_provider(model_id)

            mock_anthropic.assert_called_once_with(
                model="claude-3-sonnet-20240229", **{}
            )
            assert result == mock_instance

    def test_google_provider_aliases(self):
        """Test that different Google provider aliases work."""
        aliases = ["google", "gemini", "google-genai"]

        for alias in aliases:
            model_id = f"{alias}:gemini-2.0-flash"

            with patch("ryoma_ai.llm.provider.ChatGoogleGenerativeAI") as mock_gemini:
                mock_instance = Mock()
                mock_gemini.return_value = mock_instance

                result = load_model_provider(model_id)

                mock_gemini.assert_called_once_with(model="gemini-2.0-flash", **{})
                assert result == mock_instance

    def test_unsupported_provider_error(self):
        """Test error handling for unsupported providers."""
        model_id = "unsupported:some-model"

        with pytest.raises(ValueError, match="Unsupported model provider: unsupported"):
            load_model_provider(model_id)

    def test_invalid_model_id_format(self):
        """Test error handling for invalid model ID format."""
        invalid_ids = ["justmodelname", "", "provider:", ":modelname"]

        for invalid_id in invalid_ids:
            with pytest.raises(ValueError, match="Invalid model_id format"):
                load_model_provider(invalid_id)

    def test_gemini_import_error(self):
        """Test error handling when Gemini dependencies are missing."""
        model_id = "gemini:gemini-2.0-flash"

        with patch(
            "ryoma_ai.llm.provider.ChatGoogleGenerativeAI",
            side_effect=ImportError("No module named 'langchain_google_genai'"),
        ):
            with pytest.raises(
                ImportError, match="Failed to import ChatGoogleGenerativeAI"
            ):
                load_model_provider(model_id)

    def test_openai_import_error(self):
        """Test error handling when OpenAI dependencies are missing."""
        model_id = "openai:gpt-4"

        with patch(
            "ryoma_ai.llm.provider.ChatOpenAI",
            side_effect=ImportError("No module named 'langchain_openai'"),
        ):
            with pytest.raises(ImportError, match="Failed to import ChatOpenAI"):
                load_model_provider(model_id)

    def test_anthropic_import_error(self):
        """Test error handling when Anthropic dependencies are missing."""
        model_id = "anthropic:claude-3-sonnet"

        with patch(
            "ryoma_ai.llm.provider.ChatAnthropic",
            side_effect=ImportError("No module named 'langchain_anthropic'"),
        ):
            with pytest.raises(ImportError, match="Failed to import ChatAnthropic"):
                load_model_provider(model_id)

    def test_model_initialization_error(self):
        """Test error handling when model initialization fails."""
        model_id = "openai:gpt-4"

        with patch(
            "ryoma_ai.llm.provider.ChatOpenAI",
            side_effect=Exception("API key not found"),
        ):
            with pytest.raises(Exception, match="API key not found"):
                load_model_provider(model_id)

    def test_empty_parameters(self):
        """Test that empty parameters are handled correctly."""
        model_id = "openai:gpt-4"

        with patch("ryoma_ai.llm.provider.ChatOpenAI") as mock_openai:
            mock_instance = Mock()
            mock_openai.return_value = mock_instance

            # Test with None
            load_model_provider(model_id, model_parameters=None)
            mock_openai.assert_called_with(model="gpt-4", **{})

            # Test with empty dict
            load_model_provider(model_id, model_parameters={})
            mock_openai.assert_called_with(model="gpt-4", **{})

    def test_special_model_names(self):
        """Test handling of special characters in model names."""
        special_names = [
            "gpt-4-turbo-preview",
            "claude-3-5-sonnet-20241022",
            "gemini-1.5-pro-001",
            "gpt-4o-mini",
        ]

        for model_name in special_names:
            model_id = f"openai:{model_name}"

            with patch("ryoma_ai.llm.provider.ChatOpenAI") as mock_openai:
                mock_instance = Mock()
                mock_openai.return_value = mock_instance

                result = load_model_provider(model_id)

                mock_openai.assert_called_once_with(model=model_name, **{})
                assert result == mock_instance


class TestModelProviderIntegration:
    """Integration tests for model provider with real scenarios."""

    @patch.dict(os.environ, {"GOOGLE_API_KEY": "test_key"})
    def test_gemini_with_environment_variable(self):
        """Test that Gemini respects environment variables."""
        model_id = "gemini:gemini-2.0-flash"

        with patch("ryoma_ai.llm.provider.ChatGoogleGenerativeAI") as mock_gemini:
            mock_instance = Mock()
            mock_gemini.return_value = mock_instance

            result = load_model_provider(model_id)

            # Should be called regardless of env var (env var handled by langchain)
            mock_gemini.assert_called_once_with(model="gemini-2.0-flash", **{})
            assert result == mock_instance

    def test_provider_case_sensitivity(self):
        """Test that provider names are case-insensitive."""
        variations = ["OpenAI:gpt-4", "OPENAI:gpt-4", "openai:gpt-4", "OpenAi:gpt-4"]

        for model_id in variations:
            with patch("ryoma_ai.llm.provider.ChatOpenAI") as mock_openai:
                mock_instance = Mock()
                mock_openai.return_value = mock_instance

                result = load_model_provider(model_id)

                mock_openai.assert_called_once_with(model="gpt-4", **{})
                assert result == mock_instance

    def test_comprehensive_parameter_passing(self):
        """Test that all parameter types are correctly passed through."""
        model_id = "anthropic:claude-3-sonnet"
        complex_params = {
            "temperature": 0.8,
            "max_tokens": 2048,
            "top_p": 0.9,
            "top_k": 40,
            "streaming": True,
            "custom_param": "value",
        }

        with patch("ryoma_ai.llm.provider.ChatAnthropic") as mock_anthropic:
            mock_instance = Mock()
            mock_anthropic.return_value = mock_instance

            result = load_model_provider(model_id, model_parameters=complex_params)

            mock_anthropic.assert_called_once_with(
                model="claude-3-sonnet", **complex_params
            )
            assert result == mock_instance
