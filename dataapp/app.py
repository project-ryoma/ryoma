import os
import langchain
import json
from flask_cors import CORS
from dataplatform.setup_agents import setup_llama_agent, setup_gpt_agent
from langchain.schema.messages import messages_to_dict

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)


# setup llm agent
langchain.debug = True
llama_agent_wrapper = setup_llama_agent()
gpt_agent_wrapper = setup_gpt_agent()

# setup
app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')


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

if __name__ == '__main__':
  app.run()


@app.route('/chat_history', methods=['POST'])
def chat_history():
    model = request.get_json()["model"]
    try:
        if model == "llama":
            message_history = llama_agent_wrapper["message_history"]
        else:
            message_history = gpt_agent_wrapper["message_history"]
        res = messages_to_dict(message_history.messages)
        print(res)
    except Exception as e:
        # get the exception message
        if model == "llama":
            message_history = llama_agent_wrapper["message_history"]
        else:
            message_history = gpt_agent_wrapper["message_history"]
        res = messages_to_dict(message_history.messages)
        print(res)
    return json.dumps(res)


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