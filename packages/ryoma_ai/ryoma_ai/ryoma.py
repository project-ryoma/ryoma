"""
Ryoma - Main SDK entry point for the Ryoma AI platform.

This module provides the `Ryoma` class, the primary interface for interacting
with the Ryoma AI platform. It manages datasources and creates agents.

Example:
    >>> from ryoma_ai import Ryoma
    >>> from ryoma_data import DataSource
    >>>
    >>> # Simple usage
    >>> ryoma = Ryoma(datasource=DataSource("sqlite", database=":memory:"))
    >>> agent = ryoma.sql_agent(model="gpt-4")
    >>> agent.stream("Show all tables")
    >>>
    >>> # Multiple datasources
    >>> ryoma = Ryoma()
    >>> ryoma.add_datasource(sales_db, name="sales")
    >>> ryoma.add_datasource(marketing_db, name="marketing")
    >>> agent = ryoma.sql_agent(model="gpt-4", mode="enhanced")
    >>> ryoma.set_active("marketing")
"""

import logging
from typing import List, Literal, Optional, Union

from langchain_core.language_models import BaseChatModel
from langchain_core.stores import InMemoryStore

from ryoma_ai.agent.chat_agent import ChatAgent
from ryoma_ai.agent.pandas_agent import PandasAgent
from ryoma_ai.agent.sql import SqlAgent
from ryoma_ai.agent.workflow import WorkflowAgent
from ryoma_ai.domain.constants import StoreKeys
from ryoma_data.base import DataSource

logger = logging.getLogger(__name__)


