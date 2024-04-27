from langchain_core.tools import BaseTool
from jupyter_ai_magics.providers import *
from jupyter_ai_magics.utils import get_lm_providers, decompose_model_id
from langchain.tools.render import render_text_description


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
    context: {prompt_context}

    question: {question}
    """

    def __init__(self,
                 model_id: str,
                 model_parameters: Optional[Dict],
                 tools: List[BaseTool],
                 prompt_context: str = None):
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
            prompt_context=self.prompt_context,
            question=question
        )

    def chat(self, question: str, allow_run_tool=False):
        prompt = self._build_prompt(question)
        chat_result = self.model.invoke(prompt)
        if allow_run_tool and "addtiional_kwargs" in chat_result and chat_result.addtiional_kwargs and "tool_calls" in chat_result.additional_kwargs:
            run_tool_result = self.run_tool(chat_result["tool_calls"])
            return run_tool_result
        return chat_result

    def run_tool(self, tool_spec: dict) -> Any:
        tool = self.tool_registry[tool_spec["name"]]
        return tool.invoke(tool_spec["args"])
