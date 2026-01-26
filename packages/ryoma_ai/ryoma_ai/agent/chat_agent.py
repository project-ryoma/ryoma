"""
Chat agent implementation for Ryoma AI.

This module provides the ChatAgent class for conversational AI interactions
with optional structured output parsing and prompt management.
"""

import logging
import uuid
from typing import Any, Dict, Optional, Union

from langchain_core.exceptions import OutputParserException
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnableSerializable
from langchain_core.stores import BaseStore
from pydantic import BaseModel

from ryoma_ai.agent.base import BaseAgent
from ryoma_ai.llm.provider import load_model_provider
from ryoma_ai.models.agent import AgentType
from ryoma_ai.prompt.prompt_template import PromptTemplateFactory

logger = logging.getLogger(__name__)


class ChatAgent(BaseAgent):
    """
    Chat agent with prompt management and optional output parsing.

    This agent provides conversational AI capabilities with support for:
    - Custom prompt templates
    - Structured output parsing
    - Chat history management
    - Flexible model configuration

    Example:
        >>> from ryoma_ai.agent.chat_agent import ChatAgent
        >>> from ryoma_ai.llm.provider import load_model_provider
        >>>
        >>> llm = load_model_provider("gpt-3.5-turbo")
        >>> agent = ChatAgent(
        ...     model=llm,
        ...     system_prompt="You are a helpful data assistant"
        ... )
        >>> response = agent.invoke("What is SQL?")
    """

    type: AgentType = AgentType.chat
    description: str = "Chat Agent supports all the basic functionalities of a chat agent."

    # Instance attributes
    config: Dict[str, Any]
    model_parameters: Optional[Dict]
    prompt_template_factory: PromptTemplateFactory
    final_prompt_template: Optional[Union[PromptTemplate, ChatPromptTemplate]]
    output_parser: Optional[PydanticOutputParser]

    def __init__(
        self,
        model: Union[str, BaseChatModel],
        model_parameters: Optional[Dict] = None,
        base_prompt_template: Optional[PromptTemplate] = None,
        context_prompt_templates: Optional[list[PromptTemplate]] = None,
        output_prompt_template: Optional[PromptTemplate] = None,
        output_parser: Optional[BaseModel] = None,
        system_prompt: Optional[str] = None,
        store: Optional[BaseStore] = None,
        **kwargs,
    ):
        """
        Initialize the chat agent.

        Args:
            model: Language model (string ID or BaseChatModel instance)
            model_parameters: Optional parameters for model initialization
            base_prompt_template: Optional base prompt template
            context_prompt_templates: Optional list of context templates
            output_prompt_template: Optional output template
            output_parser: Optional Pydantic model for structured output
            system_prompt: Optional system instructions (overrides base_prompt_template)
            store: Optional BaseStore for stateful operations
            **kwargs: Additional arguments (user_id, thread_id, etc.)
        """
        logger.info(f"Initializing ChatAgent with model: {model}")

        # Load model if string
        if isinstance(model, str):
            self._original_model_id = model
            loaded_model: BaseChatModel = load_model_provider(
                model, model_parameters=model_parameters
            )
        else:
            self._original_model_id = str(type(model).__name__)
            loaded_model = model

        # Initialize base agent with loaded model
        super().__init__(
            model=loaded_model,
            tools=None,  # ChatAgent doesn't use tools by default
            system_prompt=system_prompt,
            store=store,
        )

        # Session config for chat history
        self.config = {
            "configurable": {
                "user_id": kwargs.get("user_id", str(uuid.uuid4())),
                "thread_id": kwargs.get("thread_id", str(uuid.uuid4())),
            }
        }

        # Store model parameters
        self.model_parameters = model_parameters

        # Build prompt templates
        self.prompt_template_factory = PromptTemplateFactory(
            base_prompt_template,
            context_prompt_templates,
            output_prompt_template,
        )
        self.final_prompt_template = self.prompt_template_factory.build_prompt()
        self.output_parser = output_parser

        # Chain (lazy initialization)
        self._chain = None

    def _build_chain(self, **kwargs) -> RunnableSerializable:
        """
        Build the LLM chain with prompt and optional output parser.

        Returns:
            Runnable chain: prompt → model → (optional parser)
        """
        logger.info(f"Building LLM chain with model: {type(self.model).__name__}")

        if not self.model:
            raise ValueError(
                "Unable to initialize model. Please ensure valid configuration."
            )

        self.final_prompt_template = self.prompt_template_factory.build_prompt()

        if self.output_parser:
            return self.final_prompt_template | self.model | self.output_parser

        return self.final_prompt_template | self.model

    @property
    def chain(self) -> RunnableSerializable:
        """Get the LLM chain, building it if necessary."""
        if self._chain is None:
            self._chain = self._build_chain()
        return self._chain

    def invoke(self, user_input: str, **kwargs) -> str:
        """
        Synchronously invoke the agent with user input.

        Args:
            user_input: User's question or message
            **kwargs: Additional arguments passed to the chain

        Returns:
            Agent's response as string

        Raises:
            OutputParserException: If output parsing fails
        """
        try:
            messages = [HumanMessage(content=user_input)]
            response = self.chain.invoke({"messages": messages}, **kwargs)

            if isinstance(response, AIMessage):
                return response.content
            elif hasattr(response, "content"):
                return response.content
            else:
                return str(response)

        except OutputParserException as e:
            logger.error(f"Output parsing failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Agent invocation failed: {e}")
            raise

    def stream(self, user_input: str, **kwargs):
        """
        Stream response to user input.

        Args:
            user_input: User's question or message
            **kwargs: Additional arguments passed to the chain

        Yields:
            Response chunks
        """
        messages = [HumanMessage(content=user_input)]

        for chunk in self.chain.stream({"messages": messages}, **kwargs):
            if isinstance(chunk, AIMessage):
                yield chunk.content
            elif hasattr(chunk, "content"):
                yield chunk.content
            else:
                yield str(chunk)

    async def ainvoke(self, user_input: str, **kwargs) -> str:
        """
        Asynchronously invoke the agent with user input.

        Args:
            user_input: User's question or message
            **kwargs: Additional arguments passed to the chain

        Returns:
            Agent's response as string
        """
        try:
            messages = [HumanMessage(content=user_input)]
            response = await self.chain.ainvoke({"messages": messages}, **kwargs)

            if isinstance(response, AIMessage):
                return response.content
            elif hasattr(response, "content"):
                return response.content
            else:
                return str(response)

        except OutputParserException as e:
            logger.error(f"Output parsing failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Agent invocation failed: {e}")
            raise
