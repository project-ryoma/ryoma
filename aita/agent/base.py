import uuid

from jupyter_ai_magics.providers import *
from jupyter_ai_magics.utils import decompose_model_id, get_lm_providers
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableSerializable

from aita.datasource.base import DataSource


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
    config: Dict[str, Any]
    model: RunnableSerializable
    chain: RunnableSerializable
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

        self._create_chain()

    def _create_chain(self):
        self.chain = self.prompt_template | self.model

    def _set_base_prompt_template(self):
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", self.base_prompt_template),
            ]
        )

    def set_base_prompt_template(self, base_prompt_template: str):
        self.base_prompt_template = base_prompt_template
        self._set_base_prompt_template()
        self._create_chain()
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

    def _fill_prompt_context(self, context: str):
        if not self.prompt_context_template:
            self._set_base_prompt_context_template()
        prompt_context_template = self.prompt_context_template.partial(prompt_context=context)
        self.prompt_template.append(prompt_context_template)

    def add_datasource(self, datasource: DataSource):
        self._fill_prompt_context(str(datasource.get_metadata()))
        return self

    def stream(self, question: Optional[str] = "", display: Optional[bool] = True):
        self._format_question(question)
        events = self.chain.stream(self.config)
        if display:
            for event in events:
                print(event.content, end="", flush=True)
        else:
            return events

    def get_current_state(self) -> None:
        return None

    def with_structured_output(self, output_format: BaseModel):
        parser = PydanticOutputParser(pydantic_object=output_format)
        self.chain = self.chain | parser
        return self
