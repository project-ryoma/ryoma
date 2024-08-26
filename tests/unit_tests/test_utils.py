import os
from datetime import datetime
from typing import Dict, Generator

from openai.types.chat import ChatCompletionChunk, ChatCompletionMessage
from openai.types.chat.chat_completion import ChatCompletion, Choice
from openai_responses.ext.httpx import Request, Response
from openai_responses.streaming import EventStream
from typing_extensions import override

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
    def generate(self) -> Generator[ChatCompletionChunk, None, None]:  #
        yield ChatCompletionChunk.model_validate(
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

        yield ChatCompletionChunk.model_validate(
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

        yield ChatCompletionChunk.model_validate(
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


class CreateChatCompletionEventStreamWithToolCall(EventStream):
    @override
    def generate(self) -> Generator[ChatCompletionChunk, None, None]:
        yield ChatCompletionChunk.model_validate(
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
                "additional_kwargs": {
                    "tool_calls": [
                        {
                            "function": {
                                "name": "sql_database_query",
                                "arguments": {
                                    "query": "SELECT * FROM customers LIMIT 4"
                                },
                            }
                        }
                    ]
                },
            }
        )


def create_chat_completion_response_stream(request: Request) -> Response:
    stream = CreateChatCompletionEventStream()
    return Response(201, content=stream)


def create_chat_completion_response_with_tool_call(request: Request) -> Response:
    stream = CreateChatCompletionEventStreamWithToolCall()
    return Response(201, content=stream)
