import reflex as rx
from langchain_core.messages import HumanMessage


class QA(rx.Base):
    """A question and answer pair."""

    question: str
    answer: str


DEFAULT_CHATS = {
    "Intros": [],
}

from aita.datasource.snowflake import SnowflakeDataSource
from aita.agent.sql import SqlAgent
import os

SNOWFLAKE_USER = os.environ.get("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.environ.get("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ACCOUNT = os.environ.get("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_WAREHOUSE = os.environ.get("SNOWFLAKE_WAREHOUSE")
SNOWFLAKE_DATABASE = os.environ.get("SNOWFLAKE_DATABASE")
SNOWFLAKE_SCHEMA = os.environ.get("SNOWFLAKE_SCHEMA")
SNOWFLAKE_ROLE = os.environ.get("SNOWFLAKE_ROLE")

sf_datasource = SnowflakeDataSource(
    user=SNOWFLAKE_USER,
    password=SNOWFLAKE_PASSWORD,
    account=SNOWFLAKE_ACCOUNT,
    warehouse=SNOWFLAKE_WAREHOUSE,
    database=SNOWFLAKE_DATABASE,
    schema=SNOWFLAKE_SCHEMA,
    role=SNOWFLAKE_ROLE,
)

sql_agent = SqlAgent(sf_datasource, "gpt-3.5-turbo", allow_extract_metadata=True)


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

    current_model: str = "gpt-3.5-turbo"

    current_datasource: str = "datasource1"

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

    async def process_question(self, form_data: dict[str, str]):
        # Get the question from the form
        question = form_data["question"]

        # Check if the question is empty
        if question == "":
            return

        async for value in self.aita_process_question(question):
            yield value

    async def aita_process_question(self, question: str):
        """Get the response from the API.

        Args:
            form_data: A dict with the current question.
        """

        # Add the question to the list of questions.
        qa = QA(question=question, answer="")
        self.chats[self.current_chat].append(qa)

        # Clear the input and start the processing.
        self.processing = True
        yield

        for result in sql_agent.chat(question, display=False):
            message = result.get("messages")
            if not message:
                continue
            if isinstance(message, list):
                message = message[-1]
            if not isinstance(message, HumanMessage):
                self.chats[self.current_chat][-1].answer += message.content
            yield

        # Toggle the processing flag.
        self.processing = False
