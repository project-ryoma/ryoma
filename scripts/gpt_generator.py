
# create a gpt generator that can generate code snippets based on input prompt

import openai


prompt = "create a python snowflake connector which complete the following data source class:"
prompt += "\n\n"
f = open("./monorepo/scripts/datasource.txt", "r")
prompt += f.read()

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

print(response.choices[0].message["content"])



