import logging
import os
from typing import Optional, List, Dict, Any

import reflex as rx
from langchain.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain.vectorstores import VectorStore
from langchain.embeddings.base import Embeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from ryoma_lab.models.vector_store import VectorStore as VectorStoreModel
from ryoma_lab.states.ai import AIState
from ryoma_lab.states.embedding import EmbeddingState


class VectorStoreState(AIState):
    vector_store: str = "qdrant"
    vector_store_configs: Optional[dict[str, str]] = {
        "collection_name": "default_collection",
    }

    create_store_dialog_open: bool = False
    add_documents_dialog_open: bool = False

    files: List[str] = []

    _current_vector_store: Optional[VectorStore] = None
    _current_embedding_model: Optional[Embeddings] = None

    def set_vector_store_config(self, key: str, value: str):
        self.vector_store_configs[key] = value

    def toggle_create_store_dialog(self):
        self.create_store_dialog_open = not self.create_store_dialog_open

    def toggle_add_documents_dialog(self):
        self.add_documents_dialog_open = not self.add_documents_dialog_open

    def create_vector_store(self):
        try:
            self._current_embedding_model = self._create_embedding_model()
            self._current_vector_store = self._create_vector_store()
            
            new_store = VectorStoreModel(
                vector_store=self.vector_store,
                vector_store_configs=self.vector_store_configs,
            )
            
            with rx.session() as session:
                session.add(new_store)
                session.commit()
            
            self.toggle_create_store_dialog()
        except Exception as e:
            logging.error(f"Error creating vector store: {e}")
            raise e

    async def handle_upload(self, files: List[rx.UploadFile]):
        for file in files:
            file_content = await file.read()
            file_path = f"{self.project_name}/{file.filename}"
            
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            self.files.append(file_path)

    def add_documents(self):
        if not self._current_vector_store or not self._current_embedding_model:
            raise ValueError("Vector store or embedding model not initialized")

        for file_path in self.files:
            file_type = self._get_file_type(file_path)
            if file_type == "pdf":
                docs = PyPDFLoader(file_path).load()
            elif file_type == "txt":
                docs = TextLoader(file_path).load()
            elif file_type == "docx":
                docs = Docx2txtLoader(file_path).load()
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            self._current_vector_store.add_documents(docs)

        self.files = []
        self.toggle_add_documents_dialog()

    def _create_embedding_model(self) -> Embeddings:
        return EmbeddingState._create_embedding_client()

    def _create_vector_store(self) -> VectorStore:
        client = QdrantClient(":memory:")
        return QdrantVectorStore(
            client=client,
            collection_name=self.vector_store_configs["collection_name"],
            embeddings=self._current_embedding_model,
        )

    def _process_pdf_source(self, file_path: str):
        try:
            docs = PyPDFLoader(file_path).load()
            self._current_vector_store.add_documents(docs)
        except Exception as e:
            logging.error(f"Error processing PDF source: {e}")
            raise e

    def _get_file_type(self, file: str) -> str:
        supported_file_types = {
            ".pdf": "pdf",
            ".txt": "txt",
            ".docx": "docx",
        }
        file_type = os.path.splitext(file)[1].lower()
        return supported_file_types.get(file_type, "unknown")

    def load_store(self):
        with rx.session() as session:
            self.store = session.query(VectorStoreModel).all()

    def on_load(self) -> None:
        self.load_store()
