from langchain import HuggingFaceHub
import os
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from dataplatform.tools import tools, string_tools
from langchain.agents import initialize_agent, AgentType
from langchain.prompts import MessagesPlaceholder
from langchain.chat_models import ChatOpenAI
 
HUGGINGFACEHUB_API_TOKEN = "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"

import os
os.environ["HUGGINGFACEHUB_API_TOKEN"] = HUGGINGFACEHUB_API_TOKEN

# message_history = SQLChatMessageHistory(
#     connection_string=connection_string,
#     session_id="session id that you sent from frontend or client side/ you can use string as well like test1 for testing"
# )
memory = ConversationBufferMemory(
    memory_key="memory",
    return_messages=True,
    # message_history=message_history
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
        memory=memory
    )
    return agent
    

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
    return agent