# from typing import Literal
# from langchain_community.tools.tavily_search import TavilySearchResults
# from langchain_core.runnables import ConfigurableField
# from langchain_core.tools import tool
# from langchain_openai import ChatOpenAI
# from langgraph.prebuilt import create_react_agent
# import asyncio
#
# @tool
# def get_weather(city: Literal["nyc", "sf"]):
#     """Use this to get weather information."""
#     if city == "nyc":
#         return "It might be cloudy in nyc"
#     elif city == "sf":
#         return "It's always sunny in sf"
#     else:
#         raise AssertionError("Unknown city")
#
#
# tools = [get_weather]
#
# model = ChatOpenAI(model_name="gpt-4o", temperature=0, streaming=True)
# graph = create_react_agent(model, tools)
#
# inputs = {"messages": [("human", "what's the weather in sf")]}
#
#
# async def main():
#     async for event in graph.astream_events(inputs, version="v1"):
#         kind = event["event"]
#         if kind == "on_chat_model_stream":
#             content = event["data"]["chunk"].content
#             if content:
#                 # Empty content in the context of OpenAI or Anthropic usually means
#                 # that the model is asking for a tool to be invoked.
#                 # So we only print non-empty content
#                 print(content, end="|")
#         elif kind == "on_tool_start":
#             print("--")
#             print(
#                 f"Starting tool: {event['name']} with inputs: {event['data'].get('input')}"
#             )
#         elif kind == "on_tool_end":
#             print(f"Done tool: {event['name']}")
#             print(f"Tool output was: {event['data'].get('output')}")
#             print("--")
#
# asyncio.run(main())

a = """
Here are the first 10 rows of the order data:

| O_ORDERKEY | O_CUSTKEY | O_ORDERSTATUS | O_TOTALPRICE | O_ORDERDATE | O_ORDERPRIORITY | O_CLERK | O_SHIPPRIORITY | O_COMMENT |
|------------|-----------|---------------|--------------|-------------|-----------------|---------|----------------|-----------|
| 3000001 | 145618 | F | 30175.88 | 1992-12-17 | 4-NOT SPECIFIED | Clerk#000000141 | 0 | l packages. furiously careful instructions gro... |
| 3000002 | 1481 | O | 297999.63 | 1995-07-28 | 1-URGENT | Clerk#000000547 | 0 | carefully unusual dependencie |
| 3000003 | 127432 | O | 345438.38 | 1997-11-04 | 5-LOW | Clerk#000000488 | 0 | n packages boost slyly bold deposits. deposits... |
| 3000004 | 47423 | O | 135965.53 | 1996-06-13 | 4-NOT SPECIFIED | Clerk#000000004 | 0 | nts wake carefully final decoys. quickly final... |
| 3000005 | 84973 | F | 209937.09 | 1992-09-12 | 5-LOW | Clerk#000000030 | 0 | yly after the quickly unusual ide |
| 3000006 | 135136 | O | 140186.32 | 1996-09-26 | 1-URGENT | Clerk#000000726 | 0 | ronic pinto beans use furiously final, slow no... |
| 3000007 | 78841 | F | 298655.07 | 1992-04-13 | 5-LOW | Clerk#000000871 | 0 | ses eat. deposits wake |
| 3000032 | 124576 | F | 175973.90 | 1992-03-02 | 1-URGENT | Clerk#000000460 | 0 | lar deposits mold carefully against the dep |
| 3000033 | 30247 | F | 4635.38 | 1993-11-10 | 1-URGENT | Clerk#000000923 | 0 | mes special packages nag quickly. |
| 3000034 | 5498 | F | 348308.79 | 1992-04-21 | 1-URGENT | Clerk#000000418 | 0 | lly final packages are slyly beyond the reques... |
"""
b = ""
for c in a:
    b += c
    print(b)
