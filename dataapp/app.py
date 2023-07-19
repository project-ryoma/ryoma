import os
from langchain import OpenAI, LLMChain
from langchain.prompts import PromptTemplate
from dataplatform.snowflake_client import SnowflakeClient


from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)


# get snowflake configs from environment variables
snowflake_user = os.environ.get('SNOWFLAKE_USER', "")
snowflake_password = os.environ.get('SNOWFLAKE_PASSWORD', "")
snowflake_account = os.environ.get('SNOWFLAKE_ACCOUNT', "")

app = Flask(__name__)


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
    llm = OpenAI(model="gpt-3.5-turbo")
    prompt = request.form.get('prompt')
    prompt_template = PromptTemplate.from_template("Create a sql query with the context: {context}")
    prompt_template.format(context=prompt)
    chain = LLMChain(llm=llm, prompt=prompt_template)
    query = chain.run(prompt)

    snowflake_client = SnowflakeClient(snowflake_user, snowflake_password, snowflake_account)

    if query:
         print('Request for query page received with query=%s' % query)
         return render_template('query.html', query = query, results = snowflake_client.run_query(query))
    else:
         print('Request for query page received with no query or blank query -- redirecting')
         return redirect(url_for('index'))


if __name__ == '__main__':
  app.run()
