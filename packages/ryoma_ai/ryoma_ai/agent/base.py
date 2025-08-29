import logging
from typing import Any, Dict, List, Literal, Optional, Union

from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore
from ryoma_ai.agent.resource_registry import ResourceRegistry
from ryoma_ai.catalog.indexer import UnifiedCatalogIndexService
from ryoma_ai.datasource.base import DataSource
from ryoma_ai.datasource.metadata import Catalog
from ryoma_ai.embedding.client import get_embedding_client
from ryoma_ai.models.agent import AgentType
from ryoma_ai.store.catalog_store import CatalogNotIndexedError, CatalogStore
from ryoma_ai.vector_store.config import VectorStoreConfig
from ryoma_ai.vector_store.factory import create_vector_store

logger = logging.getLogger(__name__)


class BaseAgent:
    """
    Base class for all agents in Ryoma. Inherits from this class can be used to create custom agents.
    """

    type: AgentType = AgentType.base
    description: str = "Ryoma Agent is your best friend!"
    vector_store: Optional[VectorStore] = None

    def __init__(
        self,
        datasource: Optional[DataSource] = None,
        embedding: Optional[Union[dict, Embeddings]] = None,
        vector_store: Optional[Union[dict, VectorStore]] = None,
        store=None,
        **kwargs,
    ):
        self.resource_registry = ResourceRegistry()

        # Initialize store for InjectedStore functionality
        if store is None:
            # Provide default InMemoryStore for programmatic usage
            from langchain_core.stores import InMemoryStore
            self.store = InMemoryStore()
            logger.info("Using default InMemoryStore - for production, pass unified store from CLI")
        else:
            self.store = store

        if datasource:
            # Add datasource to store for InjectedStore
            self.add_datasource(datasource)

        if embedding:
            self.embedding = self.init_embedding(embedding)

        if vector_store:
            embedding_to_use = getattr(self, "embedding", None)
            self.vector_store = self.init_vector_store(vector_store, embedding_to_use)

        # Initialize unified catalog indexing service
        self._catalog_index_service = None
        if hasattr(self, "vector_store") and self.vector_store:
            self._catalog_index_service = UnifiedCatalogIndexService(
                vector_store=self.vector_store,
                metadata_store=self.store,  # Use agent's store for metadata
            )

        # Initialize catalog store
        self._catalog_store = None

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

    def add_datasource(self, datasource: DataSource):
        """
        Register a DataSource as a resource.

        Args:
            datasource: The DataSource to register.

        Returns:
              self (for chaining)
        """
        # Add datasource to store using LangChain store API
        self.store.mset([("datasource_main", datasource)])
        return self

    def get_datasource(self) -> DataSource:
        """
        Get the registered DataSource.

        Returns:
            The registered DataSource.
        """
        results = self.store.mget(["datasource_main"])
        datasource = results[0] if results and results[0] is not None else None
        if not datasource:
            raise ValueError("No DataSource registered.")
        return datasource

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
        data_source_id: Optional[str] = None,
    ):
        """
        Index a DataSource using the unified catalog indexing service.

        Args:
            datasource: The DataSource to index.
            level: The level of indexing (catalog, schema, table, column). Defaults to 'catalog'.
            data_source_id: Optional ID for the data source (defaults to datasource type).
        """
        if isinstance(datasource, str):
            # Assume it's a resource name
            datasource = self.get_resource_by_name(datasource)
            if not isinstance(datasource, DataSource):
                raise ValueError(f"Resource '{datasource}' is not a DataSource")

        if not data_source_id:
            data_source_id = f"agent_{id(self)}_{datasource.type}"

        # Use unified indexing service
        if not self._catalog_index_service:
            raise ValueError(
                "Catalog indexing service is not initialized. Ensure vector_store is set."
            )

        catalog_id = self._catalog_index_service.index_datasource(
            datasource=datasource,
            data_source_id=data_source_id,
            level=level,  # type: ignore
        )
        logger.info(f"Indexed datasource using unified service: {catalog_id}")
        return catalog_id

    def index_all_data_sources(self):
        """
        Index all DataSources using the unified indexing service.
        """
        datasources = self.get_resources_by_type(DataSource)
        if not datasources:
            logger.info("No datasources to index")
            return

        for i, datasource in enumerate(datasources):
            try:
                self.index_datasource(
                    datasource, data_source_id=f"agent_{id(self)}_ds_{i}"
                )
            except Exception as e:
                logger.error(f"Failed to index datasource {i}: {e}")

    def _get_catalog_store(self) -> Optional[CatalogStore]:
        """Get catalog store with lazy initialization."""
        if self._catalog_store is None and self._catalog_index_service:
            # Create a CatalogStore from the unified indexing service's metadata store
            self._catalog_store = CatalogStore(
                metadata_store=self._catalog_index_service.metadata_store,
                vector_store=self._catalog_index_service.vector_store,
            )
        return self._catalog_store

    def search_catalogs(self, query: str, top_k: int = 5, **kwargs) -> Catalog:
        """
        Search for relevant catalog metadata using optimized indexing.

        This method uses semantic search on indexed catalog metadata to avoid
        loading the entire catalog, providing better performance for large datasets.

        Args:
            query: The query string to search for.
            top_k: The number of top results to return. Defaults to 5.
            **kwargs: Additional search parameters

        Returns:
            A Catalog containing only relevant metadata found via search.

        Raises:
            CatalogNotIndexedError: If catalog indexing is not properly configured
            ValueError: If vector store is not configured
        """
        # Try optimized search first
        catalog_store = self._get_catalog_store()
        if catalog_store:
            try:
                min_score = kwargs.get("min_score", 0.3)
                element_types = kwargs.get("element_types")

                return catalog_store.search_relevant_catalog(
                    query=query,
                    top_k=top_k,
                    min_score=min_score,
                    element_types=element_types,
                )
            except CatalogNotIndexedError as e:
                logger.warning(f"Optimized catalog search failed: {e}")
                raise ValueError(
                    "Catalog search requires proper indexing. "
                    "Please run agent.index_datasource() first, or use get_datasource().get_catalog() "
                    "for unoptimized full catalog access."
                ) from e

        # If no catalog store available, raise error (no fallback)
        raise ValueError(
            "Catalog search requires vector store and proper indexing. "
            "Please configure vector_store and run agent.index_datasource() first."
        )

    def get_table_suggestions(
        self,
        query: str,
        max_tables: int = 5,
        min_score: float = 0.4,
    ) -> List[Dict[str, str]]:
        """
        Get table suggestions based on a query using indexed metadata.

        Args:
            query: Search query describing the data needed
            max_tables: Maximum number of table suggestions
            min_score: Minimum similarity score for relevance

        Returns:
            List of table suggestions with metadata

        Raises:
            ValueError: If catalog indexing is not properly configured
        """
        catalog_store = self._get_catalog_store()
        if not catalog_store:
            raise ValueError(
                "Table suggestions require vector store and proper indexing. "
                "Please configure vector_store and run agent.index_datasource() first."
            )

        try:
            return catalog_store.get_table_suggestions(
                query=query,
                max_tables=max_tables,
                min_score=min_score,
            )
        except CatalogNotIndexedError as e:
            raise ValueError(
                "Table suggestions require proper indexing. "
                "Please run agent.index_datasource() first."
            ) from e

    def get_column_suggestions(
        self,
        query: str,
        table_context: Optional[str] = None,
        max_columns: int = 10,
        min_score: float = 0.3,
    ) -> List[Dict[str, str]]:
        """
        Get column suggestions based on a query using indexed metadata.

        Args:
            query: Search query describing the data needed
            table_context: Optional table name to filter results
            max_columns: Maximum number of column suggestions
            min_score: Minimum similarity score for relevance

        Returns:
            List of column suggestions with metadata

        Raises:
            ValueError: If catalog indexing is not properly configured
        """
        catalog_store = self._get_catalog_store()
        if not catalog_store:
            raise ValueError(
                "Column suggestions require vector store and proper indexing. "
                "Please configure vector_store and run agent.index_datasource() first."
            )

        try:
            return catalog_store.get_column_suggestions(
                query=query,
                table_context=table_context,
                max_columns=max_columns,
                min_score=min_score,
            )
        except CatalogNotIndexedError as e:
            raise ValueError(
                "Column suggestions require proper indexing. "
                "Please run agent.index_datasource() first."
            ) from e

    def validate_catalog_indexing(self) -> Dict[str, Any]:
        """
        Check if catalog indexing is properly configured and working.

        Returns:
            Dictionary with indexing status and recommendations
        """
        catalog_store = self._get_catalog_store()
        if not catalog_store:
            return {
                "status": "not_configured",
                "has_vector_store": bool(self.vector_store),
                "has_indexing_service": bool(self._catalog_index_service),
                "recommendation": "Configure vector_store and run '/index-catalog' command or agent.index_datasource() to enable optimized catalog search",
            }

        indexing_status = catalog_store.validate_indexing_status()
        indexing_status["status"] = (
            "configured"
            if indexing_status.get("has_indexed_catalogs")
            else "no_catalogs"
        )

        if not indexing_status.get("has_indexed_catalogs"):
            indexing_status["recommendation"] = (
                "Run '/index-catalog' command or agent.index_datasource() to index your catalogs for optimized search"
            )
        else:
            indexing_status["recommendation"] = (
                "Catalog indexing is properly configured"
            )

        return indexing_status
