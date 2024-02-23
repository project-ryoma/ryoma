from typing import Any

import importlib
import json

from fastapi import APIRouter

from aita.tools import tool_schemas
from aita.utils import chat_completion_request, run_tool
from app.api.deps import SessionDep
from app.models import ChatResponse, ChatRequest, ChatResponseStatus

router = APIRouter()


@router.post("/", response_model=ChatResponse)
def chat(*, session: SessionDep, chat_request: ChatRequest) -> Any:
    messages = [{"role": "user", "content": "(current request) %s" % chat_request.prompt}]

    # chat_response = chat_completion_request(messages, n=1)
    chat_response = chat_completion_request(messages, tool_schemas)
    if isinstance(chat_response, Exception):
        return ChatResponse(
            status=ChatResponseStatus.error,
            message= f"Failed to get chat response with err: \n{chat_response}"
        )

    # initial message
    response_choice = chat_response.choices[0]

    # if the response message contains a function call, ask the user to confirm the execution of the function
    if response_choice.finish_reason == "function_call":
        tool = response_choice.message.function_call
        tool_name = tool.name
        tool_arguments = json.loads(tool.arguments)

        if not chat_request.allow_function_calls:
            return ChatResponse(
                status=ChatResponseStatus.success,
                message="Please confirm to use the tool.",
                additional_info={
                    "type": "use_tool",
                    "name": tool_name,
                    "arguments": tool_arguments
                }
            )
        else:
            run_tool(tool_name, tool_arguments)
            return ChatResponse(
                status=ChatResponseStatus.error,
                messate=chat_response.choices[0].message.content
            )
    else:
        return ChatResponse(
            status=ChatResponseStatus.success,
            message=response_choice.message.content
        )
