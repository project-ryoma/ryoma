from typing import Optional

from ryoma_ai.agent.resource_registry import ResourceRegistry
from ryoma_ai.datasource.base import DataSource
from ryoma_ai.models.agent import AgentType
from ryoma_ai.vector_store.base import VectorStore


class BaseAgent:
    """
    Base class for all agents in Ryoma. Inherits from this class can be used to create custom agents.
    """

    type: AgentType = AgentType.base
    description: str = "Ryoma Agent is your best friend!"
    resource_registry: ResourceRegistry
    vector_store: Optional[VectorStore] = None

    def __init__(self,
                 datasource: Optional[DataSource] = None,
                 vector_store: Optional[VectorStore] = None):
        self.resource_registry = ResourceRegistry()

        if datasource:
            self.register_resource(datasource)

        if vector_store:
            self.vector_store = vector_store

    def add_datasource(self,
                       datasource: DataSource,
                       index: bool = False
                       ):
        """
        Register a DataSource as a resource.

        Args:
            datasource: The DataSource to register.
            index: Whether to index the DataSource in the vector store.

        Returns:
              self (for chaining)
        """
        self.register_resource(datasource)
        if index:
            self.index_datasource(datasource)
        return self

    def register_resource(self,
                          obj):
        self.resource_registry.register(obj)
        return id(obj)

    def get_resources_by_type(self,
                              cls):
        return self.resource_registry.get_by_type(cls)

    def index_datasource(self,
                         datasource: DataSource):
        """
        Index a DataSource in the vector store.

        Args:
              datasource: The DataSource to index.
        """
        if not self.vector_store:
            raise ValueError("Vector store is not set.")

        self.vector_store.index_datasource(datasource)

    def index_all_datasources(self):
        """
        Index all DataSources in the vector store.
        """
        if not self.vector_store:
            raise ValueError("Vector store is not set.")
        for datasource in self.get_resources_by_type(DataSource):
            self.vector_store.index_datasource(datasource)
