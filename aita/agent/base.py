import uuid

from jupyter_ai_magics.providers import *
from langchain_core.exceptions import OutputParserException
from langchain_core.messages import AIMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableSerializable

from aita.agent.utils import get_model
from aita.datasource.base import DataSource
from aita.datasource.catalog import Catalog
from aita.prompt.base import BasePromptTemplate, BasicContextPromptTemplate


class AitaAgent:
    type: str = "aita"
    description: str = "Aita Agent is your best friend!"
    config: Dict[str, Any]
    model: RunnableSerializable
    model_parameters: Optional[Dict]
    prompt_template: Optional[ChatPromptTemplate]
    context_prompt: Optional[ChatPromptTemplate]
    context_prompt_template: List[ChatPromptTemplate]
    output_prompt: Optional[PromptTemplate]
    output_parser: Optional[PydanticOutputParser]

    def __init__(
        self,
        model: Union[str, RunnableSerializable],
        model_parameters: Optional[Dict] = None,
        **kwargs,
    ):
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
        self.prompt_template = None
        self.base_prompt = self._set_base_prompt()
        self.context_prompt_template = []
        self.context_prompt = self._set_context_prompt()
        self.output_prompt = None
        self.output_parser = None

    def _create_chain(self, **kwargs) -> RunnableSerializable:
        if self.output_parser:
            return self.output_prompt | self.model | self.output_parser
        return self.prompt_template | self.model

    @staticmethod
    def _set_base_prompt(base_prompt: Optional[Union[str, ChatPromptTemplate]] = None):
        if not base_prompt:
            base_prompt = BasePromptTemplate
        if isinstance(base_prompt, str):
            base_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", base_prompt),
                ]
            )
        return base_prompt

    def set_base_prompt(self, base_prompt: Optional[Union[str, ChatPromptTemplate]] = None):
        self.base_prompt = self._set_base_prompt(base_prompt)
        return self

    @staticmethod
    def _set_context_prompt(context_prompt: Optional[Union[str, ChatPromptTemplate]] = None):
        if not context_prompt:
            context_prompt = BasicContextPromptTemplate
        if isinstance(context_prompt, str):
            context_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", context_prompt),
                ]
            )
        return context_prompt

    def set_context_prompt(self, context_prompt: Optional[Union[str, ChatPromptTemplate]] = None):
        self.context_prompt = self._set_context_prompt(context_prompt)
        return self

    def add_prompt_context(self, prompt_context: str):
        context_prompt = self.context_prompt.partial(
            prompt_context=prompt_context
        )
        self.context_prompt_template.append(context_prompt)

    def add_datasource(self, datasource: DataSource):
        self.add_prompt_context(str(datasource.get_metadata()))
        return self

    def add_data_catalog(self, catalog: Catalog):
        self.add_prompt_context(str(catalog))
        return self

    def _build_prompt(self, question: str):
        self.prompt_template = ChatPromptTemplate.from_messages(self.base_prompt.messages)
        self.prompt_template.extend(self.context_prompt_template)
        self.prompt_template.append(("user", question))

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