class Ryoma:
    """
    Main entry point for the Ryoma AI platform.

    Ryoma manages datasources and creates AI agents. It provides a simple,
    unified interface for working with databases using natural language.

    Attributes:
        datasources: Dictionary of registered datasources by name
        active: Name of the currently active datasource

    Example:
        >>> from ryoma_ai import Ryoma
        >>> from ryoma_data import DataSource
        >>>
        >>> # Single datasource
        >>> ryoma = Ryoma(datasource=DataSource("postgres", host="localhost", ...))
        >>> agent = ryoma.sql_agent(model="gpt-4")
        >>>
        >>> # Multiple datasources
        >>> ryoma = Ryoma()
        >>> ryoma.add_datasource(db1, name="sales")
        >>> ryoma.add_datasource(db2, name="marketing")
        >>> ryoma.set_active("sales")
        >>> agent = ryoma.sql_agent(model="gpt-4")
    """

    def __init__(
        self,
        datasource: Optional[DataSource] = None,
        name: Optional[str] = None,
    ):
        """
        Initialize Ryoma.

        Args:
            datasource: Optional datasource to add immediately
            name: Optional name for the datasource (defaults to datasource.id)

        Example:
            >>> ryoma = Ryoma(datasource=my_db)
            >>> ryoma = Ryoma()  # Add datasources later
        """
        self._datasources: dict[str, DataSource] = {}
        self._active: Optional[str] = None
        self._store = InMemoryStore()

        if datasource is not None:
            self.add_datasource(datasource, name=name)

        logger.debug("Initialized Ryoma")

    def add_datasource(
        self,
        datasource: DataSource,
        name: Optional[str] = None,
    ) -> "Ryoma":
        """
        Add a datasource.

        The first datasource added becomes the active datasource automatically.

        Args:
            datasource: DataSource to add
            name: Optional name (defaults to datasource.id)

        Returns:
            self for method chaining

        Example:
            >>> ryoma.add_datasource(db1, name="sales")
            >>> ryoma.add_datasource(db2, name="marketing")
        """
        ds_name = name or getattr(datasource, "id", None) or f"ds_{len(self._datasources)}"
        self._datasources[ds_name] = datasource

        # First datasource becomes active
        if self._active is None:
            self._active = ds_name
            self._update_store()

        logger.info(f"Added datasource: {ds_name}")
        return self

    def set_active(self, name: str) -> "Ryoma":
        """
        Set the active datasource.

        Args:
            name: Name of the datasource to activate

        Returns:
            self for method chaining

        Raises:
            ValueError: If datasource not found

        Example:
            >>> ryoma.set_active("marketing")
        """
        if name not in self._datasources:
            available = list(self._datasources.keys())
            raise ValueError(
                f"Datasource '{name}' not found. Available: {available}"
            )

        self._active = name
        self._update_store()
        logger.info(f"Activated datasource: {name}")
        return self

    def get_active(self) -> Optional[DataSource]:
        """
        Get the currently active datasource.

        Returns:
            The active DataSource, or None if no datasource is configured
        """
        if self._active is None:
            return None
        return self._datasources.get(self._active)

    def list_datasources(self) -> List[str]:
        """
        List all registered datasource names.

        Returns:
            List of datasource names
        """
        return list(self._datasources.keys())

    def remove_datasource(self, name: str) -> "Ryoma":
        """
        Remove a datasource.

        Args:
            name: Name of the datasource to remove

        Returns:
            self for method chaining

        Raises:
            ValueError: If datasource not found
        """
        if name not in self._datasources:
            raise ValueError(f"Datasource '{name}' not found")

        del self._datasources[name]

        # If we removed the active datasource, clear it
        if self._active == name:
            self._active = next(iter(self._datasources), None)
            self._update_store()

        logger.info(f"Removed datasource: {name}")
        return self

    def sql_agent(
        self,
        model: Union[str, BaseChatModel] = "gpt-3.5-turbo",
        mode: Literal["basic", "enhanced", "reforce"] = "basic",
        **kwargs,
    ) -> WorkflowAgent:
        """
        Create a SQL agent.

        Args:
            model: Model identifier (e.g., "gpt-4") or LLM instance
            mode: Agent mode - "basic", "enhanced", or "reforce"
            **kwargs: Additional arguments passed to SqlAgent

        Returns:
            Configured SQL agent

        Raises:
            ValueError: If no active datasource is configured

        Example:
            >>> agent = ryoma.sql_agent(model="gpt-4", mode="enhanced")
            >>> agent.stream("Show top customers by revenue")
        """
        self._require_datasource()

        return SqlAgent(
            model=model,
            mode=mode,
            store=self._store,
            **kwargs,
        )

    def pandas_agent(
        self,
        model: Union[str, BaseChatModel] = "gpt-3.5-turbo",
        **kwargs,
    ) -> PandasAgent:
        """
        Create a Pandas agent for DataFrame analysis.

        Args:
            model: Model identifier or LLM instance
            **kwargs: Additional arguments passed to PandasAgent

        Returns:
            Configured Pandas agent

        Example:
            >>> agent = ryoma.pandas_agent(model="gpt-4")
            >>> agent.add_dataframe(df, df_id="sales")
            >>> agent.stream("What's the average by region?")
        """
        return PandasAgent(
            model=model,
            store=self._store,
            **kwargs,
        )

    def chat_agent(
        self,
        model: Union[str, BaseChatModel] = "gpt-3.5-turbo",
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> ChatAgent:
        """
        Create a chat agent for general conversation.

        Args:
            model: Model identifier or LLM instance
            system_prompt: Optional system instructions
            **kwargs: Additional arguments passed to ChatAgent

        Returns:
            Configured chat agent

        Example:
            >>> agent = ryoma.chat_agent(model="gpt-4", system_prompt="You are a data expert")
            >>> agent.stream("What is a JOIN in SQL?")
        """
        return ChatAgent(
            model=model,
            system_prompt=system_prompt,
            **kwargs,
        )

    def _require_datasource(self) -> None:
        """Raise error if no active datasource."""
        if self._active is None or self._active not in self._datasources:
            raise ValueError(
                "No active datasource configured. "
                "Use ryoma.add_datasource() or pass datasource to Ryoma()."
            )

    def _update_store(self) -> None:
        """Update the internal store with current active datasource."""
        if self._active and self._active in self._datasources:
            datasource = self._datasources[self._active]
            self._store.mset([(StoreKeys.ACTIVE_DATASOURCE, datasource)])

    @property
    def active(self) -> Optional[str]:
        """Name of the active datasource."""
        return self._active

    @property
    def datasources(self) -> dict[str, DataSource]:
        """Dictionary of all registered datasources."""
        return self._datasources.copy()

    def __repr__(self) -> str:
        ds_count = len(self._datasources)
        active = self._active or "None"
        return f"Ryoma(datasources={ds_count}, active='{active}')"
