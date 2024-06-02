import logging
from abc import abstractmethod

import reflex as rx

from aita.agent.base import AitaAgent
from aita.agent.factory import AgentFactory
from aita.datasource.base import DataSource
from aitalab.states.datasource import DataSourceState
from aitalab.states.prompt_template import PromptTemplateState
from aitalab.states.tool import Tool


class QA(rx.Base):
    """A question and answer pair."""

    question: str
    answer: str


DEFAULT_CHATS = {
    "Intros": [],
}


class ChatState(rx.State):
    """The app state."""

    # A dict from the chat name to the list of questions and answers.
    chats: dict[str, list[QA]] = DEFAULT_CHATS

    # The current chat name.
    current_chat = "Intros"

    # The current question.
    question: str

    # Whether we are processing the question.
    processing: bool = False

    # The name of the new chat.
    new_chat_name: str = ""

    current_model: str

    current_datasource: str

    current_prompt_template: str = ""

    _current_agent: AitaAgent = None

    current_agent_type: str = ""

    current_tools: list[Tool] = [Tool(id="1", name="Create Table", args={"query": "select *"})]

    current_tool_ids: list[str] = ["1"]

    current_tool: str

    def set_current_tool_arg(self, tool_id: str, key: str, value: str):
        tool = next(filter(lambda x: x.id == tool_id, self.current_tools), None)
        tool.args[key] = value

    def add_tool(self, tool: Tool):
        self.current_tools.append(tool)

    @abstractmethod
    def run_tool(self):
        tool = next(filter(lambda x: x.id == self.current_tool, self.current_tools), None)
        if tool:
            tool.run()

    @abstractmethod
    def cancel_tool(self):
        tool = next(filter(lambda x: x.id == self.current_tool, self.current_tools), None)
        if tool:
            tool.cancel()

    def create_chat(self):
        """Create a new chat."""
        # Add the new chat to the list of chats.
        self.current_chat = self.new_chat_name
        self.chats[self.new_chat_name] = []

    def delete_chat(self):
        """Delete the current chat."""
        del self.chats[self.current_chat]
        if len(self.chats) == 0:
            self.chats = DEFAULT_CHATS
        self.current_chat = list(self.chats.keys())[0]

    def set_chat(self, chat_name: str):
        """Set the name of the current chat.

        Args:
            chat_name: The name of the chat.
        """
        self.current_chat = chat_name

    @rx.var
    def chat_titles(self) -> list[str]:
        """Get the list of chat titles.

        Returns:
            The list of chat names.
        """
        return list(self.chats.keys())

    def create_agent(self, datasource: DataSource, prompt: str):
        logging.info(
            f"Creating agent with tool {self.current_agent_type} and model {self.current_model}"
        )
        self._current_agent = AgentFactory.create_agent(
            self.current_agent_type,
            model_id=self.current_model,
            datasource=datasource,
            prompt_context=prompt,
        )

    async def process_question(self, form_data: dict[str, str]):
        # Get the question from the form
        question = form_data["question"]

        # Check if the question is empty
        if question == "":
            return

        logging.info(f"Processing question: {question}")
        print(f"Processing question: {question}")

        # Get the datasource
        if self.current_datasource:
            datasource = DataSourceState.connect(self.current_datasource)
            catalog = datasource.get_metadata()
            target = {
                "catalog": catalog,
                "question": question,
                "db_id": "",
                "path_db": "/Users/haoxu/dev/aita/DAIL-SQL/dataset/spider/database/concert_singer/concert_singer.sqlite",
                "query": "",
            }

            # build prompt
            prompt_template_state = await self.get_state(PromptTemplateState)
            prompt_template = next(
                filter(
                    lambda x: x.prompt_template_name == self.current_prompt_template,
                    prompt_template_state.prompt_templates,
                ),
                None,
            )
            prompt = PromptTemplateState.build_prompt(prompt_template, self.current_model, target)
        else:
            datasource = None
            prompt = ""

        print(f"Coneccted to datasource {self.current_datasource}")
        print(f"Created prompt: {prompt}")

        # create agent
        # if self._current_agent is None:
        #     self._current_agent = SqlAgent(datasource, model_id=self.current_model, prompt_context=prompt)
        self.create_agent(datasource, prompt)
        print(f"Created agent: {self._current_agent}")

        async for value in self.aita_process_question(question):
            yield value

    async def aita_process_question(self, question: str):
        """Get the response from the API.

        Args:
            question: A dict with the current question.
        """

        # Add the question to the list of questions.
        qa = QA(question=question, answer="")
        self.chats[self.current_chat].append(qa)

        # Clear the input and start the processing.
        self.processing = True
        yield

        # Get the response and add it to the answer.
        events = self._current_agent.chat(question, display=False)
        for event in events:
            self.chats[self.current_chat][-1].answer += event.content
            yield

        chat_state = self._current_agent.get_current_state()
        if chat_state and chat_state.next:
            # having an action to execute
            for tool_call in self._current_agent.get_current_tool_calls():
                tool = Tool(id=tool_call["id"], name=tool_call["name"], args=tool_call["args"])
                self.current_tools.append(tool)

            # Add the tool call to the answer
            self.chats[self.current_chat][-1].answer += f"Confirm to run the tool in the panel"

        # Toggle the processing flag.
        self.processing = False
