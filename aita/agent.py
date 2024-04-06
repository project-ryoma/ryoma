import os
from operator import itemgetter
from typing import Union, Dict, List

import pandas as pd
from langchain.output_parsers import JsonOutputToolsParser
from langchain_core.runnables import Runnable, RunnablePassthrough, RunnableLambda
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from aita.tools import QuerySQLDataBaseTool, PandasTool, PythonTool, ExtractMetadataTool
from datasource.base import SqlDataSource


class AitaAgent:
    model: str
    temperature: float
    tool_registry: Dict[str, BaseTool]

    base_prompt_template = """
    context: {prompt_context}

    question: {question}
    """

    def __init__(self, model, temperature, tools, prompt_context=None):
        self.model = model
        self.temperature = temperature
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.tool_registry = {}
        self.prompt_context = prompt_context
        if tools:
            self.llm = self.llm.bind_tools(tools)
            print(self.llm)
            self.register_tools(tools)

    def register_tools(self, tools):
        for tool in tools:
            self.tool_registry[tool.name] = tool

    def chat(self, question, allow_call_tool=False):
        prompt = self.base_prompt_template.format(
            prompt_context=self.prompt_context,
            question=question
        )
        chat_response = self.llm.invoke(prompt)
        print(chat_response)

        if "tool_calls" in chat_response.additional_kwargs and allow_call_tool:
            call_tool_list = RunnableLambda(self.call_tool).map()
            chain = self.llm | JsonOutputToolsParser() | call_tool_list
            return chain.invoke(prompt)
        return chat_response

    def call_tool(self, tool_invocation: dict) -> Union[str, Runnable]:
        """Function for dynamically constructing the end of the chain based on the model-selected tool."""
        tool = self.tool_registry[tool_invocation["type"]]
        return RunnablePassthrough.assign(output=itemgetter("args") | tool)


class AitaSqlAgent(AitaAgent):
    db: SqlDataSource

    prompt_context = """
    database metadata: {metadata}
    """

    def __init__(self, db, model, temperature, allow_extract_metadata=False):
        tools = [
            QuerySQLDataBaseTool(db=db),
            ExtractMetadataTool(db=db)
        ]
        if allow_extract_metadata:
            metadata = db.get_metadata()
            self.prompt_context = self.prompt_context.format(metadata=metadata)
        super().__init__(model, temperature, tools, prompt_context=self.prompt_context)


class AitaPythonAgent(AitaAgent):
    def __init__(self, model, temperature):
        super().__init__(model, temperature, [PythonTool()])


class AitaPandasAgent(AitaAgent):
    dataframes: List[pd.DataFrame]

    prompt_context = """
    Meta data of all available data source as pandas dataframe:
    {dataframe_metadata}
    """

    def __init__(self, dataframes: Dict[str, pd.DataFrame], model, temperature):
        tool = PandasTool(script_context=dataframes)
        dataframe_metadata = []
        for name, df in dataframes.items():
            dataframe_metadata.append({
                "name": name,
                "columns": df.columns.tolist()
            })
        self.prompt_context = self.prompt_context.format(dataframe_metadata=dataframe_metadata)
        super().__init__(model, temperature, [tool], prompt_context=self.prompt_context)


os.environ["OPENAI_API_KEY"] = "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"

# snowflake_uri = "snowflake://aita:Xh!0135259098@xl62897.us-east-2.aws?warehouse=COMPUTE_WH&database=SNOWFLAKE_SAMPLE_DATA&schema=TPCH_SF1&role=PUBLIC_ROLE"
# db = SQLDatabase.from_uri(snowflake_uri)

from aita.datasource.snowflake import SnowflakeDataSource

db = SnowflakeDataSource(
    user="AITA",
    password="Xh!0135259098",
    account="qlezend-pu83508",
    warehouse="COMPUTE_WH",
    database="SNOWFLAKE_SAMPLE_DATA",
    schema="TPCH_SF1",
    role="PUBLIC_ROLE"
)
# print(db.execute("SELECT * FROM CUSTOMER limit 10"))

# from aita.datasource.postgresql import PostgreSqlDataSource
#
# db = PostgreSqlDataSource(
#     user="",
#     password="",
#     host="localhost",
#     port="5432",
#     database="aita"
# )

# sql_agent = AitaSqlAgent(db, "gpt-3.5-turbo", 0.8, allow_extract_metadata=True)
# print(sql_agent.chat("I want to get the top customers which making the most purchases", allow_call_tool=True))
# print(sql_agent.chat("extract snowflake data source metadata", allow_call_tool=True))

df1 = db.to_pandas("SELECT * FROM CUSTOMER")

pandas_agent = AitaPandasAgent({"df1": df1}, "gpt-3.5-turbo", 0.8)
print(pandas_agent.chat("find the top 5 customers make the most purchases", allow_call_tool=True))

# python_agent = AitaPythonAgent(db, "gpt-3.5-turbo", 0.8, {})
# python_agent.chat("python code to show the customers data with snowflake database as data source", allow_call_tool=True)
