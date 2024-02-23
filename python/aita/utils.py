import os
import importlib
from typing import Dict

from openai import ChatCompletion, OpenAI, OpenAIError

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)


def chat_completion_request(
    messages, functions=None, max_tokens=1000, n=3, temperature=0.7
) -> ChatCompletion:
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0613",
            messages=messages,
            max_tokens=max_tokens,
            n=n,
            temperature=temperature,
            functions=functions,
        )
        return response
    except OpenAIError as e:
        return e


def run_tool(
    tool_name: str, tool_arguments: Dict[str, str]
) -> ChatCompletion:
    try:
        module = importlib.import_module("aita.tools")
        tool = getattr(module, tool_name)
        fn_result = tool.__call__(**tool_arguments)
        chat_response = chat_completion_request(
            messages=[{"role": "user", "content": fn_result}], n=1
        )
        return chat_response
    except Exception as err:
        error_template = f"""
        Failed to execute function: {tool_name} with function arguments: {tool_arguments}
        Error: {err}.
        Can you please figure out what went wrong, and maybe ask user for more information?
        """
        chat_response = chat_completion_request(
            messages=[{"role": "user", "content": error_template}], n=1
        )
        return chat_response
