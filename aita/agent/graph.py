from enum import Enum

from IPython.display import Image, display
from jupyter_ai_magics.providers import *
from langchain.tools.render import render_text_description
from langchain_core.messages import HumanMessage, ToolCall, ToolMessage
from langchain_core.runnables import RunnableConfig, RunnableLambda, RunnableSerializable
from langchain_core.tools import BaseTool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.pregel import StateSnapshot

from aita.agent.base import AitaAgent
from aita.datasource.base import DataSource
from aita.states import MessageState


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


class GraphAgent(AitaAgent):
    tools: List[BaseTool]
    graph: StateGraph
    compiled_graph: CompiledGraph

    def __init__(
        self,
        tools: List[BaseTool],
        model: Union[RunnableSerializable, str],
        model_parameters: Optional[Dict] = None,
        graph: Optional[StateGraph] = None,
        **kwargs,
    ):
        self.tools = tools

        super().__init__(model, model_parameters, **kwargs)

        # build the graph, this has to happen after the prompt is built
        self.memory = MemorySaver()
        self.compiled_graph = self._build_graph(graph)

    def _bind_tools(self):
        if hasattr(self.model, "bind_tools"):
            return self.model.bind_tools(self.tools)
        else:
            rendered_tools = render_text_description(self.tools)
            tool_prompt = f"""
            You are an assistant that has access to the following set of tools. Here are the names and descriptions for each tool:

            {rendered_tools}

            """
            self.base_prompt.append(("system", tool_prompt))
            return self.model

    def _build_graph(self, graph: StateGraph) -> CompiledGraph:
        if graph:
            return graph.compile(checkpointer=self.memory, interrupt_before=["tools"])
        workflow = StateGraph(MessageState)

        # Define the two nodes we will cycle between
        workflow.add_node("agent", self.call_model)
        workflow.add_node("tools", self.build_tool_node(self.tools))

        # We now add a conditional edge
        workflow.add_conditional_edges(
            "agent",
            tools_condition,
        )

        workflow.set_entry_point("agent")
        workflow.add_edge("tools", "agent")
        return workflow.compile(checkpointer=self.memory, interrupt_before=["tools"])

    @staticmethod
    def init_state_graph():
        return StateGraph(MessageState)

    def get_graph(self):
        return self.compiled_graph.get_graph(self.config)

    def get_current_state(self) -> Optional[StateSnapshot]:
        return self.compiled_graph.get_state(self.config)

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

    def _build_prompt(self, question: str):
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
            self.prompt_template = ChatPromptTemplate.from_messages(self.base_prompt.messages)
            self.prompt_template.extend(self.context_prompt_template)
            self.prompt_template.append(
                MessagesPlaceholder(variable_name="messages", optional=True)
            )
            return {"messages": [HumanMessage(content=question)]}

    def stream(
        self,
        question: Optional[str] = "",
        tool_mode: str = ToolMode.DISALLOWED,
        max_iterations: int = 10,
        display=True,
    ):
        if not question and tool_mode != ToolMode.DISALLOWED and self.get_current_tool_calls():
            messages = None
        else:
            messages = self._build_prompt(question)
        events = self.compiled_graph.stream(messages, config=self.config, stream_mode="values")
        if display:
            _printed = set()
            self._print_graph_events(events, _printed)

        if tool_mode == ToolMode.CONTINUOUS:
            current_state = self.get_current_state()
            iterations = 0
            while current_state.next and iterations < max_iterations:
                iterations += 1
                events = self.compiled_graph.stream(None, config=self.config)
                if display:
                    print(f"Iteration {iterations}")
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
        if not question and tool_mode != ToolMode.DISALLOWED and self.get_current_tool_calls():
            messages = None
        else:
            messages = self._build_prompt(question)
        result = self.compiled_graph.invoke(messages, config=self.config)
        if display:
            _printed = set()
            self._print_graph_events(result, _printed)

        if tool_mode == ToolMode.CONTINUOUS:
            print("Starting the iterative invocation process.")
            current_state = self.get_current_state()
            iterations = 0
            while current_state.next and iterations < max_iterations:
                iterations += 1
                result = self.compiled_graph.invoke(None, config=self.config)
                if display:
                    print(f"Iteration {iterations}")
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

    def call_tool(self, tool_name: str, tool_id: Optional[str] = None, **kwargs):
        if not tool_name:
            raise ValueError("Tool name is required.")
        curr_tool_calls = self.get_current_tool_calls()
        if tool_id:
            tool_call = next((tc for tc in curr_tool_calls if tc["id"] == tool_id), None)
        else:
            tool_call = next((tc for tc in curr_tool_calls if tc["name"] == tool_name), None)
        if not tool_call:
            raise ValueError(f"Tool call {tool_name} not found in current state.")
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            raise ValueError(f"Tool {tool_name} not found in the tool sets.")
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
            (index for (index, tc) in enumerate(curr_tool_calls) if tc["id"] == tool_id), None
        )
        if tool_call_index is None:
            raise ValueError(f"Tool call {tool_id} not found in current state.")
        current_state_messages[-1].tool_calls[tool_call_index]["args"] = tool_args
        new_state = {"messages": [current_state_messages[-1]]}
        self.compiled_graph.update_state(self.config, new_state)

    def cancel_tool(self, tool_id: str):
        pass

    def call_model(self, state: MessageState, config: RunnableConfig):
        print("Calling the model.")
        print(self.prompt_template)
        chain = self.prompt_template | self._bind_tools()
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
        display(Image(self.compiled_graph.get_graph().draw_mermaid_png()))
