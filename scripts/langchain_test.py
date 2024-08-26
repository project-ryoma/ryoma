import json

from langchain.chains import create_sql_query_chain
from langchain_community.tools import QuerySQLDataBaseTool
from langchain_community.utilities import SQLDatabase
from langchain_core.tools import tool
from langchain_core.utils.function_calling import convert_to_openai_tool
from langchain_openai import ChatOpenAI


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers together.

    Args:
        a: First integer
        b: Second integer
    """
    return a * b


# print(json.dumps(convert_to_openai_tool(multiply), indent=2))
#
# llm_with_tool = llm.bind(
#     tools=[convert_to_openai_tool(multiply)],
#     tool_choice={"type": "function", "function": {"name": "multiply"}},
# )
# print(llm_with_tool.invoke(
#     "what's five times four"
# ))


from langchain.chains import create_sql_query_chain
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI

db = SQLDatabase.from_uri("")
# print(db.dialect)
# print(db.get_usable_table_names())
# db.run("SELECT * FROM orders LIMIT 10;")

query_tool = QuerySQLDataBaseTool(db=db)
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0).bind_tools(
    [multiply, query_tool]
)
chain = create_sql_query_chain(llm, db)
response = chain.invoke(
    {"question": "the top 10 customers buying the most number of orders"}
)
print(response)

print(llm.invoke("the top 10 customers buying the most number of orders"))
