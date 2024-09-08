import logging
import uuid
from typing import Any, Dict, Optional, Union

from langchain_core.exceptions import OutputParserException
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnableSerializable
from pydantic import BaseModel

from ryoma_ai.agent.utils import load_model_provider
from ryoma_ai.datasource.base import DataSource
from ryoma_ai.datasource.metadata import Catalog
from ryoma_ai.models.agent import AgentType
from ryoma_ai.prompt.prompt_template import PromptTemplateFactory


class RyomaAgent:
    """
    Base class for all agents in Ryoma. Inherits from this class can be used to create custom agents.
    """

    type: AgentType = AgentType.ryoma
    description: str = "Ryoma Agent is your best friend!"


class BaseAgent(RyomaAgent):
    type: AgentType = AgentType.base
    description: str = (
        "Base Agent supports all the basic functionalities of a chat agent."
    )
    config: Dict[str, Any]
    model: RunnableSerializable
    model_parameters: Optional[Dict]
    prompt_template_factory: PromptTemplateFactory
    final_prompt_template: Optional[Union[PromptTemplate, ChatPromptTemplate]]
    output_parser: Optional[PydanticOutputParser]

    def __init__(
        self,
        model: Union[str, RunnableSerializable],
        model_parameters: Optional[Dict] = None,
        base_prompt_template: Optional[PromptTemplate] = None,
        context_prompt_templates: Optional[list[PromptTemplate]] = None,
        output_prompt_template: Optional[PromptTemplate] = None,
        output_parser: Optional[BaseModel] = None,
        **kwargs,
    ):
        logging.info(f"Initializing Agent with model: {model}")

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
            self.model: RunnableSerializable = load_model_provider(
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

    def _build_chain(self, **kwargs) -> RunnableSerializable:
        if not self.model:
            raise ValueError(
                f"Unable to initialize model, please ensure you have valid configurations."
            )
        self.final_prompt_template = self.prompt_template_factory.build_prompt()
        if self.output_parser:
            return self.output_prompt | self.model | self.output_parser
        return self.final_prompt_template | self.model

    def set_base_prompt(
        self, base_prompt: Optional[Union[str, ChatPromptTemplate]] = None
    ):
        self.prompt_template_factory.set_base_prompt(base_prompt)
        return self

    def set_context_prompt(
        self, context: Optional[Union[str, ChatPromptTemplate]] = None
    ):
        self.prompt_template_factory.add_context_prompt(context)
        return self

    def add_prompt_context(self, prompt_context: str):
        self.prompt_template_factory.add_context_prompt(prompt_context)
        return self

    def add_datasource(self, datasource: DataSource):
        self.add_prompt_context(str(datasource.get_metadata()))
        self.final_prompt_template = self.prompt_template_factory.build_prompt()
        return self

    def add_data_catalog(self, catalog: Catalog):
        self.add_prompt_context(str(catalog))
        self.final_prompt_template = self.prompt_template_factory.build_prompt()
        return self

    def _format_messages(self, messages: str):
        return {"messages": [HumanMessage(content=messages)]}

    def stream(self, question: Optional[str] = "", display: Optional[bool] = True):
        messages = self._format_messages(question)
        chain = self._build_chain()
        events = chain.stream(messages, self.config)
        if display:
            for event in events:
                print(event.content, end="", flush=True)
        if self.output_parser:
            chain = self.output_prompt | self.model | self.output_parser
            events = self._parse_output(chain, events)
        return events

    def invoke(self, question: Optional[str] = "", display: Optional[bool] = True):
        messages = self._format_messages(question)
        chain = self._build_chain()
        results = chain.invoke(messages, self.config)
        if display:
            for result in results:
                print(result.content, end="", flush=True)
        if self.output_parser:
            chain = self.output_prompt | self.model | self.output_parser
            results = self._parse_output(chain, results)
        return results

    def get_current_state(self) -> None:
        return None

    def _parse_output(self, chain, result: dict, max_iterations=10):
        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            try:
                return chain.invoke({"messages": result["messages"]}, self.config)
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
        return self
