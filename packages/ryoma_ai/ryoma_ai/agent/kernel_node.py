from typing import Callable, List, Optional, Sequence, Union

from langchain_core.messages import ToolCall, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from langgraph.prebuilt import ToolNode


class KernelNode(ToolNode):
    """A ToolNode that can use a custom executor for running the tool."""

    def __init__(
        self,
        tools: Sequence[Union[BaseTool, Callable]],
        executor: Callable,
        *,
        name: str = "kernel_tools",
        tags: Optional[List[str]] = None,
        handle_tool_errors: bool = True,
    ):
        super().__init__(
            tools, name=name, tags=tags, handle_tool_errors=handle_tool_errors
        )
        self.executor = executor

    def _run_one(self, call: ToolCall, config: RunnableConfig) -> ToolMessage:
        if invalid_tool_message := self._validate_tool_call(call):
            return invalid_tool_message

        try:
            input = {**call, **{"type": "tool_call"}}
            tool = self.tools_by_name[call["name"]]
            result = self.executor(tool, input, config)
            tool_message = ToolMessage(
                content=str(result), name=call["name"], tool_call_id=call["id"]
            )
            return tool_message
        except Exception as e:
            if not self.handle_tool_errors:
                raise e
            content = f"Error: {repr(e)}\n Please fix your mistakes."
            return ToolMessage(content, name=call["name"], tool_call_id=call["id"])

    async def _arun_one(self, call: ToolCall, config: RunnableConfig) -> ToolMessage:
        if invalid_tool_message := self._validate_tool_call(call):
            return invalid_tool_message

        try:
            input = {**call, **{"type": "tool_call"}}
            tool = self.tools_by_name[call["name"]]
            result = await self.executor(tool, input, config)
            tool_message = ToolMessage(
                content=str(result), name=call["name"], tool_call_id=call["id"]
            )
            return tool_message
        except Exception as e:
            if not self.handle_tool_errors:
                raise e
            content = f"Error: {repr(e)}\n Please fix your mistakes."
            return ToolMessage(content, name=call["name"], tool_call_id=call["id"])
