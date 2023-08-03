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

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)


# setup llm agent
langchain.debug = True
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")
agent_kwargs = {
    "extra_prompt_messages": [MessagesPlaceholder(variable_name="memory")],
}
memory = ConversationBufferMemory(memory_key="memory", return_messages=True)
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
    agent_kwargs=agent_kwargs,
    memory=memory
)

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
    try:
        res = agent.run(prompt)
    except Exception as e:
        # get the exception message
        res = agent.run(
        f"""
        Get the error message: {str(e)}
        Can you please ask for clarification?
        """
        )

    return json.dumps(res)

if __name__ == '__main__':
  app.run()
