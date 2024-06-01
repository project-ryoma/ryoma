from langchain_core.prompts import ChatPromptTemplate

BasicDataSourcePromptTemplate = ChatPromptTemplate.from_messages(
    messages=[("system", """
Given the following data sources schema:
{prompt_context}

Answer the following questions:
""")])
