import os
import langchain
import json
from langchain.agents import initialize_agent, AgentType
from langchain.prompts import MessagesPlaceholder
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from dataplatform.snowflake_client import snowflake_client
from dataplatform.tools import tools
from flask_cors import CORS
from langchain.memory import SQLChatMessageHistory
from dataplatform.setup_agents import setup_llama_agent, setup_gpt_agent

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)


# setup llm agent
langchain.debug = True
llama_agent = setup_llama_agent()
gpt_agent = setup_gpt_agent()

# read configs from environment variables and connection_string to mysql database
MYSQL_HOST = os.environ.get("MYSQL_HOST", "")
MYSQL_PORT = os.environ.get("MYSQL_PORT", "3306")
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
MYSQL_MEMORY_DATABASE = os.environ.get("MYSQL_MEMORY_DATABASE", "memory")
SSL_MODE = os.environ.get("SSL_MODE")

connection_string = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}?{MYSQL_MEMORY_DATABASE}"

if SSL_MODE:
    connection_string += f"?ssl={SSL_MODE}"

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
            agent = llama_agent
        else:
            agent = gpt_agent
        res = agent.run(prompt)
    except ValueError as e:
        res = str(e)
        print('here')
        if res.startswith("Could not parse LLM output: `"):
            res= res.removeprefix("Could not parse LLM output: `").removesuffix("`")
    except Exception as e:
        # get the exception message
        if model == "llama":
            agent = llama_agent
        else:
            agent = gpt_agent
        res = agent.run(
        f"""
        Get the error message: {str(e)}
        Can you please ask for clarification?
        """
        )


    return json.dumps(res)

if __name__ == '__main__':
  app.run()
