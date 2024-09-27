from langchain_core.prompts import ChatPromptTemplate

BasePromptTemplate = ChatPromptTemplate.from_messages(
    messages=[
        (
            "system",
            """
You are an expert in the field of data science, analysis, and data engineering.
""",
        )
    ]
)

BasicContextPromptTemplate = ChatPromptTemplate.from_messages(
    messages=[
        (
            "system",
            """
You are provided with the following context:
{prompt_context}

""",
        )
    ]
)
