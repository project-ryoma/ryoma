from typing import Dict, Generator
from typing_extensions import override

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

import openai
from openai.types.chat import ChatCompletionChunk

import openai_responses
from openai_responses import OpenAIMock
from openai_responses.streaming import Event, EventStream
from openai_responses.ext.httpx import Request, Response

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


class CreateChatCompletionEventStream(EventStream):  #
    @override
    def generate(self) -> Generator[Event, None, None]:  #
        chunk = ChatCompletionChunk.model_validate(
            {
                "id": "chatcmpl-123",
                "object": "chat.completion.chunk",
                "created": 1694268190,
                "model": "gpt-4o",
                "system_fingerprint": "fp_44709d6fcb",
                "choices": [
                    {
                        "index": 0,
                        "delta": {"role": "assistant", "content": ""},
                        "logprobs": None,
                        "finish_reason": None,
                    }
                ],
            }
        )
        yield self.event(None, chunk)  #

        chunk = ChatCompletionChunk.model_validate(
            {
                "id": "chatcmpl-123",
                "object": "chat.completion.chunk",
                "created": 1694268190,
                "model": "gpt-4o",
                "system_fingerprint": "fp_44709d6fcb",
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": "Hello"},
                        "logprobs": None,
                        "finish_reason": None,
                    }
                ],
            }
        )
        yield self.event(None, chunk)

        chunk = ChatCompletionChunk.model_validate(
            {
                "id": "chatcmpl-123",
                "object": "chat.completion.chunk",
                "created": 1694268190,
                "model": "gpt-4o",
                "system_fingerprint": "fp_44709d6fcb",
                "choices": [
                    {"index": 0, "delta": {}, "logprobs": None, "finish_reason": "stop"}
                ],
            }
        )
        yield self.event(None, chunk)


def create_chat_completion_response(request: Request) -> Response:
    stream = CreateChatCompletionEventStream()
    return Response(201, content=stream)


@openai_responses.mock()
def test_create_chat_completion_stream(openai_mock: OpenAIMock):
    openai_mock.chat.completions.create.response = create_chat_completion_response

    client = openai.Client(api_key="sk-fake123")
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ],
        stream=True,
    )

    received_chunks = 0

    for chunk in completion:
        received_chunks += 1
        assert chunk.id

    assert received_chunks == 3


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
def sql_agent():
    return SqlAgent("gpt-3.5-turbo")


@pytest.fixture
def pandas_agent():
    return PandasAgent("gpt-3.5-turbo")


def test_agent(agent):
    assert "gpt-3.5-turbo" in agent.model.models
    assert agent.tool_registry == {}


def test_sql_agent(sql_agent):
    assert "gpt-3.5-turbo" in sql_agent.model.models
    assert "sql_database_query" in sql_agent.tool_registry


@openai_responses.mock()
def test_chat(agent, openai_mock: OpenAIMock):
    openai_mock.chat.completions.create.response = create_chat_completion_response
    chat_response = agent.chat("Hello, world!", display=False)
    first_response = next(chat_response)
    assert first_response.content == ""


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
    with patch("aita.tool.sql_tool.SqlQueryTool.run") as mock_run:
        mock_run.return_value = "result"
        result = sql_agent.run_tool(
            {"name": "sql_database_query", "args": "SELECT * FROM customers LIMIT 4"}
        )
        assert result == "result"


def test_pandas_agent(pandas_agent):
    assert "gpt-3.5-turbo" in pandas_agent.model.models
    assert "pandas_analysis_tool" in pandas_agent.tool_registry
