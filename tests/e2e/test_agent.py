from ryoma.agent.base import BaseAgent
from ryoma.agent.sql import SqlAgent

import os
import pytest


@pytest.fixture(autouse=True)
def setup_openai_api_key():
    # Check if OPENAI_API_KEY is set in the environment
    if "OPENAI_API_KEY" not in os.environ:
        pytest.skip("OPENAI_API_KEY not set in environment variables")


def test_base_agent():
    # Create an simple ryoma Agent with GPT-3.5-turbo model
    ryoma_agent = BaseAgent("gpt-3.5-turbo")
    result = ryoma_agent.stream(
        "I want to get the top 5 customers which making the most purchases"
    )
    assert result is not None


def test_workflow_agent():
    # Create an simple ryoma Agent with GPT-3.5-turbo model
    ryoma_agent = SqlAgent("gpt-3.5-turbo")
    result = ryoma_agent.stream(
        "I want to get the top 5 customers which making the most purchases"
    )
    assert result is not None
