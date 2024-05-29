from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

BasicPromptTemplate = ChatPromptTemplate.from_messages(
    messages=[("system", """
Given the following data sources schema:
{prompt_context}

Answer the following questions:
"""), MessagesPlaceholder(variable_name="messages", optional=True)])
