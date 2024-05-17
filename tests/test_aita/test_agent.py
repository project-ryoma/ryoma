from typing import Dict

import os
from datetime import datetime

import pytest
from mock import patch
from openai.types.chat import ChatCompletionMessage
from openai.types.chat.chat_completion import ChatCompletion, Choice

from aita.agent.base import AitaAgent
from aita.agent.sql import SqlAgent
from aita.agent.pandas import PandasAgent
from aita.datasource.sql import SqlDataSource

os.environ["OPENAI_API_KEY"] = "foo"


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
        additional_kwargs=additional_kwargs,
    )


@pytest.fixture
def agent():
    return AitaAgent("gpt-3.5-turbo")


@pytest.fixture
def sql_datasource():
    SqlDataSource.__abstractmethods__ = set()
    SqlDataSource.execute = lambda x, y: "success"
    SqlDataSource.get_metadata = lambda _: "metadata"
    return SqlDataSource("sqlite:///test.db")


@pytest.fixture
def sql_agent(sql_datasource):
    return SqlAgent(sql_datasource, "gpt-3.5-turbo")


@pytest.fixture
def pandas_agent(sql_datasource):
    return PandasAgent(sql_datasource, "gpt-3.5-turbo")


def test_agent(agent):
    assert "gpt-3.5-turbo" in agent.model.models
    assert agent.tool_registry == {}


def test_sql_agent(sql_agent):
    assert "gpt-3.5-turbo" in sql_agent.model.models
    assert "sql_database_query" in sql_agent.tool_registry


def test_chat(agent):
    with patch("langchain_openai.ChatOpenAI.invoke") as mock_invoke:
        mock_invoke.return_value = mock_chat_response("Hello, world!")
        chat_response = agent.chat("Hello, world!")
        assert chat_response.choices[0].message.content == "Hello, world!"


def test_chat_with_tool(sql_agent):
    with patch("langchain_openai.ChatOpenAI.invoke") as mock_invoke:
        mock_invoke.return_value = mock_chat_response(
            "Hello, world!", additional_kwargs={
                "tool_calls": [
                    {
                        "function": {
                            "name": "sql_database_query",
                            "arguments": {
                                "query": "SELECT * FROM customers LIMIT 4"
                            }
                        }
                    }
                ]
            }
        )

        chat_response = sql_agent.chat("top 4 customers in database", allow_run_tool=True)
        assert chat_response == ["success"]


def test_run_tool(sql_agent):
    with patch("aita.tool.sql_tool.SqlDatabaseTool.run") as mock_run:
        mock_run.return_value = "result"
        result = sql_agent.run_tool(
            {"name": "sql_database_query", "args": "SELECT * FROM customers LIMIT 4"}
        )
        assert result == "result"


def test_pandas_agent(pandas_agent):
    assert "gpt-3.5-turbo" in pandas_agent.model.models
    assert "pandas_analysis_tool" in pandas_agent.tool_registry
