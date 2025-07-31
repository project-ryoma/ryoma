from typing import Literal, Optional, Union

from langchain_core.embeddings import Embeddings
from ryoma_ai.agent.resource_registry import ResourceRegistry
from ryoma_ai.datasource.base import DataSource
from ryoma_ai.datasource.metadata import Catalog, Column, Schema, Table
from ryoma_ai.embedding.client import get_embedding_client
from ryoma_ai.models.agent import AgentType
from ryoma_ai.vector_store.base import VectorStore
from ryoma_ai.vector_store.config import VectorStoreConfig
from ryoma_ai.vector_store.factory import create_vector_store


class BaseAgent:
    """
    Base class for all agents in Ryoma. Inherits from this class can be used to create custom agents.
    """

    type: AgentType = AgentType.base
    description: str = "Ryoma Agent is your best friend!"
    _datasource: Optional[DataSource] = None
    vector_store: Optional[VectorStore] = None

    def __init__(
        self,
        datasource: Optional[DataSource] = None,
        embedding: Optional[Union[dict, Embeddings]] = None,
        vector_store: Optional[Union[dict, VectorStore]] = None,
        **kwargs,
    ):
        self.resource_registry = ResourceRegistry()

        # Initialize store for InjectedStore functionality
        from langgraph.store.memory import InMemoryStore
        self.store = InMemoryStore()

        if datasource:
            self._datasource = datasource
            # Add datasource to store for InjectedStore
            self.store.put(("datasource",), "main", datasource)

        if embedding:
            self.embedding = self.init_embedding(embedding)

        if vector_store:
            self.vector_store = self.init_vector_store(vector_store, self.embedding)

    def init_embedding(self, embedding: Union[dict, Embeddings]) -> Embeddings:
        if isinstance(embedding, Embeddings):
            return embedding
        elif isinstance(embedding, dict):
            provider = embedding.get("model")
            model_params = {k: v for k, v in embedding.items() if k != "model"}
            return get_embedding_client(provider, model_parameters=model_params)
        else:
            raise ValueError("`embedding` must be a dict or Embeddings instance.")

    def init_vector_store(
        self, vector_store: Union[dict, VectorStore], embedding: Embeddings
    ) -> VectorStore:
        if isinstance(vector_store, VectorStore):
            return vector_store
        elif isinstance(vector_store, dict):
            config = VectorStoreConfig(**vector_store)
        elif isinstance(vector_store, VectorStoreConfig):
            config = vector_store
        else:
            raise ValueError(
                "`vector_store` must be a dict, VectorStoreConfig, or VectorStore instance."
            )

        return create_vector_store(config=config, embedding_function=embedding)

    def datasource(self, datasource: DataSource):
        """
        Register a DataSource as a resource.

        Args:
            datasource: The DataSource to register.

        Returns:
              self (for chaining)
        """
        self._datasource = datasource
        # Add datasource to store for InjectedStore
        self.store.put(("datasource",), "main", datasource)
        return self

    def get_datasource(self):
        return self._datasource

    def register_resource(self, obj, name: str):
        self.resource_registry.register(obj, name)
        return id(obj)

    def get_resources_by_type(self, cls):
        return self.resource_registry.get_by_type(cls)

    def get_resource_by_name(self, name):
        return self.resource_registry.get_by_name(name)

    def index_datasource(
        self,
        datasource: Union[str, DataSource],
        level: Literal["catalog", "schema", "table", "column"] = "catalog",
    ):
        """
        Index a DataSource in the vector store.

        Args:
            datasource: The DataSource to index.
            level: The level of indexing (catalog, schema, table, column). Defaults to 'catalog'.
        """
        if not self.vector_store:
            raise ValueError("Vector store is not set.")
        self.vector_store.index_data_source(datasource, level)

    def index_all_data_sources(self):
        """
        Index all DataSources in the vector store.
        """
        if not self.vector_store:
            raise ValueError("Vector store is not set.")
        for datasource in self.get_resources_by_type(DataSource):
            self.vector_store.index_data_source(datasource)

    def search_catalogs(self, query: str, top_k: int = 5, **kwargs) -> Catalog:
        """
        Search documents in the vector store.

        Args:
            query: The query string to search for.
            top_k: The number of top results to return. Defaults to 5.
            filter: Optional filter criteria for the search.

        Returns:
            A Catalog containing the selected top items (schemas, tables, columns).
        """
        if not self.vector_store:
            raise ValueError("Vector store is not set.")
        search_results = self.vector_store.search_documents(query, top_k=top_k)
        original_catalog = self.get_datasource().get_catalog()
        filtered_catalog = Catalog(
            catalog_name=original_catalog.catalog_name, schemas=[]
        )

        for doc in search_results:
            doc_id, metadata = doc.id, doc.metadata
            level = metadata.get("level", "catalog")
            schema = original_catalog.get_schema(metadata.get("schema_name", doc_id))

            if level == "schema" and schema:
                filtered_catalog.schemas.append(schema)
            elif level == "table" and schema:
                table = schema.get_table(doc_id)
                if table:
                    if not any(
                        s.schema_name == schema.schema_name
                        for s in filtered_catalog.schemas
                    ):
                        filtered_catalog.schemas.append(
                            Schema(schema_name=schema.schema_name, tables=[])
                        )
                    filtered_schema = next(
                        s
                        for s in filtered_catalog.schemas
                        if s.schema_name == schema.schema_name
                    )
                    filtered_schema.tables.append(table)
            elif level == "column" and schema:
                table = schema.get_table(metadata.get("table_name"))
                if table:
                    column = table.get_column(doc_id)
                    if column:
                        if not any(
                            s.schema_name == schema.schema_name
                            for s in filtered_catalog.schemas
                        ):
                            filtered_catalog.schemas.append(
                                Schema(schema_name=schema.schema_name, tables=[])
                            )
                        filtered_schema = next(
                            s
                            for s in filtered_catalog.schemas
                            if s.schema_name == schema.schema_name
                        )
                        if not any(
                            t.table_name == table.table_name
                            for t in filtered_schema.tables
                        ):
                            filtered_schema.tables.append(
                                Table(table_name=table.table_name, columns=[])
                            )
                        filtered_table = next(
                            t
                            for t in filtered_schema.tables
                            if t.table_name == table.table_name
                        )
                        filtered_table.columns.append(column)

        return filtered_catalog

