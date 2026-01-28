"""
Service for building fully-configured agents.

This module provides the AgentBuilder service which orchestrates the
creation of agents with all necessary dependencies and configurations.
"""

import logging
from typing import Optional, Literal, Union
from langchain_core.language_models import BaseChatModel
from langchain_core.stores import InMemoryStore

from ryoma_ai.services.datasource_service import DataSourceService
from ryoma_ai.services.catalog_service import CatalogService
from ryoma_ai.agent.workflow import WorkflowAgent
from ryoma_ai.agent.chat_agent import ChatAgent
from ryoma_ai.agent.sql_tools import (
    get_basic_sql_tools,
    get_enhanced_sql_tools,
    get_reforce_sql_tools,
)
from ryoma_ai.llm.provider import load_model_provider
from ryoma_ai.domain.constants import StoreKeys, AgentDefaults

logger = logging.getLogger(__name__)


class AgentBuilder:
    """
    Service for building fully-configured agents.

    This builder handles all the complex wiring of agents with their
    dependencies (datasources, tools, LLMs) so that agents can stay
    simple and focused on conversation logic.

    **Architecture:**
    - Uses DataSourceService to get active datasource
    - Uses CatalogService for catalog-aware tools (optional)
    - Creates appropriate tools based on agent type/mode
    - Loads LLM from model identifier
    - Wires everything together into a clean agent

    Example:
        >>> builder = AgentBuilder(
        ...     datasource_service=datasource_service,
        ...     catalog_service=catalog_service
        ... )
        >>> agent = builder.build_sql_agent(model="gpt-4", mode="enhanced")
        >>> response = agent.stream("What are top customers?")
    """

    def __init__(
        self,
        datasource_service: DataSourceService,
        catalog_service: Optional[CatalogService] = None,
    ):
        """
        Initialize the agent builder.

        Args:
            datasource_service: Service for datasource management.
                               Required for agents that need data access.
            catalog_service: Optional service for catalog operations.
                            If provided, enables catalog-aware tools.
        """
        self._datasource_service = datasource_service
        self._catalog_service = catalog_service
        logger.debug("Initialized AgentBuilder")

    def build_sql_agent(
        self,
        model: Union[str, BaseChatModel] = AgentDefaults.DEFAULT_MODEL,
        mode: Literal["basic", "enhanced", "reforce"] = "basic",
        model_params: Optional[dict] = None,
    ) -> WorkflowAgent:
        """
        Build a SQL agent with all tools configured.

        This creates a WorkflowAgent configured for SQL query generation
        and execution. The agent gets tools based on the specified mode
        and has access to the active datasource.

        Args:
            model: Model identifier (e.g., "gpt-4") or LLM instance.
                  Defaults to "gpt-3.5-turbo".
            mode: Agent mode determining tool set:
                  - "basic": Core SQL tools only
                  - "enhanced": Basic + explanation/optimization
                  - "reforce": Enhanced with ReFoRCE prompting
            model_params: Optional parameters for LLM initialization

        Returns:
            Configured WorkflowAgent ready for SQL queries

        Raises:
            ValueError: If no active datasource is configured

        Example:
            >>> agent = builder.build_sql_agent(
            ...     model="gpt-4",
            ...     mode="enhanced"
            ... )
            >>> result = agent.invoke("Show me top 5 customers by revenue")
        """
        # Get active datasource
        try:
            datasource = self._datasource_service.get_active_datasource()
        except ValueError as e:
            raise ValueError(
                "Cannot build SQL agent: No active datasource configured. "
                "Use datasource_service.add_datasource() first."
            ) from e

        # Get tools based on mode
        if mode == "basic":
            tools = get_basic_sql_tools()
        elif mode == "enhanced":
            tools = get_enhanced_sql_tools()
        elif mode == "reforce":
            tools = get_reforce_sql_tools()
        else:
            raise ValueError(
                f"Unknown SQL agent mode: {mode}. "
                f"Valid modes: 'basic', 'enhanced', 'reforce'"
            )

        # Get LLM
        llm = self._create_llm(model, model_params)

        # Create store and add datasource for tool injection
        store = InMemoryStore()
        store.mset([(StoreKeys.ACTIVE_DATASOURCE, datasource)])

        # Build agent
        system_prompt = self._get_sql_prompt(mode)
        agent = WorkflowAgent(
            model=llm,
            tools=tools,
            system_prompt=system_prompt,
            store=store,
        )

        logger.info(
            f"Built SQL agent: mode={mode}, tools={len(tools)}, "
            f"model={type(llm).__name__}"
        )
        return agent

    def build_python_agent(
        self,
        model: Union[str, BaseChatModel] = AgentDefaults.DEFAULT_MODEL,
        model_params: Optional[dict] = None,
    ) -> WorkflowAgent:
        """
        Build a Python code execution agent.

        This creates an agent that can write and execute Python code
        to solve problems or analyze data.

        Args:
            model: Model identifier or LLM instance
            model_params: Optional parameters for LLM

        Returns:
            Configured WorkflowAgent with Python execution tools

        Example:
            >>> agent = builder.build_python_agent(model="gpt-4")
            >>> result = agent.invoke("Calculate fibonacci(10)")
        """
        from ryoma_ai.tool.python_tool import PythonREPLTool

        llm = self._create_llm(model, model_params)
        tools = [PythonREPLTool()]

        agent = WorkflowAgent(
            model=llm,
            tools=tools,
            system_prompt="You are a Python programming expert. "
            "Write and execute Python code to solve problems.",
        )

        logger.info(f"Built Python agent: tools={len(tools)}")
        return agent

    def build_chat_agent(
        self,
        model: Union[str, BaseChatModel] = AgentDefaults.DEFAULT_MODEL,
        system_prompt: Optional[str] = None,
        model_params: Optional[dict] = None,
    ) -> ChatAgent:
        """
        Build a simple chat agent without tools.

        This creates a ChatAgent for conversational interaction
        without tool use.

        Args:
            model: Model identifier or LLM instance
            system_prompt: Optional system instructions
            model_params: Optional parameters for LLM

        Returns:
            Configured ChatAgent

        Example:
            >>> agent = builder.build_chat_agent(
            ...     model="gpt-4",
            ...     system_prompt="You are a helpful data assistant"
            ... )
            >>> result = agent.invoke("What is SQL?")
        """
        llm = self._create_llm(model, model_params)

        agent = ChatAgent(
            model=llm,
            system_prompt=system_prompt,
        )

        logger.info(f"Built chat agent: model={type(llm).__name__}")
        return agent

    def _create_llm(
        self, model: Union[str, BaseChatModel], model_params: Optional[dict] = None
    ) -> BaseChatModel:
        """
        Create LLM instance from model identifier or return existing instance.

        Args:
            model: Model ID string or LLM instance
            model_params: Optional parameters for model initialization

        Returns:
            BaseChatModel instance
        """
        if isinstance(model, BaseChatModel):
            return model

        params = model_params or {}
        return load_model_provider(model, model_parameters=params)

    def _get_sql_prompt(self, mode: str) -> str:
        """
        Get system prompt for SQL agent based on mode.

        Args:
            mode: SQL agent mode (basic/enhanced/reforce)

        Returns:
            System prompt string
        """
        prompts = {
            "basic": (
                "You are a SQL expert. Write SQL queries to answer questions "
                "about the data. Always use the SqlQueryTool to execute queries."
            ),
            "enhanced": (
                "You are an advanced SQL expert. Use the available tools to "
                "analyze queries, explain execution plans, and optimize performance. "
                "Always validate and profile important queries."
            ),
            "reforce": (
                "You are a SQL expert using the ReFoRCE (Reflect, Force, Correct) approach. "
                "For each query:\n"
                "1. Reflect: Think about what the query should do\n"
                "2. Force: Generate and execute the query\n"
                "3. Correct: If results don't match expectations, revise and retry\n"
                "Use all available tools to ensure query accuracy."
            ),
        }
        return prompts.get(mode, prompts["basic"])
