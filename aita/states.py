from typing import Annotated
from typing_extensions import TypedDict

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph.message import add_messages


class MessageState(TypedDict):
    messages: Annotated[list, add_messages]

    def human_message(self, content: str):
        return [message for message in self.messages if isinstance(message, HumanMessage)]

    def ai_message(self, content: str):
        return [message for message in self.messages if isinstance(message, AIMessage)]
