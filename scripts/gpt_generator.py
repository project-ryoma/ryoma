
# create a gpt generator that can generate code snippets based on input prompt

import openai

db = "postgresql"
prompt = f"""
Create a python {db} connector which inherit and implement the following data source abstract class:
"""
prompt += "\n\n"
f = open("./monorepo/scripts/datasource.txt", "r")
prompt += f.read()

prompt += "\n\n"
prompt += """
Example:

import mysql.connector
import os
from dataplatform.datasource.datasource_client import DataSourceClient


class MysqlClient(DataSourceClient):
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        conn = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        return conn        

    def run_query(self, query):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()

# get mysql configs from environment variables
mysql_host = os.environ.get('MYSQL_HOST', "")
mysql_user = os.environ.get('MYSQL_USER', "")
mysql_password = os.environ.get('MYSQL_PASSWORD', "")
mysql_database = os.environ.get('MYSQL_DATABASE', "")

mysql_client = MysqlClient(mysql_host, mysql_user, mysql_password, mysql_database)
"""

prompt += "\n\n"
prompt += "Only return the generated code."

print(prompt)

api_key = "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"
openai.api_key = api_key

# chatgpt api
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    max_tokens=1000,
    temperature=0.9,
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
)

message = response.choices[0].message["content"]

# write to file at location ./monorepo/dataapp/dataplatform/datasource
with open(f"./monorepo/dataapp/dataplatform/datasource/{db}_client.py", "w") as f:
    f.write(message)




