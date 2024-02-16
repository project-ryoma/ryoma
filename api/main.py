from dataplatform import DataSourceFactory
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from metadb import state_store
from models import Prompt, ConnectionParams
from openai import OpenAI, OpenAIError, ChatCompletion
from tools import tool_schemas
import importlib
import json
import os
import uvicorn

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

@app.get('/health')
def health():
    return {"health": "healthy"}


@app.get('/favicon.ico', include_in_schema=False)
def favicon():
    return FileResponse('favicon.ico')


def chat_completion_request(messages, functions=None, max_tokens=1000, n=3, temperature=0.7) -> ChatCompletion:
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0613",
            messages=messages,
            max_tokens=max_tokens,
            n=n,
            temperature=temperature,
            functions=functions
        )
        print('chat_response', response)
        return response
    except OpenAIError as e:
        return e


@app.post('/connect-datasource')
def connect_datasource(datasource: str, connection_params: ConnectionParams):
    conn = DataSourceFactory.create_datasource(datasource=datasource, **connection_params.dict())

    state_store.cache[datasource] = conn
    return {"status": "Success", "message": f"Connected to datasource: {datasource}"}


@app.post('/execute-function')
def execute_function(function_name: str, function_arguments):
    function_to_call = {}.get(function_name)
    try:
        fn_result = function_to_call(**function_arguments)
        chat_response = chat_completion_request(
            messages=[{"role": "user", "content": fn_result}],
            functions=tool_schemas,
            n=1
        )
        return {
            "status": "Success",
            "message": chat_response.choices[0].message.content
        }
    except Exception as err:
        error_template = f"""
Failed to execute function: {function_name} with function arguments: {function_arguments}
Error: {err}.
Can you please figure out what went wrong, and maybe ask user for more information?
"""
        chat_response = chat_completion_request(messages=[{"role": "user", "content": error_template}], n=1)
        return {
            "status": "Error",
            "message": chat_response.choices[0].message.content
        }


@app.post('/chat')
def chat(prompt: Prompt):
    messages = [{"role": "user", "content": "(current request) %s" % prompt.prompt}]

    # chat_response = chat_completion_request(messages, n=1)
    chat_response = chat_completion_request(messages, tool_schemas)
    if isinstance(chat_response, Exception):
        return {
            "status": "Error",
            "message": "Failed to get chat response with err: \n{}".format(chat_response)
        }

    # initial message
    response_choice = chat_response.choices[0]

    # if the response message contains a function call, ask the user to confirm the execution of the function
    if response_choice.finish_reason == 'function_call':
        function_call = response_choice.message.function_call
        function_name = function_call.name
        function_arguments = json.loads(function_call.arguments)

        try:
            module = importlib.import_module("tools")
            function_to_call = getattr(module, function_name)
            fn_result = function_to_call.__call__(**function_arguments)
            chat_response = chat_completion_request(
                messages=[{"role": "user", "content": fn_result}],
                functions=tool_schemas,
                n=1
            )
            return {
                "status": "Success",
                "message": chat_response.choices[0].message.content
            }
        except Exception as err:
            error_template = f"""
        Failed to execute function: {function_name} with function arguments: {function_arguments}
        Error: {err}.
        Can you please figure out what went wrong, and maybe ask user for more information?
        """
            print(err)
            chat_response = chat_completion_request(messages=[{"role": "user", "content": error_template}], n=1)
            return {
                "status": "Error",
                "message": chat_response.choices[0].message.content
            }

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
        return {
            "status": "Success",
            "message": response_choice.message.content
        }


@app.post('/autocomplete')
def autocomplete(text: str):
    try:
        # Get the text input from the request body
        if not text:
            return {"error": "Missing text input"}, 400

        prompt = f"""
Using the chat history, complete the sentence: {text}.
Please finish the sentence beginning with the input text as it is.
Please ensure that the completed sentence starts with the exact input text.
"""

        messages = [{"role": "user", "content": prompt}]

        # Send a request to the GPT-3 API with the text input
        response = chat_completion_request(messages=messages)
        # Extract suggestions from the GPT-3 response
        suggestions = [choice.message.content.strip() for choice in response.choices]
        suggestions = list(dict.fromkeys(suggestions))

        # Return suggestions as a JSON response
        return {"suggestions": suggestions}

    except Exception as e:
        return {"error": str(e)}, 500


if __name__ == "__main__":
    uvicorn.run(app, port=3001)
