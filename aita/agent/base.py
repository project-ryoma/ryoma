from typing import Dict, Any

from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI


class AitaAgent:
    model: str
    temperature: float
    tool_registry: Dict[str, BaseTool]

    base_prompt_template = """
    context: {prompt_context}

    question: {question}
    """

    def __init__(self, model, temperature, tools, prompt_context=None):
        self.model = model
        self.temperature = temperature
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.tool_registry = {}
        self.prompt_context = prompt_context
        if tools:
            self.llm = self.llm.bind_tools(tools)
            print(self.llm)
            self.register_tools(tools)

    def register_tools(self, tools):
        for tool in tools:
            self.tool_registry[tool.name] = tool

    def _build_prompt(self, question):
        return self.base_prompt_template.format(
            prompt_context=self.prompt_context,
            question=question
        )

    def chat(self, question, allow_run_tool=False):
        prompt = self._build_prompt(question)
        chat_result = self.llm.invoke(prompt)
        if allow_run_tool and chat_result.addtiional_kwargs and "tool_calls" in chat_result.additional_kwargs:
            run_tool_result = self.run_tool(chat_result["tool_calls"])
            return run_tool_result
        return chat_result

    def run_tool(self, tool_spec: dict) -> Any:
        tool = self.tool_registry[tool_spec["name"]]
        return tool.invoke(tool_spec["args"])

