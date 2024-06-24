import uuid

from jupyter_ai_magics.providers import *
from jupyter_ai_magics.utils import decompose_model_id, get_lm_providers
from langchain_core.exceptions import OutputParserException
from langchain_core.messages import AIMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableSerializable

from aita.datasource.base import DataSource
from aita.datasource.catalog import Catalog


def get_model(model_id: str, model_parameters: Optional[Dict]) -> Optional[RunnableSerializable]:
    providers = get_lm_providers()
    provider_id, local_model_id = decompose_model_id(model_id, providers)
    if provider_id is None or provider_id not in providers:
        return None
    Provider = providers[provider_id]
    provider_params = {"model_id": local_model_id}
    model_parameters = model_parameters or {}
    return Provider(**provider_params, **model_parameters)


class AitaAgent:
    type: str = "aita"
    config: Dict[str, Any]
    model: RunnableSerializable
    model_parameters: Optional[Dict]
    prompt_template: Optional[ChatPromptTemplate]
    prompt_context_template: Optional[ChatPromptTemplate]
    base_prompt_template = """
    You are an expert in the field of data science, analysis, and data engineering.
    """
    base_prompt_context_template = """
    You are provided with the following context:
    {prompt_context}
    """

    def __init__(
        self,
        model: Union[str, RunnableSerializable],
        model_parameters: Optional[Dict] = None,
        **kwargs,
    ):
        self.output_prompt_template = None
        self.output_parser = None
        self.config = {
            "configurable": {
                "user_id": kwargs.get("user_id", str(uuid.uuid4())),
                "thread_id": kwargs.get("thread_id", str(uuid.uuid4())),
            }
        }
        self.model_parameters = model_parameters

        if isinstance(model, str):
            self.model: RunnableSerializable = get_model(model, model_parameters)
        else:
            self.model = model

        self._set_base_prompt_template()
        self.prompt_context_template = None

    def _create_chain(self, **kwargs) -> RunnableSerializable:
        if self.output_parser:
            return self.output_prompt_template | self.model | self.output_parser
        return self.prompt_template | self.model

    def _set_base_prompt_template(self):
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", self.base_prompt_template),
            ]
        )

    def set_base_prompt_template(self, base_prompt_template: str):
        self.base_prompt_template = base_prompt_template
        self._set_base_prompt_template()
        return self

    def _set_base_prompt_context_template(self):
        self.prompt_context_template = ChatPromptTemplate.from_messages(
            [("system", self.base_prompt_context_template)]
        )

    def set_prompt_context(self, prompt_context: Optional[Union[str, ChatPromptTemplate]] = None):
        if isinstance(prompt_context, str):
            prompt_context = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        self.base_prompt_context_template.format(prompt_context=prompt_context),
                    )
                ]
            )
        self.prompt_context_template = prompt_context
        return self

    def _format_question(self, question: str):
        self.prompt_template.append(("user", question))

    def _fill_prompt_context(self, prompt_context: str):
        if not self.prompt_context_template:
            self._set_base_prompt_context_template()
        prompt_context_template = self.prompt_context_template.partial(prompt_context=prompt_context)
        self.prompt_template.append(prompt_context_template)

    def add_datasource(self, datasource: DataSource):
        self._fill_prompt_context(str(datasource.get_metadata()))
        return self

    def add_data_catalog(self, catalog: Catalog):
        self._fill_prompt_context(str(catalog))
        return self

    def stream(self, question: Optional[str] = "", display: Optional[bool] = True):
        self._format_question(question)
        chain = self._create_chain()
        events = chain.stream(self.config)
        if display:
            for event in events:
                print(event.content, end="", flush=True)
        if self.output_parser:
            chain = self.output_prompt_template | self.model | self.output_parser
            events = self._parse_output(chain, events)
        return events

    def invoke(self, question: Optional[str] = "", display: Optional[bool] = True):
        self._format_question(question)
        chain = self._create_chain()
        results = chain.invoke(self.config)
        if display:
            for result in results:
                print(result.content, end="", flush=True)
        if self.output_parser:
            chain = self.output_prompt_template | self.model | self.output_parser
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
        self.output_prompt_template = PromptTemplate(
            template="Return output in required format with given messages.\n{format_instructions}\n{messages}\n",
            input_variables=["messages"],
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()},
        )
        return self
