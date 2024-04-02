from operator import itemgetter
from typing import Union, Dict

from langchain.output_parsers import JsonOutputToolsParser
from langchain_core.runnables import Runnable, RunnablePassthrough, RunnableLambda
from langchain_community.utilities import SQLDatabase
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI


from aita.datasource.base import SqlDataSource
from aita.tools import QuerySQLDataBaseTool


class AitaAgent:
    model: str
    temperature: float
    tool_registry: Dict[str, BaseTool]

    def __init__(self, model, temperature, tools, configs):
        self.model = model
        self.temperature = temperature
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.configs = configs
        self.tool_registry = {}
        if tools:
            self.llm = self.llm.bind_tools(tools)
            self.register_tools(tools)

    def register_tools(self, tools):
        for tool in tools:
            self.tool_registry[tool.name] = tool

    def chat(self, question, allow_call_tool=False):
        chat_response = self.llm.invoke(question)
        print(chat_response)

        # check if config has allow_call_tool, always use config value if it exists
        if "allow_call_tool" in self.configs:
            allow_call_tool = self.configs["allow_call_tool"]

        if "tool_calls" in chat_response.additional_kwargs and allow_call_tool:
            call_tool_list = RunnableLambda(self.call_tool).map()
            chain = self.llm | JsonOutputToolsParser() | call_tool_list
            return chain.invoke(question)
        return chat_response

    def call_tool(self, tool_invocation: dict) -> Union[str, Runnable]:
        """Function for dynamically constructing the end of the chain based on the model-selected tool."""
        tool = self.tool_registry[tool_invocation["type"]]
        return RunnablePassthrough.assign(output=itemgetter("args") | tool)


class AitaSqlAgent(AitaAgent):
    db: SqlDataSource

    def __init__(self, datasource: SqlDataSource, model, temperature, configs):
        db = SQLDatabase(engine=datasource.engine)
        tool = QuerySQLDataBaseTool(db=db)
        super().__init__(model, temperature, [tool], configs)

