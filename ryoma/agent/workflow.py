import logging
from enum import Enum
from typing import Callable

from IPython.display import Image, display
from jupyter_ai_magics.providers import *
from langchain.tools.render import render_text_description
from langchain_core.messages import HumanMessage, ToolCall, ToolMessage
from langchain_core.runnables import (
    RunnableConfig,
    RunnableLambda,
    RunnableSerializable,
)
from langchain_core.tools import BaseTool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.pregel import StateSnapshot

from ryoma.agent.base import BaseAgent
from ryoma.datasource.base import DataSource
from ryoma.models.agent import AgentType
from ryoma.states import MessageState


class ToolMode(str, Enum):
    """The mode of the tool call."""

    DISALLOWED = "disallowed"
    CONTINUOUS = "continuous"
    ONCE = "once"


def handle_tool_error(state) -> dict:
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }


class WorkflowAgent(BaseAgent):
    tools: List[BaseTool]
    graph: StateGraph
    workflow: CompiledGraph
    type: AgentType = AgentType.workflow

    def __init__(
        self,
        tools: List[BaseTool],
        model: Union[RunnableSerializable, str],
        model_parameters: Optional[Dict] = None,
        graph: Optional[StateGraph] = None,
        base_prompt_template: Optional[PromptTemplate] = None,
        context_prompt_templates: Optional[list[PromptTemplate]] = None,
        output_prompt_template: Optional[PromptTemplate] = None,
        output_parser: Optional[BaseModel] = None,
        **kwargs,
    ):
        logging.info(f"Initializing Workflow Agent with model: {model}")
        super().__init__(
            model,
            model_parameters,
            base_prompt_template,
            context_prompt_templates,
            output_prompt_template,
            output_parser,
            **kwargs,
        )

        self.tools = tools
        if self.tools:
            self.model = self._bind_tools()

        self.memory = MemorySaver()
        self.workflow = self._build_workflow(graph)

    def _bind_tools(self):
        logging.info("Binding tools {} to model".format(self.tools))
        if hasattr(self.model, "bind_tools"):
            return self.model.bind_tools(self.tools)
        else:
            rendered_tools = render_text_description(self.tools)
            tool_prompt = f"""
            You are an assistant that has access to the following set of tools. Here are the names and descriptions for each tool:

            {rendered_tools}

            """
            tool_prompt_template = ChatPromptTemplate.from_messages(
                [("system", tool_prompt)]
            )
            self.prompt_template_factory.add_context_prompt(tool_prompt_template)
            return self.model

    def _build_workflow(self, graph: StateGraph) -> CompiledGraph:
        if graph:
            return graph.compile(checkpointer=self.memory, interrupt_before=["tools"])
        workflow = StateGraph(MessageState)

        workflow.add_node("agent", self.call_model)
        workflow.add_node("tools", self.build_tool_node(self.tools))

        workflow.add_conditional_edges(
            "agent",
            tools_condition,
        )

        workflow.set_entry_point("agent")
        workflow.add_edge("tools", "agent")
        return workflow.compile(checkpointer=self.memory, interrupt_before=["tools"])

    @staticmethod
    def init_state():
        return StateGraph(MessageState)

    def get_graph(self):
        return self.workflow.get_graph(self.config)

    def get_current_state(self) -> Optional[StateSnapshot]:
        return self.workflow.get_state(self.config)

    def get_current_state_messages(self):
        current_state = self.get_current_state()
        if current_state:
            return current_state.values.get("messages")
        return []

    def get_current_tool_calls(self) -> List[ToolCall]:
        current_state_messages = self.get_current_state().values.get("messages")
        if current_state_messages and current_state_messages[-1].tool_calls:
            return current_state_messages[-1].tool_calls
        return []

    def add_datasource(self, datasource: DataSource):
        super().add_datasource(datasource)
        for tool in self.tools:
            if hasattr(tool, "datasource"):
                tool.datasource = datasource
        return self

    def _format_messages(self, question: str):
        current_state = self.get_current_state()
        if current_state.next and current_state.next[0] == "tools":
            # We are in the tool node, but the user has asked a new question
            # We need to deny the tool call and continue with the user's question
            tool_calls = self.get_current_tool_calls()
            return {
                "messages": [
                    ToolMessage(
                        tool_call_id=tool_calls[0]["id"],
                        content=f"Tool call denied by user. Reasoning: '{question}'. Continue assisting, accounting for the user's input.",
                    )
                ]
            }
        else:
            return {"messages": [HumanMessage(content=question)]}

    def stream(
        self,
        question: Optional[str] = "",
        tool_mode: str = ToolMode.DISALLOWED,
        max_iterations: int = 10,
        display=True,
    ):
        if (
            not question
            and tool_mode != ToolMode.DISALLOWED
            and self.get_current_tool_calls()
        ):
            messages = None
        else:
            messages = self._format_messages(question)
        events = self.workflow.stream(
            messages, config=self.config, stream_mode="values"
        )
        if display:
            _printed = set()
            self._print_graph_events(events, _printed)

        if tool_mode == ToolMode.CONTINUOUS:
            current_state = self.get_current_state()
            iterations = 0
            while current_state.next and iterations < max_iterations:
                iterations += 1
                events = self.workflow.stream(None, config=self.config)
                if display:
                    logging.info(f"Iteration {iterations}")
                    self._print_graph_events(events, _printed)
                current_state = self.get_current_state()
        if self.output_parser:
            chain = self.output_prompt | self.model | self.output_parser
            events = self._parse_output(chain, events, max_iterations=max_iterations)
        return events

    def invoke(
        self,
        question: Optional[str] = "",
        tool_mode: str = ToolMode.DISALLOWED,
        max_iterations: int = 10,
        display=True,
    ):
        if (
            not question
            and tool_mode != ToolMode.DISALLOWED
            and self.get_current_tool_calls()
        ):
            messages = None
        else:
            messages = self._format_messages(question)
        result = self.workflow.invoke(messages, config=self.config)
        if display:
            _printed = set()
            self._print_graph_events(result, _printed)

        if tool_mode == ToolMode.CONTINUOUS:
            logging.info("Starting the iterative invocation process.")
            current_state = self.get_current_state()
            iterations = 0
            while current_state.next and iterations < max_iterations:
                iterations += 1
                result = self.workflow.invoke(None, config=self.config)
                if display:
                    logging.info(f"Iteration {iterations}")
                    self._print_graph_events(result, _printed)
                current_state = self.get_current_state()
        if self.output_parser:
            chain = self.output_prompt | self.model | self.output_parser
            result = self._parse_output(chain, result, max_iterations=max_iterations)
        return result

    @staticmethod
    def build_tool_node(tools):
        return ToolNode(tools).with_fallbacks(
            [RunnableLambda(handle_tool_error)], exception_key="error"
        )

    def call_tool(self, tool_id: str, **kwargs):
        if not tool_id:
            raise ValueError("Tool id is required.")
        curr_tool_calls = self.get_current_tool_calls()
        tool_call = next((tc for tc in curr_tool_calls if tc["id"] == tool_id), None)
        if not tool_call:
            raise ValueError(
                f"Unable to find tool call {tool_id} in the current state."
            )
        tool = next((t for t in self.tools if t.name == tool_call["name"]), None)
        if kwargs.get("args"):
            tool_call["args"].update(kwargs["args"])
        res = tool.invoke(tool_call["args"], self.config)
        return res

    def update_tool(self, tool_id: str, tool_args: dict):
        if not tool_id:
            raise ValueError("Tool id is required.")
        current_state_messages = self.get_current_state_messages()
        curr_tool_calls = self.get_current_tool_calls()
        tool_call_index = next(
            (
                index
                for (index, tc) in enumerate(curr_tool_calls)
                if tc["id"] == tool_id
            ),
            None,
        )
        if tool_call_index is None:
            raise ValueError(f"Tool call {tool_id} not found in current state.")
        current_state_messages[-1].tool_calls[tool_call_index]["args"] = tool_args
        new_state = {"messages": [current_state_messages[-1]]}
        self.workflow.update_state(self.config, new_state)

    def cancel_tool(self, tool_id: str):
        pass

    def _build_chain(self):
        self.final_prompt_template.append(
            MessagesPlaceholder(variable_name="messages", optional=True)
        )
        return self.final_prompt_template | self.model

    def call_model(self, state: MessageState, config: RunnableConfig):
        chain = self._build_chain()
        response = chain.invoke(state, self.config)
        return {"messages": [response]}

    def _print_graph_events(self, events, printed, max_length=1500):
        if isinstance(events, dict):
            events = [events]
        for event in events:
            messages = self._get_event_message(event)
            for message in messages:
                if message.id not in printed:
                    msg_repr = message.pretty_repr(html=True)
                    if len(msg_repr) > max_length:
                        msg_repr = msg_repr[:max_length] + " ... (truncated)"
                    print(msg_repr)
                    printed.add(message.id)

    def _get_event_message(self, event):
        if "tools" in event:
            return event["tools"]["messages"]
        if "agent" in event:
            return event["agent"]["messages"]
        if "messages" in event:
            return event["messages"]
        return event

    def display_graph(self):
        display(Image(self.workflow.get_graph().draw_mermaid_png()))
