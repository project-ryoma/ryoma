from aita.tools import tool_schemas
from aita.utils import chat_completion_request
from app.api.deps import SessionDep
from app.models import QueryContent, ChatResponse
from fastapi import APIRouter
from typing import Any
import importlib
import json

router = APIRouter()


@router.post("/", response_model=ChatResponse)
def chat(*, session: SessionDep, query_content: QueryContent) -> Any:
    messages = [{"role": "user", "content": "(current request) %s" % query_content.query}]

    # chat_response = chat_completion_request(messages, n=1)
    chat_response = chat_completion_request(messages, tool_schemas)
    if isinstance(chat_response, Exception):
        return {
            "status": "Error",
            "message": f"Failed to get chat response with err: \n{chat_response}",
        }

    # initial message
    response_choice = chat_response.choices[0]

    # if the response message contains a function call, ask the user to confirm the execution of the function
    if response_choice.finish_reason == "function_call":
        function_call = response_choice.message.function_call
        function_name = function_call.name
        function_arguments = json.loads(function_call.arguments)

        try:
            module = importlib.import_module("tools")
            function_to_call = getattr(module, function_name)
            fn_result = function_to_call.__call__(**function_arguments)
            chat_response = chat_completion_request(
                messages=[{"role": "user", "content": fn_result}], functions=tool_schemas, n=1
            )
            return {"status": "Success", "message": chat_response.choices[0].message.content}
        except Exception as err:
            error_template = f"""
        Failed to execute function: {function_name} with function arguments: {function_arguments}
        Error: {err}.
        Can you please figure out what went wrong, and maybe ask user for more information?
        """
            print(err)
            chat_response = chat_completion_request(
                messages=[{"role": "user", "content": error_template}], n=1
            )
            return {"status": "Error", "message": chat_response.choices[0].message.content}

        # ask user to confirm the execution of the function, and show the function arguments,
        # check if the function arguments are correct
    #         prompt = f"""
    # The response contains a function call: {function_name} with function arguments: {function_arguments}.
    # Ask the user to confirm the execution of the function and required missing arguments.
    # """
    #         messages = [{"role": "system", "content": prompt}]
    #         chat_response = chat_completion_request(messages, functions=None, n=1)
    #         response_choice = chat_response.choices[0]
    #
    #         return {
    #             "status": "Success",
    #             "message": response_choice.message.content,
    #             "template": {
    #                 "type": "function_call",
    #                 "function_name": function_name,
    #                 "function_arguments": function_arguments
    #             }
    #         }

    else:
        return {"status": "Success", "message": response_choice.message.content}
