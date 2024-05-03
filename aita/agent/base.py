from jupyter_ai_magics.providers import *
from jupyter_ai_magics.utils import decompose_model_id, get_lm_providers
from langchain.tools.render import render_text_description
from langchain_core.tools import BaseTool


def get_model(model_id: str, model_parameters: Optional[Dict]) -> Optional[BaseProvider]:
    providers = get_lm_providers()
    provider_id, local_model_id = decompose_model_id(model_id, providers)
    if provider_id is None or provider_id not in providers:
        return None
    Provider = providers[provider_id]
    provider_params = {"model_id": local_model_id}
    model_parameters = model_parameters or {}
    return Provider(**provider_params, **model_parameters)


class AitaAgent:
    model: str
    model_parameters: Optional[Dict]
    tool_registry: Dict[str, BaseTool]

    base_prompt_template = """
    Context: {prompt_context}

    Question: {question}
    """

    def __init__(
        self,
        model_id: str,
        model_parameters: Optional[Dict] = None,
        tools: List[BaseTool] = None,
        prompt_context: str = None,
    ):
        self.model: BaseProvider = get_model(model_id, model_parameters)
        self.tool_registry = {}
        self.prompt_context = prompt_context
        if tools:
            self.bind_tools(tools)

    def bind_tools(self, tools: List[BaseTool]):
        if hasattr(self.model, "bind_tools"):
            self.model = self.model.bind_tools(tools)
        else:
            rendered_tools = render_text_description(tools)
            tool_prompt = f"""
            You are an assistant that has access to the following set of tools. Here are the names and descriptions for each tool:

            {rendered_tools}

            """
            self.base_prompt_template = tool_prompt + self.base_prompt_template
        self.register_tools(tools)

    def register_tools(self, tools: List[BaseTool]):
        for tool in tools:
            self.tool_registry[tool.name] = tool

    def _build_prompt(self, question: str):
        return self.base_prompt_template.format(
            prompt_context=self.prompt_context, question=question
        )

    def chat(self, question: str, allow_run_tool=False):
        prompt = self._build_prompt(question)
        chat_result = self.model.invoke(prompt)
        if (
            allow_run_tool
            and hasattr(chat_result, "additional_kwargs")
            and "tool_calls" in chat_result.additional_kwargs
        ):
            run_tool_results = []
            for tool in chat_result.additional_kwargs["tool_calls"]:
                run_tool_result = self.run_tool(tool["function"])
                run_tool_results.append(run_tool_result)
            return run_tool_results
        return chat_result

    def run_tool(self, tool_spec: Dict) -> Any:
        tool = self.tool_registry[tool_spec["name"]]
        arguments = tool_spec.get("arguments")
        if isinstance(arguments, str):
            arguments = json.loads(arguments)
        return tool.invoke(arguments)
