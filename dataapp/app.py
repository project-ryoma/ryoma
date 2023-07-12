import os
from langchain import OpenAI, LLMChain
from snowflake.connector import connect
from langchain.prompts import PromptTemplate


from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)

app = Flask(__name__)

llm = OpenAI(temperature=0)

conn = connect(
    user='admin',
    password='password',
    account='langchain.us-east-1',
)

def run_query(query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


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
    raw_prompt = request.form.get('prompt')
    prompt = PromptTemplate.from_template("Create a sql query with the context: {context}")
    prompt.format(context=raw_prompt)
    chain = LLMChain(llm=llm, prompt=prompt)
    query = chain.run(prompt)
    
    if query:
         print('Request for query page received with query=%s' % query)
         return render_template('query.html', query = query, results = run_query(query))
    else:
         print('Request for query page received with no query or blank query -- redirecting')
         return redirect(url_for('index'))


if __name__ == '__main__':
   app.run()
