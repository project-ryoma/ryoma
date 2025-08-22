import logging
import uuid
from typing import Any, Dict, Optional, Union

from langchain_core.embeddings import Embeddings
from langchain_core.exceptions import OutputParserException
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnableSerializable
from pydantic import BaseModel
from ryoma_ai.agent.base import BaseAgent
from ryoma_ai.datasource.base import DataSource
from ryoma_ai.llm.provider import load_model_provider
from ryoma_ai.models.agent import AgentType

# from ryoma_ai.prompt import prompt_manager, PromptType  # Available for future use
from ryoma_ai.prompt.prompt_template import PromptTemplateFactory
from ryoma_ai.vector_store.base import VectorStore


class ChatAgent(BaseAgent):
    type: AgentType = AgentType.chat
    description: str = (
        "Chat Agent supports all the basic functionalities of a chat agent."
    )
    config: Dict[str, Any]
    model: BaseChatModel
    model_parameters: Optional[Dict]
    prompt_template_factory: PromptTemplateFactory
    final_prompt_template: Optional[Union[PromptTemplate, ChatPromptTemplate]]
    output_parser: Optional[PydanticOutputParser]

    def __init__(
        self,
        model: Union[str, BaseChatModel],
        model_parameters: Optional[Dict] = None,
        base_prompt_template: Optional[PromptTemplate] = None,
        context_prompt_templates: Optional[list[PromptTemplate]] = None,
        output_prompt_template: Optional[PromptTemplate] = None,
        output_parser: Optional[BaseModel] = None,
        datasource: Optional[DataSource] = None,
        embedding: Optional[Union[dict, Embeddings]] = None,
        vector_store: Optional[Union[dict, VectorStore]] = None,
        **kwargs,
    ):
        logging.info(f"Initializing Agent with model: {model}")

        super().__init__(
            datasource=datasource,
            embedding=embedding,
            vector_store=vector_store,
            **kwargs,
        )

        # configs
        self.config = {
            "configurable": {
                "user_id": kwargs.get("user_id", str(uuid.uuid4())),
                "thread_id": kwargs.get("thread_id", str(uuid.uuid4())),
            }
        }

        # model
        self.model_parameters = model_parameters
        if isinstance(model, str):
            self.model: BaseChatModel = load_model_provider(
                model, model_parameters=model_parameters
            )
        else:
            self.model = model

        # prompt
        self.prompt_template_factory = PromptTemplateFactory(
            base_prompt_template,
            context_prompt_templates,
            output_prompt_template,
        )
        self.final_prompt_template = self.prompt_template_factory.build_prompt()
        self.output_parser = output_parser

        # chain (lazy initialization)
        self._chain = None

    def _build_chain(self, **kwargs) -> RunnableSerializable:
        logging.info(f"Building llm chain with model: {self.model}")
        if not self.model:
            raise ValueError(
                "Unable to initialize model, please ensure you have valid configurations."
            )
        self.final_prompt_template = self.prompt_template_factory.build_prompt()
        if self.output_parser:
            return self.output_prompt | self.model | self.output_parser
        return self.final_prompt_template | self.model

    @property
    def chain(self) -> RunnableSerializable:
        """Lazy initialization of the chain. Built only once when first accessed."""
        if self._chain is None:
            self._chain = self._build_chain()
        return self._chain

    def set_base_prompt(
        self, base_prompt: Optional[Union[str, ChatPromptTemplate]] = None
    ):
        self.prompt_template_factory.set_base_template(base_prompt)
        self._chain = None  # Invalidate chain to force rebuild
        return self

    def add_prompt(self, prompt: Optional[Union[str, ChatPromptTemplate]]):
        self.prompt_template_factory.add_context_template(prompt)
        self._chain = None  # Invalidate chain to force rebuild
        return self

    def _format_messages(self, messages: str):
        return {"messages": [HumanMessage(content=messages)]}

    def _add_retrieval_context(self, query: str, top_k: int = 5):
        if not self.vector_store:
            raise ValueError(
                "Unable to initialize vector store, please ensure you have valid configurations."
            )
        top_k_columns = self.vector_store.retrieve_columns(query, top_k=top_k)
        if not top_k_columns:
            raise ValueError("Unable to retrieve top k columns from vector store.")
        self.add_prompt(f"Top-K context from vector store: {top_k_columns}")

    def stream(
        self,
        question: Optional[str] = "",
        display: Optional[bool] = True,
    ):
        messages = self._format_messages(question)
        events = self.chain.stream(messages, self.config)
        if display:
            print("\n", end="", flush=True)  # Start with newline for clean display
            for event in events:
                if hasattr(event, "content") and event.content:
                    print(event.content, end="", flush=True)
            print()  # Add final newline after streaming completes
        if self.output_parser:
            events = self._parse_output(self.chain, events)
        return events

    def invoke(
        self,
        question: Optional[str] = "",
        display: Optional[bool] = True,
    ):
        messages = self._format_messages(question)

        results = self.chain.invoke(messages, self.config)
        if display:
            for result in results:
                print(result.content, end="", flush=True)
        if self.output_parser:
            results = self._parse_output(self.chain, results)
        return results

    def chat(
        self,
        question: Optional[str] = "",
        display: Optional[bool] = True,
        stream: Optional[bool] = False,
    ):
        if stream:
            return self.stream(question, display)
        return self.invoke(question, display)

    def _parse_output(self, agent, result: dict, max_iterations=10):
        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            try:
                return agent.invoke({"messages": result["messages"]}, self.config)
            except OutputParserException as e:
                result["messages"] += [
                    AIMessage(
                        content=f"Error: {repr(e)}\n please fix your mistakes.",
                    )
                ]
        return result

    def set_output_parser(self, output_parser: BaseModel):
        self.output_parser = PydanticOutputParser(pydantic_object=output_parser)
        self.output_prompt = PromptTemplate(
            template="Return output in required format with given messages.\n{format_instructions}\n{messages}\n",
            input_variables=["messages"],
            partial_variables={
                "format_instructions": self.output_parser.get_format_instructions()
            },
        )
        self._chain = None  # Invalidate chain to force rebuild
        return self
