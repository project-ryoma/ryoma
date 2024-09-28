from typing import Dict, Literal, Optional, Union

from langchain_core.messages import ToolMessage
from langchain_core.output_parsers.openai_tools import PydanticToolsParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, ValidationError
from langchain_core.runnables import RunnableSerializable
from langchain_core.runnables.config import RunnableConfig
from langgraph.graph import END, StateGraph
from ryoma_ai.agent.workflow import WorkflowAgent
from ryoma_ai.states import MessageState


class ValidatorAgent(WorkflowAgent):
    validator: BaseModel
    validator_chain: RunnableSerializable

    def __int__(
        self,
        validator: BaseModel,
        model: Union[RunnableSerializable, str],
        model_parameters: Optional[Dict] = None,
        **kwargs,
    ):
        self.validator_tool = validator

        self.base_prompt_template = PromptTemplate(
            template="Please return the output given messages and following the feature validation\n{messages}",
            input_variables=["messages"],
        )

        super().__init__([self.validator_tool], model, model_parameters, **kwargs)

    def call_model(self, state: list, config: RunnableConfig):
        messages = {**state, "user_info": config.get("user_id", None)}
        response = self.chain.invoke(messages, config)
        return {"messages": [response]}

    def validate(self, state: list, config: RunnableConfig):
        messages = state["messages"][-1]
        try:
            response = self.validator.invoke(messages)
            return {"messages": [response]}
        except ValidationError as e:
            state = state + [
                ToolMessage(
                    content=f"{repr(e)}\n\nPay close attention to the function feature.\n\n"
                    + self.validator.schema_json()
                    + " Respond by fixing all validation errors.",
                    tool_call_id=response.tool_calls[0]["id"],
                ),
            ]
            return state

    def _build_workflow(self):
        workflow = StateGraph(MessageState)

        workflow.add_node("agent", self.call_model)
        workflow.add_node("tools", self.build_tool_node(self.tools))
        workflow.add_node("validator", self.call_model)
        workflow.add_node("validation", self._validate)

        workflow.add_conditional_edges("agent", self._should_call_tool)
        workflow.add_conditional_edges("validator", self._should_validate)
        workflow.add_edge("tools", "agent")
        workflow.add_edge("validation", "validator")

        workflow.set_entry_point("agent")
        return workflow.compile(
            checkpointer=self.memory, interrupt_before=["validator", "tools"]
        )

    def _validate(self, state: list, config: RunnableConfig):
        message = state["messages"][-1]
        try:
            validator = PydanticToolsParser(tools=[self.validator])
            validator.invoke(message)
            response = self.validator_chain.invoke(config)
            response.additional_kwargs["validated"] = True
            return {"messages": [response]}
        except ValidationError as e:
            return {
                "messages": [
                    ToolMessage(
                        content=f"{repr(e)}\n\nPay close attention to the function feature.\n\n"
                        + " Respond by fixing all validation errors.",
                        tool_call_id=message.tool_calls[0]["id"],
                    )
                ]
            }

    def _should_call_tool(self, state: list) -> Literal["tools", "validator"]:
        if isinstance(state, list):
            ai_message = state[-1]
        elif messages := state.get("messages", []):
            ai_message = messages[-1]
        else:
            raise ValueError(f"No messages found in input state to tool_edge: {state}")
        if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
            return "tools"
        return "validator"

    def _should_validate(
        self, state: list
    ) -> Literal["agent", "validation", "__end__"]:
        if (
            state["messages"][-1].tool_calls
            and "validated" not in state["messages"][-1].additional_kwargs
        ):
            return "validation"
        return END
