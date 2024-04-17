import os
import json
import msal
from openai import OpenAI, OpenAIError, ChatCompletion
import sys

from flask_cors import CORS
from flask_session import Session

from flask import (Flask, redirect, render_template, request, jsonify,
                   send_from_directory, url_for, session)
from utils import Utils
from services.pbiembedservice import PbiEmbedService
import importlib
import logging


client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)


with open('./dataplatform/function_metadata.json', 'r') as f:
    functions_metadata = json.load(f)


# Create a mapping of function names to function objects
fn_map = {}
for function_metadata in functions_metadata:
    function_name = function_metadata['name']
    module_name = function_metadata.get('module', 'your_default_module')
    try:
        module = importlib.import_module(module_name)
        function = getattr(module, function_name)
        fn_map[function_name] = function
    except ImportError:
        logging.error(f"Could not import module: {module_name}")
    except AttributeError:
        logging.error(f"Could not find function: {function_name} in module: {module_name}")


confidential_client_app = msal.ConfidentialClientApplication(
    "f85ee12f-73a9-43d4-8453-2db3de7848fd",
    authority="https://login.microsoftonline.com/a60e2d77-3925-4eca-ace0-eecc604d922c",
    client_credential="LTV8Q~iCUw5LAzWLoO_0fWbevUCIgP2s6Ic1lanj",
)


# setup
app = Flask(__name__)

# Load configuration
app.config.from_object('config.BaseConfig')

CORS(app)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# logging
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
app.logger.addHandler(handler)

@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')

@app.route('/health')
def health():
    resp = jsonify(health="healthy")
    resp.status_code = 200
    return resp

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/hello', methods=['POST'])
def hello():
   name = request.form.get('name')

   if name:
       print('Request for hello page received with name=%s' % name)
       return render_template('hello.html', name = name)
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))

def chat_completion_request(messages, functions=None, max_tokens=1000, n=3, temperature=0.7) -> ChatCompletion:
    try:
        api_args = {
            "model": "gpt-3.5-turbo-0613",
            "messages": messages,
            "max_tokens": max_tokens,  # You might want to limit the number of tokens to keep suggestions short
            "n": n,  # Number of suggestions to generate
            "temperature": temperature  # Adjust as needed to control randomness
        }

        if functions is not None:
            api_args["functions"] = functions

        response = client.chat.completions.create(**api_args)
        print('chat_response', response)
        return response
    except OpenAIError as e:
        return e


@app.route('/execute_function', methods=['POST'])
def execute_function(function_name, function_arguments):
    function_to_call = fn_map.get(function_name)
    try:
        fn_result = function_to_call(**function_arguments)
        chat_response = chat_completion_request(messages=[{"role": "user", "content": fn_result}], n=1)
        return jsonify(
            {
                "status": "Success",
                "message": chat_response
            }
    )
    except Exception as err:
        error_template = f"""
Failed to execute function: {function_name} with function arguments: {function_arguments}
Error: {err}.
Can you please figure out what went wrong, and maybe ask user for more information?
"""
        chat_response = chat_completion_request(messages=[{"role": "user", "content": error_template}], n=1)
        return jsonify(
            {
                "status": "Error",
                "message": chat_response.choices[0].message.content
            }
        )


@app.route('/chatv2', methods=['POST'])
def chat():
    prompt = request.json.get('prompt', '')

    messages = [{"role": "user", "content": "(current request) %s" % prompt}]

    chat_response = chat_completion_request(messages, functions=functions_metadata, n=1)
    if isinstance(chat_response, Exception):
        return jsonify(
            {
                "status": "Error",
                "message": "Failed to get chat response with err: \n{}".format(chat_response)
            }
        )

    # initial message
    response_choice = chat_response.choices[0]

    # if the response message contains a function call, ask the user to confirm the execution of the function
    if response_choice.finish_reason == 'function_call':
        function_call = response_choice.message.function_call
        function_name = function_call.name
        function_arguments = json.loads(function_call.arguments)

        # ask user to confirm the execution of the function, and show the function arguments,
        # check if the function arguments are correct
        prompt = f"""
The response contains a function call: {function_name} with function arguments: {function_arguments}.
Ask the user to confirm the execution of the function and required missing arguments.
"""
        messages = [{"role": "system", "content": prompt}]
        chat_response = chat_completion_request(messages, functions=functions_metadata, n=1)
        response_choice = chat_response.choices[0]

        return jsonify(
            {
                "status": "Success",
                "message": response_choice.message.content,
                "template": {
                    "type": "function_call",
                    "function_name": function_name,
                    "function_arguments": function_arguments
                }
            }
        )
        
    else:
        return jsonify(
            {
                "status": "Success",
                "message": response_choice.message.content
            }
        )

@app.route('/authenticate', methods=['POST'])
def authenticate():
    token_response = confidential_client_app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    if "access_token" in token_response:
        return jsonify(access_token=token_response["access_token"])
    else:
        return jsonify(error=token_response.get("error_description", "Unknown error"))


@app.route('/getembedinfo', methods=['GET'])
def get_embed_info():
    '''Returns report embed configuration'''

    config_result = Utils.check_config(app)
    if config_result is not None:
        return json.dumps({'errorMsg': config_result}), 500

    try:
        embed_info = PbiEmbedService().get_embed_params_for_single_report(app.config['WORKSPACE_ID'], app.config['REPORT_ID'])
        return embed_info
    except Exception as ex:
        return json.dumps({'errorMsg': str(ex)}), 500


@app.route('/autocomplete', methods=['POST'])
def autocomplete():
    try:
        # Get the text input from the request body
        text = request.json.get('text')
        if not text:
            return jsonify({"error": "Missing text input"}), 400
        
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
        return jsonify({"suggestions": suggestions})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/get_job_history', methods=['GET'])
def get_job_history():
    return json.dumps([
    {
        "job_id": "1",
        "job_name": "ingest_data_from_mysql_to_snowflake",
        "job_type": "batch",
        "job_status": "running",
        "job_start_time": "2023-08-05 00:00:00", # today
        "job_engine": "airflow"
    },
    {
        "job_id": "2",
        "job_name": "ingest_data_from_snowflake_to_mysql_on_spark",
        "job_type": "batch",
        "job_status": "running",
        "job_start_time": "2023-08-05 03:00:00",
        "job_engine": "spark"
    },
    {
        "job_id": "3",
        "job_name": "ingest_data_from_snowflake_to_mysql_on_airflow",
        "job_type": "batch",
        "job_status": "completed",
        "job_start_time":"2023-08-05 10:00:00",
        "job_engine": "airflow"
    }
    ])

if __name__ == '__main__':
  app.run()
