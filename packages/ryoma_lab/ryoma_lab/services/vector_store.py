import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import reflex as rx
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from ryoma_ai.vector_store.config import DocumentProcessorConfig
from ryoma_ai.vector_store.document_processor import DocumentProcessor
from ryoma_ai.vector_store.factory import create_vector_store
from ryoma_lab.config.vector_store_config import get_vector_store_config_from_rxconfig
from ryoma_lab.models.vector_store import DocumentProject
from sqlmodel import select


class VectorStoreService:
    """
    Vector Store Service using LangChain interface.
    Supports multiple vector stores: Chroma, FAISS, Qdrant, Milvus, PGVector, etc.
    Provides high-level operations for document indexing and semantic search.
    """

    def __init__(self):
        self.session = rx.session()
        self._stores = {}  # Cache for vector stores
        self._processors = {}  # Cache for document processors

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Close all cached stores
        for store in self._stores.values():
            if hasattr(store, "__exit__"):
                store.__exit__(None, None, None)
        self.session.close()

    def _get_vector_store(self, project_name: str, embedding_function: Embeddings):
        """Get or create cached vector store using rxconfig"""
        if project_name not in self._stores:
            project_model = self.get_project(project_name)
            if not project_model:
                raise ValueError(f"Document project '{project_name}' not found")

            # Get configuration from rxconfig
            config = get_vector_store_config_from_rxconfig()
            # Override collection name with project name
            config.collection_name = project_name

            self._stores[project_name] = create_vector_store(config, embedding_function)

        return self._stores[project_name]

    def _get_document_processor(
        self, project_name: str, embedding_function: Embeddings
    ):
        """Get or create cached document processor"""
        cache_key = f"{project_name}_{id(embedding_function)}"

        if cache_key not in self._processors:
            vector_store = self._get_vector_store(project_name, embedding_function)
            doc_config = DocumentProcessorConfig()
            self._processors[cache_key] = DocumentProcessor(
                vector_store=vector_store,
                embedding_function=embedding_function,
                config=doc_config,
            )

        return self._processors[cache_key]

    # Database operations
    def load_projects(self) -> List[DocumentProject]:
        """Load all document projects."""
        return list(self.session.exec(select(DocumentProject)).all())

    def get_project(self, project_name: str) -> Optional[DocumentProject]:
        """Get a document project by name."""
        return self.session.exec(
            select(DocumentProject).filter(DocumentProject.project_name == project_name)
        ).first()

    def delete_project(self, project_name: str) -> None:
        """Delete a document project."""
        # Clear from cache
        if project_name in self._stores:
            store = self._stores.pop(project_name)
            if hasattr(store, "__exit__"):
                store.__exit__(None, None, None)

        # Clear processors cache
        keys_to_remove = [
            k for k in self._processors.keys() if k.startswith(f"{project_name}_")
        ]
        for key in keys_to_remove:
            self._processors.pop(key)

        # Delete from database
        result = self.session.exec(
            select(DocumentProject).filter(DocumentProject.project_name == project_name)
        )
        project = result.first()
        if project:
            self.session.delete(project)
            self.session.commit()

    def create_project(
        self, project_name: str, description: Optional[str] = None
    ) -> DocumentProject:
        """
        Create a new document project.
        Configuration comes from rxconfig.py
        """
        try:
            # Save to database
            project_model = DocumentProject(
                project_name=project_name,
                description=description,
                document_count=0,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                is_active=True,
            )

            self.session.add(project_model)
            self.session.commit()

            logging.info(f"Created document project: {project_name}")
            return project_model

        except Exception as e:
            logging.error(f"Failed to create document project {project_name}: {e}")
            raise

    # New Milvus-based API methods
    def index_documents(
        self,
        project_name: str,
        file_paths: List[str],
        embedding_function: Embeddings,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Index multiple documents into a vector store.
        """
        processor = self._get_document_processor(project_name, embedding_function)

        total_chunks = 0
        for file_path in file_paths:
            try:
                chunks = processor.process_and_index_file(file_path, metadata)
                total_chunks += chunks
                logging.info(f"Indexed {chunks} chunks from {file_path}")
            except Exception as e:
                logging.error(f"Failed to index {file_path}: {e}")
                continue

        return total_chunks

    def search_documents(
        self,
        project_name: str,
        query: str,
        embedding_function: Embeddings,
        top_k: int = 5,
        filter_expr: Optional[str] = None,
    ) -> List[Document]:
        """
        Search documents using text query.
        """
        processor = self._get_document_processor(project_name, embedding_function)
        return processor.search_documents(query, top_k)

    def search_vectors(
        self,
        project_name: str,
        query_vector: List[float],
        embedding_function: Embeddings,
        top_k: int = 5,
        filter_expr: Optional[str] = None,
    ) -> List[Document]:
        """
        Search using pre-computed vector.
        Note: LangChain VectorStores don't typically support direct vector search.
        Use similarity_search with query text instead.
        """
        self._get_vector_store(project_name, embedding_function)

        # LangChain VectorStores don't have direct vector search
        # This is a limitation of the unified interface
        logging.warning("Direct vector search not supported in LangChain interface")
        return []

    def get_project_info(self, project_name: str) -> Dict[str, Any]:
        """
        Get basic information about a document project.
        """
        try:
            project_model = self.get_project(project_name)
            if not project_model:
                return {"name": project_name, "error": "Project not found"}

            # Get configuration from rxconfig
            config = get_vector_store_config_from_rxconfig()

            return {
                "name": project_name,
                "description": project_model.description,
                "document_count": project_model.document_count,
                "type": config.type,
                "collection_name": project_name,  # Use project name as collection name
                "dimension": config.dimension,
                "distance_metric": config.distance_metric,
                "created_at": project_model.created_at,
                "is_active": project_model.is_active,
            }
        except Exception as e:
            logging.error(f"Failed to get project info for {project_name}: {e}")
            return {"name": project_name, "error": str(e)}

    def clear_store(self, project_name: str) -> None:
        """
        Clear all vectors from a store.
        Note: LangChain VectorStores don't have a standard clear method.
        """
        try:
            # Clear from cache - forces recreation
            if project_name in self._stores:
                self._stores.pop(project_name)

            # Clear processors cache
            keys_to_remove = [
                k for k in self._processors.keys() if k.startswith(f"{project_name}_")
            ]
            for key in keys_to_remove:
                self._processors.pop(key)

            logging.info(f"Cleared cache for store: {project_name}")
            logging.warning(
                "LangChain VectorStores don't support clear operation. Cache cleared only."
            )
        except Exception as e:
            logging.error(f"Failed to clear store {project_name}: {e}")
            raise

    def index_texts(
        self,
        project_name: str,
        texts: List[str],
        embedding_function: Embeddings,
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> int:
        """
        Index raw text documents.
        """
        processor = self._get_document_processor(project_name, embedding_function)
        base_metadata = {"source": "direct_text"}
        if metadatas:
            for i, metadata in enumerate(metadatas):
                metadata.update(base_metadata)

        return processor.process_and_index_texts(texts, base_metadata)

    def get_vector_count(self, project_name: str) -> int:
        """
        Get the number of vectors in a store.
        Note: LangChain VectorStores don't have a standard vector count method.
        """
        logging.warning("Vector count not supported in LangChain interface")
        return -1

    def list_vectors(
        self, project_name: str, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List vectors with metadata.
        Note: LangChain VectorStores don't have a standard list method.
        """
        logging.warning("List vectors not supported in LangChain interface")
        return []
