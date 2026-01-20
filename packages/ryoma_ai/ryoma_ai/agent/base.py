"""
Base agent class for Ryoma AI.

This module provides the foundational BaseAgent class that all Ryoma agents
inherit from. The agent is designed to be simple and focused - it only handles
conversation and tool execution, with all infrastructure concerns managed by
external services.
"""

import logging
from typing import List, Optional
from langchain_core.language_models import BaseChatModel
from langchain_core.stores import BaseStore
from langchain_core.tools import BaseTool
from ryoma_ai.models.agent import AgentType

logger = logging.getLogger(__name__)


class BaseAgent:
    """
    Base class for all agents in Ryoma.

    This is a simplified agent that focuses solely on conversation and tool
    execution. All infrastructure concerns (datasource management, catalog
    indexing, vector stores, embeddings) are handled by external services.

    **Design Philosophy:**
    - Single Responsibility: Only handles agent conversation logic
    - Dependency Injection: Services are injected, not created internally
    - Separation of Concerns: Infrastructure separated from domain logic

    **Breaking Changes from v0.1.x:**
    - Removed: datasource, embedding, vector_store parameters
    - Removed: add_datasource(), get_datasource() methods
    - Removed: index_datasource(), search_catalogs() methods
    - Removed: resource_registry, init_embedding(), init_vector_store()
    - Simplified: __init__ now only takes model, tools, system_prompt, store

    **Migration Guide:**
    Use DataSourceService for datasource management, CatalogService for
    catalog operations, and AgentBuilder to construct fully-configured agents.

    Example:
        >>> # Old way (v0.1.x) - DON'T USE
        >>> agent = SqlAgent(
        ...     model="gpt-4",
        ...     datasource=my_datasource,
        ...     embedding={"model": "openai"},
        ...     vector_store={"type": "qdrant"},
        ... )

        >>> # New way (v0.2.0) - USE THIS
        >>> from ryoma_ai.services import AgentBuilder
        >>> agent = agent_builder.build_sql_agent(model="gpt-4")
    """

    # Class attributes
    type: AgentType = AgentType.base
    description: str = "Ryoma Agent - AI-powered data assistant"

    def __init__(
        self,
        model: Optional[BaseChatModel] = None,
        tools: Optional[List[BaseTool]] = None,
        system_prompt: Optional[str] = None,
        store: Optional[BaseStore] = None,
    ):
        """
        Initialize the base agent.

        Args:
            model: Language model for reasoning and generation.
                   Can be None if subclass sets it differently.
            tools: List of tools available to the agent.
                   Tools should be LangChain BaseTool instances.
            system_prompt: System instructions for the agent.
                          Defines the agent's behavior and capabilities.
            store: BaseStore for LangGraph's InjectedStore pattern.
                  Used to pass datasource and other context to tools.
                  If None, tools won't have access to injected store.

        Note:
            This is a minimal initialization. Subclasses should extend this
            with their specific requirements (e.g., building chains, graphs).
        """
        self.model = model
        self.tools = tools or []
        self.system_prompt = system_prompt or "You are a helpful AI assistant."
        self.store = store

        logger.debug(
            f"Initialized {self.__class__.__name__} with "
            f"{len(self.tools)} tools, "
            f"model={type(model).__name__ if model else 'None'}"
        )

    def stream(self, user_input: str):
        """
        Stream response to user input.

        This method should be implemented by subclasses to provide
        streaming responses.

        Args:
            user_input: User's question or command

        Yields:
            Response chunks

        Raises:
            NotImplementedError: If subclass doesn't implement this method
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement stream() method"
        )

    def invoke(self, user_input: str):
        """
        Synchronously invoke the agent.

        This method should be implemented by subclasses to provide
        synchronous responses.

        Args:
            user_input: User's question or command

        Returns:
            Complete response

        Raises:
            NotImplementedError: If subclass doesn't implement this method
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement invoke() method"
        )

    async def ainvoke(self, user_input: str):
        """
        Asynchronously invoke the agent.

        This method should be implemented by subclasses to provide
        async responses.

        Args:
            user_input: User's question or command

        Returns:
            Complete response

        Raises:
            NotImplementedError: If subclass doesn't implement this method
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement ainvoke() method"
        )
