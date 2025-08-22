import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from ryoma_ai.vector_store.config import DocumentProcessorConfig


class DocumentProcessor:
    """
    Handles document processing, chunking, and indexing for LangChain vector stores.
    Works with any LangChain-compatible vector store (Chroma, FAISS, Qdrant, Milvus, etc.)
    """

    def __init__(
        self,
        vector_store: VectorStore,
        embedding_function: Embeddings,
        config: Optional[DocumentProcessorConfig] = None,
    ):
        self.vector_store = vector_store
        self.embedding_function = embedding_function
        self.config = config or DocumentProcessorConfig()

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
        )

    def process_and_index_file(
        self, file_path: str, metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Process a file and index it into the vector store.
        Returns the number of chunks indexed.
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_path.stat().st_size > self.config.max_file_size_mb * 1024 * 1024:
            raise ValueError(
                f"File too large: {file_path.stat().st_size / (1024*1024):.1f}MB"
            )

        # Extract text based on file type
        file_type = file_path.suffix.lower()

        if file_type == ".pdf":
            documents = self._process_pdf(str(file_path))
        elif file_type == ".txt":
            documents = self._process_txt(str(file_path))
        elif file_type == ".csv":
            documents = self._process_csv(str(file_path))
        elif file_type == ".json":
            documents = self._process_json(str(file_path))
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

        # Add file metadata
        base_metadata = metadata or {}
        base_metadata.update(
            {
                "source_file": str(file_path),
                "file_type": file_type[1:],  # Remove dot
                "file_size": file_path.stat().st_size,
            }
        )

        return self._embed_and_index_documents(documents, base_metadata)

    def process_and_index_texts(
        self, texts: List[str], metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Process raw texts and index them.
        """
        if not texts:
            return 0

        # Chunk texts
        all_chunks = []
        for text in texts:
            chunks = self.text_splitter.split_text(text)
            all_chunks.extend(chunks)

        base_metadata = metadata or {"source": "direct_text"}
        return self._embed_and_index_documents(all_chunks, base_metadata)

    def search_documents(self, query: str, top_k: int = 5) -> List[Document]:
        """
        Search documents using text query.
        Returns LangChain Documents with page_content and metadata.
        """
        try:
            # Use LangChain's similarity search
            results = self.vector_store.similarity_search(query, k=top_k)
            return results

        except Exception as e:
            logging.error(f"Document search failed: {e}")
            raise

    def _process_pdf(self, file_path: str) -> List[str]:
        """Process PDF file"""
        try:
            loader = PyPDFLoader(file_path)
            docs = loader.load()

            # Combine all pages and chunk
            full_text = "\n\n".join([doc.page_content for doc in docs])
            return self.text_splitter.split_text(full_text)

        except Exception as e:
            logging.error(f"Failed to process PDF {file_path}: {e}")
            raise

    def _process_txt(self, file_path: str) -> List[str]:
        """Process text file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

            return self.text_splitter.split_text(text)

        except Exception as e:
            logging.error(f"Failed to process TXT {file_path}: {e}")
            raise

    def _process_csv(self, file_path: str) -> List[str]:
        """Process CSV file"""
        try:
            df = pd.read_csv(file_path)

            # Convert each row to text
            documents = []
            for _, row in df.iterrows():
                # Create a readable text representation of the row
                row_text = "\n".join(
                    [f"{col}: {val}" for col, val in row.items() if pd.notna(val)]
                )
                documents.append(row_text)

            return documents

        except Exception as e:
            logging.error(f"Failed to process CSV {file_path}: {e}")
            raise

    def _process_json(self, file_path: str) -> List[str]:
        """Process JSON file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Handle different JSON structures
            if isinstance(data, list):
                # List of objects
                return [json.dumps(item, indent=2) for item in data]
            elif isinstance(data, dict):
                # Single object - chunk by keys if large
                text = json.dumps(data, indent=2)
                return self.text_splitter.split_text(text)
            else:
                # Simple value
                return [str(data)]

        except Exception as e:
            logging.error(f"Failed to process JSON {file_path}: {e}")
            raise

    def _embed_and_index_documents(
        self, documents: List[str], base_metadata: Dict[str, Any]
    ) -> int:
        """
        Embed documents and index them in the vector store using LangChain interface.
        """
        if not documents:
            return 0

        try:
            # Prepare metadata for each document
            metadatas = []
            for i, doc in enumerate(documents):
                metadata = base_metadata.copy()
                metadata.update(
                    {
                        "chunk_index": i,
                        "content_preview": doc[:200] + "..." if len(doc) > 200 else doc,
                    }
                )
                metadatas.append(metadata)

            # Use LangChain's add_texts method
            self.vector_store.add_texts(texts=documents, metadatas=metadatas)

            logging.info(f"Successfully indexed {len(documents)} document chunks")
            return len(documents)

        except Exception as e:
            logging.error(f"Failed to embed and index documents: {e}")
            raise
