import os

import openai
import openai_responses
import pytest
from openai_responses import OpenAIMock
from ryoma_ai.agent.base import ChatAgent

from tests.unit_tests.test_utils import (
    create_chat_completion_response_stream,
    mock_chat_response,
)


@pytest.fixture(autouse=True)
def mock_openai_api_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "foo")


@openai_responses.mock()
def test_create_chat_completion_stream(openai_mock: OpenAIMock):
    openai_mock.chat.completions.create.response = (
        create_chat_completion_response_stream
    )

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
    return ChatAgent("gpt-3.5-turbo")


@openai_responses.mock()
def test_chat(agent, openai_mock: OpenAIMock):
    openai_mock.chat.completions.create.response = mock_chat_response("Hello, world!")
    chat_response = agent.invoke("Hello, world!", display=False)
    assert chat_response.content == "Hello, world!"
