import logging
import uuid

from jupyter_ai_magics.providers import *
from langchain_core.exceptions import OutputParserException
from langchain_core.messages import AIMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableSerializable

from aita.agent.utils import get_model
from aita.datasource.base import DataSource
from aita.datasource.metadata import Catalog
from aita.prompt.prompt_template import PromptTemplateFactory


class AitaAgent:
    type: str = "aita"
    description: str = "Aita Agent is your best friend!"
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
            self.model: RunnableSerializable = get_model(model, model_parameters)
        else:
            self.model = model

        # prompt
        self.prompt_template_factory = PromptTemplateFactory(
            base_prompt_template,
            context_prompt_templates,
            output_prompt_template,
        )
        self.final_prompt_template = None
        self.output_parser = output_parser

    def _create_chain(self, **kwargs) -> RunnableSerializable:
        if self.output_parser:
            return self.output_prompt | self.model | self.output_parser
        return self.final_prompt_template | self.model

    def set_base_prompt(self, base_prompt: Optional[Union[str, ChatPromptTemplate]] = None):
        self.prompt_template_factory.set_base_prompt(base_prompt)
        return self

    def set_context_prompt(self, context: Optional[Union[str, ChatPromptTemplate]] = None):
        self.prompt_template_factory.add_context_prompt(context)
        return self

    def add_prompt_context(self, prompt_context: str):
        self.prompt_template_factory.add_context_prompt(prompt_context)
        return self

    def add_datasource(self, datasource: DataSource):
        self.add_prompt_context(str(datasource.get_metadata()))
        return self

    def add_data_catalog(self, catalog: Catalog):
        self.add_prompt_context(str(catalog))
        return self

    def _build_prompt(self, question: str):
        self.final_prompt_template = self.prompt_template_factory.build_prompt()
        self.final_prompt_template.append(("user", question))

    def stream(self, question: Optional[str] = "", display: Optional[bool] = True):
        self._build_prompt(question)
        chain = self._create_chain()
        events = chain.stream(self.config)
        if display:
            for event in events:
                print(event.content, end="", flush=True)
        if self.output_parser:
            chain = self.output_prompt | self.model | self.output_parser
            events = self._parse_output(chain, events)
        return events

    def invoke(self, question: Optional[str] = "", display: Optional[bool] = True):
        self._build_prompt(question)
        chain = self._create_chain()
        results = chain.invoke(self.config)
        if display:
            for result in results:
                print(result.content, end="", flush=True)
        if self.output_parser:
            chain = self.output_prompt | self.model | self.output_parser
            results = self._parse_output(chain, results)
        return results

    def embed(self, query: str) -> list:
        assert hasattr(self.model, "embed"), "Model does not support embedding"
        return self.model.embed(query)

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
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()},
        )
        return self
