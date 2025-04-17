import os

import pytest
from ryoma_ai.agent.base import ChatAgent
from ryoma_ai.agent.sql import SqlAgent


@pytest.fixture(autouse=True)
def setup_openai_api_key():
    # Check if OPENAI_API_KEY is set in the environment
    if "OPENAI_API_KEY" not in os.environ:
        pytest.skip("OPENAI_API_KEY not set in environment variables")


def test_base_agent():
    # Create an simple ryoma_ai Agent with GPT-3.5-turbo model
    ryoma_agent = ChatAgent("gpt-3.5-turbo")
    result = ryoma_agent.stream(
        "I want to get the top 5 customers which making the most purchases"
    )
    assert result is not None


def test_workflow_agent():
    # Create an simple ryoma_ai Agent with GPT-3.5-turbo model
    ryoma_agent = SqlAgent("gpt-3.5-turbo")
    result = ryoma_agent.stream(
        "I want to get the top 5 customers which making the most purchases"
    )
    assert result is not None
