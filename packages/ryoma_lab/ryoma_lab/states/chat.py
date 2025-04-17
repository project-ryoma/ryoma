import base64
import logging
import pickle
from typing import Any, Iterator, Optional, Union

import reflex as rx
from langchain_core.messages import AIMessage, ToolMessage
from ryoma_ai.agent.base import ChatAgent
from ryoma_ai.agent.embedding import EmbeddingAgent
from ryoma_ai.agent.factory import AgentFactory
from ryoma_ai.agent.workflow import ToolMode, WorkflowAgent
from ryoma_lab.models.tool import Tool, ToolArg, ToolOutput
from ryoma_lab.services.prompt_template import PromptTemplateService
from ryoma_lab.services.vector_store import VectorStoreService
from ryoma_lab.states.prompt_template import PromptTemplate
from ryoma_lab.states.workspace import WorkspaceState
from sqlmodel import delete, select


class QA(rx.Base):
    """A question and answer pair."""

    question: Optional[str]
    answer: Optional[str]


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


class ChatState(WorkspaceState):
    """The app state."""

    # chat states
    chats: dict[str, list[QA]] = DEFAULT_CHATS

    current_chat = "Intros"

    question: str

    new_chat_title: str = ""

    # basic model states
    current_chat_model: str

    # RAG states
    current_embedding_model: Optional[str] = ""

    current_prompt_template: Optional[PromptTemplate] = None

    current_k_shot: int = 0

    current_vector_store: str = ""

    current_vector_feature: str = ""

    # agent states
    current_chat_agent_type: str = ""

    _current_chat_agent: Optional[Union[ChatAgent, WorkflowAgent]] = None

    _current_embedding_agent: Optional[EmbeddingAgent] = None

    _current_chat_agent_state_change: bool = False

    _current_embedding_agent_state_change: bool = False

    # tool states
    current_tool: Optional[Tool] = None

    current_tool_output: Optional[ToolOutput] = None

    # Whether we are processing the question.
    processing: bool = False

    vector_feature_dialog_open: bool = False

    @rx.var
    def current_feature_views(self) -> list[str]:
        if not self.current_vector_store:
            return []
        with VectorStoreService() as vector_store_service:
            all_stores = vector_store_service.load_stores()
            current_store = next(
                (
                    store
                    for store in all_stores
                    if store.project_name == self.current_vector_store
                ),
                None,
            )
            feature_views = vector_store_service.get_feature_views(current_store)
        return [
            f"{feature_view.name}:{feature_view.feature}"
            for feature_view in feature_views
        ]

    def set_current_chat_model(self, chat_model: str):
        if self.current_chat_model != chat_model:
            self.current_chat_model = chat_model
            self._current_chat_agent_state_change = True

    def set_current_chat_agent_type(self, chat_agent_type: str):
        if self.current_chat_agent_type != chat_agent_type:
            self.current_chat_agent_type = chat_agent_type
            self._current_chat_agent_state_change = True

    def set_current_prompt_template(self, prompt_template_name: str):
        with PromptTemplateService() as prompt_template_service:
            self.current_prompt_template = (
                prompt_template_service.get_prompt_template_by_name(
                    prompt_template_name
                )
            )
        self.vector_feature_dialog_open = (
            self.current_prompt_template and self.current_prompt_template.k_shot > 0
        )

    def _create_chat_agent(self, **kwargs):
        if not self._current_chat_agent or self._current_chat_agent_state_change:
            logging.info(
                f"Creating {self.current_chat_agent_type} agent with model {self.current_chat_model}"
            )

            self._current_chat_agent = AgentFactory.create_agent(
                agent_type=self.current_chat_agent_type,
                model=self.current_chat_model,
                **kwargs,
            )
            if self.current_catalog_name:
                datasource = self._get_datasource()
                self._current_chat_agent.add_datasource(datasource)

            logging.info(
                f"Created {self.current_chat_agent_type} agent with model {self.current_chat_model}"
            )
            self._current_chat_agent_state_change = False

    def set_current_embedding_model(self, embedding_model: str):
        if self.current_embedding_model != embedding_model:
            self.current_embedding_model = embedding_model
            self._current_embedding_agent_state_change = True

    def _create_embedding_agent(self):
        if (
            not self._current_embedding_agent
            or self._current_embedding_agent_state_change
        ):
            logging.info(
                f"Creating embedding agent with model {self.current_embedding_model}"
            )
            self._current_embedding_agent = AgentFactory.create_agent(
                agent_type="embedding",
                model=self.current_embedding_model,
                model_parameters=None,
            )
            self._current_embedding_agent_state_change = False

    def set_current_vector_feature(self, vector_feature: str):
        if vector_feature == "new":
            return rx.redirect("/vector_store_project_name")
        self.current_vector_feature = vector_feature

    def should_create_embedding_agent(self):
        if self.current_prompt_template and self.current_prompt_template.k_shot > 0:
            return True

    def update_tool_arg(self, key: str, value: str):
        for arg in self.current_tool.args:
            if arg.name == key:
                arg.value = value

    def cancel_tool(self):
        logging.info(f"Canceling tool {self.current_tool_id}")
        self._current_chat_agent.cancel_tool(self.current_tool_id)

    def create_chat(self):
        """Create a new chat."""
        # Add the new chat to the list of chats.
        self.current_chat = self.new_chat_title
        self.chats[self.new_chat_title] = []
        with rx.session() as session:
            session.add(
                Chat(
                    title=self.new_chat_title,
                    user=self.user.username,
                    question=None,
                    answer=None,
                    description=None,
                    created_at=None,
                    updated_at=None,
                )
            )
            session.commit()

    def delete_chat(self, chat_title: str):
        """Delete the current chat."""
        with rx.session() as session:
            session.exec(delete(Chat).where(Chat.title == chat_title))
            session.commit()
        del self.chats[chat_title]
        self.load_chats()
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

    def _commit_chat(self, title: str, question: str, answer: str):
        with rx.session() as session:
            session.add(
                Chat(
                    title=title,
                    user=self.user.username,
                    question=question,
                    answer=answer,
                    description=None,
                    created_at=None,
                    updated_at=None,
                )
            )
            session.commit()

    async def _process_agent_response(self, events: Iterator[Any]):
        for event in events:
            if hasattr(event, "content"):
                message = event
            else:
                message = event["messages"][-1]
            if isinstance(message, AIMessage):
                self.chats[self.current_chat][-1].answer += message.content
                yield
            elif isinstance(message, ToolMessage):
                if message.artifact is not None and message.artifact != "":
                    encoded_artifact = message.artifact.encode("utf-8")
                    artifact = base64.b64decode(encoded_artifact)
                    result = pickle.loads(artifact)
                    self.current_tool_output = ToolOutput(data=result, show=True)
                yield

    async def _process_agent_state(self):
        chat_state = self._current_chat_agent.get_current_state()
        if chat_state and chat_state.next:
            # having an action/tool to run
            tool_call = self._current_chat_agent.get_current_tool_calls()[0]
            self.current_tool = Tool(
                id=tool_call["id"],
                name=tool_call["name"],
                args=[
                    ToolArg(name=key, value=value)
                    for key, value in tool_call["args"].items()
                ],
            )

            # Add the tool call to the answer
            self.chats[self.current_chat][
                -1
            ].answer += f"\nIn order to assist you further, I need to run a tool. I've added the tool code to a new cell in the notebook for you to review and run."

            # Add a new cell to the notebook with the tool code
            self.add_tool_cell(self.current_tool, self.execute_tool, self.update_tool)

    async def execute_tool(self, tool_id: str, updated_code: str):
        if not self.current_tool or self.current_tool.id != tool_id:
            return

        # Update the tool with the potentially edited code
        self.update_tool(tool_id, updated_code)

        async for _ in self.run_tool():
            yield

    def update_tool(self, tool_id: str, updated_code: str):
        if self.current_tool and self.current_tool.id == tool_id:
            # Parse the updated code to extract new argument values
            new_args = self.parse_tool_code(updated_code)
            for arg in self.current_tool.args:
                if arg.name in new_args:
                    arg.value = new_args[arg.name]

            tool_args = {
                tool_arg.name: tool_arg.value for tool_arg in self.current_tool.args
            }
            self._current_chat_agent.update_tool(self.current_tool.id, tool_args)

    def parse_tool_code(self, code: str) -> dict[str, str]:
        # Implement parsing logic to extract argument values from the code
        # This is a simple example and might need to be more robust
        args = {}
        lines = code.split("\n")
        for line in lines:
            if "=" in line:
                key, value = line.split("=", 1)
                args[key.strip()] = value.strip()
        return args

    async def run_tool(self):
        if not self.current_tool:
            return

        self.processing = True

        # Add an empty question to the list of questions.
        qa = QA(question="", answer="")
        self.chats[self.current_chat].append(qa)

        events = self._current_chat_agent.stream(tool_mode=ToolMode.ONCE, display=False)
        async for _ in self._process_agent_response(events):
            yield

        await self._process_agent_state()

        # Toggle the processing flag.
        self.processing = False

        # commit the chat to the catalog
        self._commit_chat(
            self.current_chat,
            self.chats[self.current_chat][-1].question,
            self.chats[self.current_chat][-1].answer,
        )

    async def process_question(self, form_data: dict[str, str]):
        if not self.current_chat_model:
            yield rx.toast.error("Please select a chat model.")
            return

        # Clear the input and start the processing.
        self.processing = True

        # Get the question from the form
        question = form_data["question"]

        # Check if the question is empty
        if question == "":
            return

        # Add the question to the list of questions.
        qa = QA(question=question, answer="")
        self.chats[self.current_chat].append(qa)

        yield

        logging.info(f"Processing question: {question}")

        if self.current_tool_output:
            logging.info("Adding last tool run to history")
            WorkspaceState.add_tool_run(self.current_tool, self.current_tool_output)
            self.current_tool = None
            self.current_tool_output = None
            yield

        # init the chat agent
        self._create_chat_agent()

        # init the embedding agent
        if self.should_create_embedding_agent():
            self._create_embedding_agent()

            # embed the question
            embedded_question = self._current_embedding_agent.embed_query(question)

            with VectorStoreService() as vector_store_service:
                top_k_features = vector_store_service.retrieve_vector_features(
                    fs=self._current_store,
                    feature=self.current_vector_feature,
                    query=embedded_question,
                    top_k=self.current_k_shot,
                )

            # TODO: add similar features to the prompt template
            self._current_chat_agent.add_prompt_context(top_k_features)

        async for value in self._invoke_agent(question):
            yield

        # Toggle the processing flag.
        self.processing = False

        # commit the chat to the catalog
        self._commit_chat(
            self.current_chat,
            self.chats[self.current_chat][-1].question,
            self.chats[self.current_chat][-1].answer,
        )

    async def _invoke_agent(self, question: Optional[str] = ""):
        """Get the response from the API.

        Args:
            question: The question to ask the API.
        """

        # Get the response and add it to the answer.
        events = self._current_chat_agent.stream(question, display=False)
        async for _ in self._process_agent_response(events):
            yield

        await self._process_agent_state()

    def load_chats(self):
        """Load the chats from the catalog."""
        with rx.session() as session:
            chats = session.exec(
                select(Chat).where(Chat.user == self.user.username)
            ).all()
            for chat in chats:
                if chat.title not in self.chats:
                    self.chats[chat.title] = []
                self.chats[chat.title].append(
                    QA(question=chat.question, answer=chat.answer)
                )
            if not self.chats:
                self.chats = DEFAULT_CHATS

    def on_load(self):
        self.load_chats()
