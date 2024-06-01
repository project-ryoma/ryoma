import uuid

from langgraph.graph.graph import CompiledGraph
from langgraph.pregel import StateSnapshot

from aita.datasource.base import DataSource
from aita.states import MessageState
from jupyter_ai_magics.providers import *
from jupyter_ai_magics.utils import decompose_model_id, get_lm_providers
from langchain.tools.render import render_text_description
from langchain_core.messages import ToolMessage, HumanMessage
from langchain_core.runnables import RunnableLambda, RunnableConfig, RunnableSerializable
from langchain_core.tools import BaseTool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition, ToolInvocation

# default configuration
# TODO: make this configurable
CONFIG = {
    "configurable": {
        "user_id": str(uuid.uuid4()),
        "thread_id": str(uuid.uuid4()),
    }
}


def get_model(model_id: str, model_parameters: Optional[Dict]) -> Optional[RunnableSerializable]:
    providers = get_lm_providers()
    provider_id, local_model_id = decompose_model_id(model_id, providers)
    if provider_id is None or provider_id not in providers:
        return None
    Provider = providers[provider_id]
    provider_params = {"model_id": local_model_id}
    model_parameters = model_parameters or {}
    return Provider(**provider_params, **model_parameters)


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


class AitaAgent:
    model: Union[RunnableSerializable, str]
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
        model: str,
        model_parameters: Optional[Dict] = None,
        **kwargs,
    ):
        if isinstance(model, str):
            self.model: RunnableSerializable = get_model(model, model_parameters)
        else:
            self.model = model

        self._set_base_prompt_template()
        self.prompt_context_template = None

    def _set_base_prompt_template(self):
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", self.base_prompt_template),
            ]
        )
        self.model = self.prompt_template | self.model

    def _set_base_prompt_context_template(self):
        self.prompt_context_template = ChatPromptTemplate.from_messages(
            [("system", self.base_prompt_context_template)]
        )

    def set_prompt_context(self, prompt_context: Optional[Union[str, ChatPromptTemplate]] = None):
        if isinstance(prompt_context, str):
            prompt_context = ChatPromptTemplate.from_messages(
                [("system", self.base_prompt_context_template.format(prompt_context=prompt_context))])
        if not self.prompt_context_template:
            self.prompt_context_template = prompt_context
        else:
            self.prompt_context_template.append(prompt_context)
        return self

    def _format_question(self, question: str):
        if self.prompt_context_template:
            self.prompt_template.append(self.prompt_context_template)
        self.prompt_template.append(("user", question))

    def _fill_prompt_context(self, context: str):
        if not self.prompt_context_template:
            self._set_base_prompt_context_template()
        self.prompt_context_template = self.prompt_context_template.partial(
            prompt_context=context)
        return self

    def add_datasource(self, datasource: DataSource):
        self._fill_prompt_context(str(datasource.get_metadata()))
        return self

    def chat(self,
             question: Optional[str] = "",
             display: Optional[bool] = True):
        self._format_question(question)
        events = self.model.stream(CONFIG)
        if display:
            for event in events:
                print(event.content, end="", flush=True)
        else:
            return events


class ToolAgent(AitaAgent):
    tools: List[BaseTool]
    model_graph: CompiledGraph

    def __init__(
        self,
        tools: List[BaseTool],
        model: Union[RunnableSerializable, str],
        model_parameters: Optional[Dict] = None,
        **kwargs,
    ):
        if isinstance(model, str):
            self.model = get_model(model, model_parameters)
        else:
            self.model = model

        # bind tools to the model
        self.tools = tools
        self._bind_tools(self.tools)

        super().__init__(self.model, model_parameters, **kwargs)

        # build the graph, this has to happen after the prompt is built
        self.memory = MemorySaver()
        self.model_graph = self._build_graph()

    def _bind_tools(self, tools: List[BaseTool]):
        if hasattr(self.model, "bind_tools"):
            self.model = self.model.bind_tools(tools)
        else:
            rendered_tools = render_text_description(tools)
            tool_prompt = f"""
            You are an assistant that has access to the following set of tools. Here are the names and descriptions for each tool:

            {rendered_tools}

            """
            self.base_prompt_template = tool_prompt + self.base_prompt_template

    def _build_graph(self) -> CompiledGraph:
        workflow = StateGraph(MessageState)

        # Define the two nodes we will cycle between
        workflow.add_node("agent", self.call_model)
        workflow.add_node("action", self._build_tool_node())

        # We now add a conditional edge
        workflow.add_conditional_edges(
            "agent",
            tools_condition,
            {
                "action": "action",
                END: END,
            },
        )

        # Set the entrypoint as `agent`
        # This means that this node is the first one called
        workflow.set_entry_point("agent")

        workflow.add_edge("action", "agent")
        return workflow.compile(checkpointer=self.memory, interrupt_before=["action"])

    def get_current_state(self) -> Optional[StateSnapshot]:
        return self.model_graph.get_state(CONFIG)

    def get_current_tool_calls(self) -> List[ToolMessage]:
        return self.get_current_state().values.get("messages")[-1].tool_calls

    def add_datasource(self, datasource: DataSource):
        super().add_datasource(datasource)
        for tool in self.tools:
            if hasattr(tool, "datasource"):
                tool.datasource = datasource
        return self

    def _format_question(self, question: str):
        if self.prompt_context_template:
            self.prompt_template.append(self.prompt_context_template)
        self.prompt_template.append(MessagesPlaceholder(variable_name="messages", optional=True))

    def chat(self,
             question: Optional[str] = "",
             allow_run_tool: Optional[bool] = False,
             display=True):
        if allow_run_tool:
            messages = None
        else:
            self._format_question(question)
            messages = {"messages": [HumanMessage(content=question)]}
        events = self.model_graph.stream(messages, config=CONFIG, stream_mode="values")
        if display:
            self._print_graph_events(events)
        return events

    def _build_tool_node(self):
        return ToolNode(self.tools).with_fallbacks(
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
        res = tool.invoke(tool_call["args"], CONFIG)
        return res

    def call_model(self, state: MessageState, config: RunnableConfig):
        messages = {**state, "user_info": config.get("user_id", None)}
        response = self.model.invoke(messages)
        # We return a list, because this will get added to the existing list
        return {"messages": [response]}

    def _print_graph_events(self, events, max_length=1500):
        _printed = set()
        for event in events:
            current_state = event.get("dialog_state")
            if current_state:
                print(f"Currently in: ", current_state[-1])
            message = event.get("messages")
            if message:
                if isinstance(message, list):
                    message = message[-1]
                if message.id not in _printed:
                    msg_repr = message.pretty_repr(html=True)
                    if len(msg_repr) > max_length:
                        msg_repr = msg_repr[:max_length] + " ... (truncated)"
                    print(msg_repr)
                    _printed.add(message.id)
