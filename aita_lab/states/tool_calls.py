from typing import Optional

import reflex as rx

from aita_lab.states.tool import Tool, ToolOutput


class ToolCall(rx.Base):
    tool: Tool = None
    tool_output: ToolOutput = None


class ToolCallState(rx.State):
    tool_calls: list[ToolCall] = []

    def add_tool_call(self, tool: Tool, output: ToolOutput):
        self.tool_calls.append(ToolCall(tool=tool, output=output))

    def clear_tool_calls(self):
        self.tool_calls = []

    def on_load(self):
        pass
        # self.tool_calls =
