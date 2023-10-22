from langchain import HuggingFaceHub
from langchain.memory import ConversationBufferMemory
from dataplatform.tools import tools, string_tools
from langchain.agents import initialize_agent, AgentType
from langchain.prompts import MessagesPlaceholder
from langchain.chat_models import ChatOpenAI
from langchain.memory.chat_message_histories import SQLChatMessageHistory
from enum import Enum

HUGGINGFACEHUB_API_TOKEN = "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"

import os
os.environ["HUGGINGFACEHUB_API_TOKEN"] = HUGGINGFACEHUB_API_TOKEN


# read configs from environment variables and connection_string to mysql database
MYSQL_HOST = os.environ.get("AZURE_MYSQL_HOST", "localhost")
MYSQL_PORT = os.environ.get("AZURE_MYSQL_PORT", "3306")
MYSQL_USER = os.environ.get("AZURE_MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("AZURE_MYSQL_PASSWORD", "")
MYSQL_MEMORY_DATABASE = os.environ.get("MYSQL_MEMORY_DATABASE", "memory")
SSL_MODE = os.environ.get("SSL_MODE")

# connection_string = "mysql+pymysql://root:@localhost:3306/memory"
connection_string = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_MEMORY_DATABASE}"
print(connection_string)

if SSL_MODE:
    connection_string += f"?ssl={SSL_MODE}"

message_history = SQLChatMessageHistory(
    connection_string=connection_string,
    session_id="aita"
)

memory = ConversationBufferMemory(
    memory_key="memory",
    return_messages=True,
    message_history=message_history
)
agent_kwargs = {
    "extra_prompt_messages": [MessagesPlaceholder(variable_name="memory")],
}

def setup_llama_agent():
    repo_id = "meta-llama/Llama-2-7b-hf"
    
    llm = HuggingFaceHub(repo_id=repo_id)

    agent = initialize_agent(
        string_tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        agent_kwargs=agent_kwargs,
        memory=memory,
        handle_parsing_errors=True
    )
    return {
        "agent": agent,
        "message_history": message_history,
        "memory": memory
    }

def setup_gpt_agent():
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")

    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=True,
        agent_kwargs=agent_kwargs,
        memory=memory
    )
    return {
        "agent": agent,
        "message_history": message_history,
        "memory": memory
    }


class ModelType(Enum):
    LLAMA = "llama"
    GPT = "gpt"


class AgentWrapper:
    def __init__(self, agent, message_history):
        self.agent = agent
        self.message_history = message_history


class AgentManager:
    def __init__(self, llama_agent_wrapper, gpt_agent_wrapper):
        self.wrappers = {
            ModelType.LLAMA: llama_agent_wrapper,
            ModelType.GPT: gpt_agent_wrapper
        }
        self.current_agent_wrapper = None

    def set_agent(self, model_str):
        try:
            model_type = ModelType[model_str.upper()]
            self.current_agent_wrapper = self.wrappers[model_type]
        except KeyError:
            raise ValueError(f"Invalid model type: {model_str}")

    @property
    def agent(self):
        return self.current_agent_wrapper.agent if self.current_agent_wrapper else None

    @property
    def message_history(self):
        return self.current_agent_wrapper.message_history if self.current_agent_wrapper else None
