import os
import langchain
import json
import msal
import openai

from flask_cors import CORS
from dataplatform.setup_agents import setup_llama_agent, setup_gpt_agent
from langchain.schema.messages import messages_to_dict

from flask import (Flask, redirect, render_template, request, jsonify,
                   send_from_directory, url_for)
from utils import Utils
from services.pbiembedservice import PbiEmbedService


confidential_client_app = msal.ConfidentialClientApplication(
    "f85ee12f-73a9-43d4-8453-2db3de7848fd",
    authority="https://login.microsoftonline.com/a60e2d77-3925-4eca-ace0-eecc604d922c",
    client_credential="LTV8Q~iCUw5LAzWLoO_0fWbevUCIgP2s6Ic1lanj",
)

# setup llm agent
langchain.debug = True
llama_agent_wrapper = setup_llama_agent()
gpt_agent_wrapper = setup_gpt_agent()

# setup
app = Flask(__name__)

# Load configuration
app.config.from_object('config.BaseConfig')

CORS(app)

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


@app.route('/chat', methods=['POST'])
def run():
    prompt = request.get_json()["prompt"]
    model = request.get_json()["model"]
    try:
        if model == "llama":
            agent = llama_agent_wrapper["agent"]
            message_history = llama_agent_wrapper["message_history"]
        else:
            agent = gpt_agent_wrapper["agent"]
            message_history = gpt_agent_wrapper["message_history"]
        res = agent.run(prompt)
        message_history.add_user_message(prompt)
        message_history.add_ai_message(res)
    except Exception as e:
        # get the exception message
        if model == "llama":
            agent = llama_agent_wrapper["agent"]
            message_history = llama_agent_wrapper["message_history"]
        else:
            agent = gpt_agent_wrapper["agent"]
            message_history = gpt_agent_wrapper["message_history"]
        res = agent.run(
        f"""
        Get the error message: {str(e)}
        Can you please ask for clarification?
        """
        )
        message_history.add_user_message(prompt)
        message_history.add_ai_message(res)
    return json.dumps(res)


@app.route('/chat_history', methods=['POST'])
def chat_history():
    model = request.get_json()["model"]
    try:
        if model == "llama":
            message_history = llama_agent_wrapper["message_history"]
        else:
            message_history = gpt_agent_wrapper["message_history"]
        res = messages_to_dict(message_history.messages)
    except Exception as e:
        # get the exception message
        if model == "llama":
            message_history = llama_agent_wrapper["message_history"]
        else:
            message_history = gpt_agent_wrapper["message_history"]
        res = messages_to_dict(message_history.messages)
    return json.dumps(res)


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
        
        message_history = []
        for message in gpt_agent_wrapper["message_history"].messages:
            if isinstance(message, langchain.schema.messages.HumanMessage):
                message_history.append({"role": "user", "content": message.content})
        message_history = message_history[-5:]

        prompt = f"""
Complete the sentence: {text}
Using the chat history, please finish the sentence beginning with the input text.
Please include the input text in the sentence.
        """
        
        messages = message_history + [{"role": "user", "content": prompt}]

        # Send a request to the GPT-3 API with the text input
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Or whichever engine you prefer
            messages=messages,
            max_tokens=50,  # You might want to limit the number of tokens to keep suggestions short
            n=3,  # Number of suggestions to generate
            temperature=0.7  # Adjust as needed to control randomness
        )

        # Extract suggestions from the GPT-3 response
        suggestions = [choice['message']['content'].strip() for choice in response['choices']]
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
