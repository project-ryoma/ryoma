from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages


class MessageState(TypedDict):
    messages: Annotated[list, add_messages]
