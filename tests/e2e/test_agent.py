from ryoma.agent.base import RyomaAgent
from ryoma.agent.sql import SqlAgent


def test_base_agent():
    # Create an simple ryoma Agent with GPT-3.5-turbo model
    ryoma_agent = RyomaAgent("gpt-3.5-turbo")
    result = ryoma_agent.stream("I want to get the top 5 customers which making the most purchases")
    assert result is not None


def test_workflow_agent():
    # Create an simple ryoma Agent with GPT-3.5-turbo model
    ryoma_agent = SqlAgent("gpt-3.5-turbo")
    result = ryoma_agent.stream("I want to get the top 5 customers which making the most purchases")
    assert result is not None
