"""
End-to-end tests for agents.

These tests can use either:
1. OpenAI API (requires OPENAI_API_KEY environment variable)
2. GPT4All local model (requires gpt4all package and will download model on first run)
"""
import os
import pytest
from ryoma_ai.agent.chat_agent import ChatAgent
from ryoma_ai.agent.sql import SqlAgent


# Determine which backend to use
USE_OPENAI = os.environ.get("OPENAI_API_KEY") and os.environ.get("USE_OPENAI_FOR_TESTS", "").lower() == "true"
USE_GPT4ALL = not USE_OPENAI and os.environ.get("USE_GPT4ALL_FOR_TESTS", "").lower() == "true"

if USE_GPT4ALL:
    # Only import if we're using it
    pytest.importorskip("gpt4all")
    MODEL = "gpt4all:Llama-3.2-1B-Instruct-Q4_0.gguf"
elif USE_OPENAI:
    MODEL = "gpt-3.5-turbo"
else:
    # Skip all tests if no backend is configured
    pytest.skip("No LLM backend configured. Set USE_OPENAI_FOR_TESTS=true or USE_GPT4ALL_FOR_TESTS=true", allow_module_level=True)


def test_base_agent():
    """Test ChatAgent with configured model."""
    ryoma_agent = ChatAgent(MODEL)
    
    # Test with a simple query
    result = ryoma_agent.stream(
        "What is 2 + 2?"
    )
    assert result is not None
    
    # Collect streamed results
    responses = list(result)
    assert len(responses) > 0
    
    # Check that we got some response content
    response_text = "".join(str(r) for r in responses)
    assert len(response_text) > 0


def test_workflow_agent():
    """Test SqlAgent with configured model."""
    ryoma_agent = SqlAgent(MODEL)
    
    # Test with a simple SQL-related query
    result = ryoma_agent.stream(
        "Show me a simple SQL query to select all records from a table"
    )
    assert result is not None
    
    # Collect streamed results
    responses = list(result)
    assert len(responses) > 0
    
    # Check that we got some response
    response_text = "".join(str(r) for r in responses)
    assert len(response_text) > 0