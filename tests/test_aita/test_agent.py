# create a test suite for the agent class
# test the agent class methods
# test the agent class properties
# test the agent class attributes
from typing import Dict

import pytest
from aita.agent import AitaAgent, AitaSqlAgent
from mock import patch

from openai.types.chat import ChatCompletionMessage
from openai.types.chat.chat_completion import ChatCompletion, Choice
from datetime import datetime
from langchain_community.utilities.sql_database import SQLDatabase


def mock_chat_response(content: str, additional_kwargs: Dict = None):
    if additional_kwargs is None:
        additional_kwargs = {}
    return ChatCompletion(
        id="foo",
        model="gpt-4",
        object="chat.completion",
        choices=[
            Choice(
                finish_reason="stop",
                index=0,
                message=ChatCompletionMessage(
                    content=content,
                    role="assistant",
                ),
            )
        ],
        created=int(datetime.now().timestamp()),
        additional_kwargs=additional_kwargs
    )


@pytest.fixture
def agent():
    return AitaAgent("gpt-3.5-turbo", 0.5, [], {})


@pytest.fixture
def sql_agent():
    with patch("sqlalchemy.create_engine") as mock_engine:
        mock_engine.return_value = "engine"
        db = SQLDatabase.from_uri("postgresql://:@localhost:5432")
        return AitaSqlAgent(db, "gpt-3.5-turbo", 0.5, {})


def test_agent(agent):
    assert agent.model == "gpt-3.5-turbo"
    assert agent.temperature == 0.5
    assert agent.tool_registry == {}


def test_chat(agent):
    with patch("langchain_openai.ChatOpenAI.invoke") as mock_invoke:
        mock_invoke.return_value = mock_chat_response("Hello, world!")
        chat_response = agent.chat("Hello, world!")
        assert chat_response.choices[0].message.content == "Hello, world!"


def test_chat_with_tool(sql_agent):
    with patch("langchain_openai.ChatOpenAI.invoke") as mock_invoke:
        mock_invoke.return_value = mock_chat_response(
            "Hello, world!",
            additional_kwargs={"tool_calls": "sql_db_query"}
        )

        chat_response = agent.chat("top 4 customers in database", allow_call_tool=True)
        assert chat_response.choices[0].message.content == "Hello, world!"
