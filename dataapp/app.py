import os
import langchain
import json
from langchain import LLMChain, LLMMathChain
from langchain.agents import initialize_agent, AgentType
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from dataplatform.snowflake_client import snowflake_client
from dataplatform.tools import tools
from flask_cors import CORS

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)

langchain.debug = True

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


@app.route('/query', methods=['POST'])
def query():
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")

    prompt = request.form.get('prompt')
    prompt_template = PromptTemplate.from_template("Create a sql query with the context: {context}")
    prompt_template.format(context=prompt)
    chain = LLMChain(llm=llm, prompt=prompt_template)
    query = chain.run(prompt)

    if query:
         print('Request for query page received with query=%s' % query)
         return render_template('query.html', query = query, results = snowflake_client.run_query(query))
    else:
         print('Request for query page received with no query or blank query -- redirecting')
         return redirect(url_for('index'))


@app.route('/chat', methods=['POST'])
def run():
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")
    llm_math_chain = LLMMathChain.from_llm(llm=llm, verbose=True)
    agent = initialize_agent(tools, llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=True)

    prompt = request.form.get('prompt')
    print('prompt here', prompt)
    res = agent.run(prompt)

    return json.dumps(res)

if __name__ == '__main__':
  app.run()
