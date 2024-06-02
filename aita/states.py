from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from typing import Annotated


class MessageState(TypedDict):
    messages: Annotated[list, add_messages]

    def human_message(self, content: str):
        return [message for message in self.messages if isinstance(message, HumanMessage)]

    def ai_message(self, content: str):
        return [message for message in self.messages if isinstance(message, AIMessage)]
