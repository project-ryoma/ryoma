from typing import Optional, Union

import logging

import pandas as pd
import reflex as rx
from langchain_core.messages import HumanMessage
from pandas import DataFrame

from sqlmodel import select
from aita.agent.base import AitaAgent
from aita.agent.factory import AgentFactory
from aita.agent.graph import GraphAgent
from aita_lab.states.datasource import DataSourceState
from aita_lab.states.tool import Tool
from aita_lab.states.base import BaseState


class QA(rx.Base):
    """A question and answer pair."""

    question: Optional[str]
    answer: Optional[str]


class RunToolOutput(rx.Base):
    data: pd.DataFrame
    show: bool = False


class Chat(rx.Model, table=True):
    """Chat Model"""

    title: str
    user: str
    question: Optional[str]
    answer: Optional[str]
    description: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]


DEFAULT_CHATS = {
    "Intros": [],
}


class ChatState(BaseState):
    """The app state."""

    chats: dict[str, list[QA]] = DEFAULT_CHATS

    # The current chat title.
    current_chat = "Intros"

    # The current question.
    question: str

    # Whether we are processing the question.
    processing: bool = False

    # The name of the new chat.
    new_chat_title: str = ""

    current_model: str

    current_datasource: str

    current_prompt_template: str = ""

    _current_agent: Optional[Union[AitaAgent, GraphAgent]] = None

    current_agent_type: str = ""

    current_tools: list[Tool] = []

    current_tool: Optional[Tool] = None

    # create an example dataframe
    run_tool_output: Optional[RunToolOutput] = RunToolOutput(data=pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]}),
                                                             show=True)

    def set_current_tool_by_id(self, tool_id: str):
        logging.info(f"Setting current tool to {tool_id}")
        self.current_tool = next(filter(lambda x: x.id == tool_id, self.current_tools), None)

    def set_current_tool_by_name(self, tool_name: str):
        logging.info(f"Setting current tool to {tool_name}")
        self.current_tool = next(filter(lambda x: x.name == tool_name, self.current_tools), None)

    def set_current_tool_arg(self, tool_id: str, key: str, value: str):
        tool = next(filter(lambda x: x.id == tool_id, self.current_tools), None)
        tool.args[key] = value

    def delete_current_tool(self):
        self.current_tools = [
            tool for tool in self.current_tools if tool.id != self.current_tool.id
        ]
        self.current_tool = None

    def run_tool(self):
        logging.info(f"Running tool {self.current_tool.name} with args {self.current_tool.args}")
        try:
            result = self._current_agent.call_tool(self.current_tool.name, self.current_tool.id)
            print(result)
            if isinstance(result, DataFrame):
                self.run_tool_output = RunToolOutput(data=result, show=True)
        except Exception as e:
            logging.error(f"Error running tool {self.current_tool.name}: {e}")
        finally:
            print(self.run_tool_output)
            self.delete_current_tool()

    def cancel_tool(self):
        logging.info(f"Canceling tool {self.current_tool.name}")
        self._current_agent.cancel_tool(self.current_tool.name, self.current_tool.id)

    def create_chat(self):
        """Create a new chat."""
        # Add the new chat to the list of chats.
        self.current_chat = self.new_chat_title
        self.chats[self.new_chat_title] = []
        with rx.session() as session:
            session.add(
                Chat(
                    title=self.new_chat_title,
                    user=self.user.name,
                    question=None,
                    answer=None,
                    description=None,
                    created_at=None,
                    updated_at=None,
                )
            )
            session.commit()

    def delete_chat(self):
        """Delete the current chat."""
        del self.chats[self.current_chat]
        if len(self.chats) == 0:
            self.chats = []
        self.current_chat = list(self.chats.keys())[0]

    def set_chat(self, chat_title: str):
        """Set the title of the current chat.

        Args:
            chat_title: The name of the chat.
        """
        self.current_chat = chat_title

    @rx.var
    def chat_titles(self) -> list[str]:
        """Get the list of chat titles.

        Returns:
            The list of chat names.
        """
        return list(self.chats.keys())

    def _create_agent(self, **kwargs):
        logging.info(
            f"Creating {self.current_agent_type} agent with model {self.current_model}"
        )
        if not self._current_agent or self._current_agent.type != self.current_agent_type:
            print('here', self.current_agent_type, self.current_model)
            self._current_agent = AgentFactory.create_agent(
                agent_type=self.current_agent_type,
                model=self.current_model,
                **kwargs,
            )

    async def process_question(self, form_data: dict[str, str]):
        # Get the question from the form
        question = form_data["question"]

        # Check if the question is empty
        if question == "":
            return

        logging.info(f"Processing question: {question}")

        self._create_agent()

        if self.current_datasource:
            datasource = DataSourceState.connect(self.current_datasource)
            self._current_agent.add_datasource(datasource)

        async for value in self._invoke_question(question):
            yield value

    async def _invoke_question(self, question: str):
        """Get the response from the API.

        Args:
            question: The question to ask the API.
        """

        # Add the question to the list of questions.
        qa = QA(question=question, answer="")
        self.chats[self.current_chat].append(qa)

        # Clear the input and start the processing.
        self.processing = True
        yield

        # Get the response and add it to the answer.
        events = self._current_agent.stream(question, display=False)
        for event in events:
            if hasattr(event, "content"):
                messages = event
            else:
                messages = event["messages"][-1]
            if not isinstance(messages, HumanMessage):
                self.chats[self.current_chat][-1].answer += messages.content
            yield

        chat_state = self._current_agent.get_current_state()
        if chat_state and chat_state.next:
            # having an action to execute
            for tool_call in self._current_agent.get_current_tool_calls():
                tool = Tool(id=tool_call["id"], name=tool_call["name"], args=tool_call["args"])
                self.current_tools.append(tool)
                if not self.current_tool:
                    self.current_tool = tool

            # Add the tool call to the answer
            self.chats[self.current_chat][-1].answer += \
                f"In order to assist you further, I need to run a tool shown in the kernel. Please confirm to run the tool."

        # Toggle the processing flag.
        self.processing = False

        # commit the chat to the database
        self._commit_chat(self.current_chat, self.chats[self.current_chat][-1].question,
                          self.chats[self.current_chat][-1].answer)

    def _commit_chat(self, title: str, question: str, answer: str):
        with rx.session() as session:
            session.add(
                Chat(
                    title=title,
                    user=self.user.name,
                    question=question,
                    answer=answer,
                    description=None,
                    created_at=None,
                    updated_at=None,
                )
            )
            session.commit()

    def load_chats(self):
        """Load the chats from the database."""
        with rx.session() as session:
            chats = session.exec(select(Chat).where(Chat.user == self.user.name)).all()
            for chat in chats:
                self.chats[chat.title] = [
                    QA(question=chat.question, answer=chat.answer)
                ]
            if not self.chats:
                self.chats = DEFAULT_CHATS

    def on_load(self):
        self.load_chats()
