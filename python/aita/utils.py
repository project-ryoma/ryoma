import os
from openai import ChatCompletion, OpenAI, OpenAIError


client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)


def chat_completion_request(
    messages, functions=None, max_tokens=1000, n=3, temperature=0.7
) -> ChatCompletion:
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0613",
            messages=messages,
            max_tokens=max_tokens,
            n=n,
            temperature=temperature,
            functions=functions,
        )
        return response
    except OpenAIError as e:
        return e
