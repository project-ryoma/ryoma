import logging
from typing import List, Dict, Any, Optional
import time

from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections, utility
from pymilvus.exceptions import MilvusException

from ryoma_ai.vector_store.base import VectorStore, SearchResult
from ryoma_ai.vector_store.config import MilvusVectorStoreConfig


class MilvusVectorStore(VectorStore):
    """
    High-performance Milvus vector store implementation.
    Supports advanced indexing, hybrid search, and scalable vector operations.
    """
    
    def __init__(self, config: MilvusVectorStoreConfig):
        self.config = config
        self.collection: Optional[Collection] = None
        self._connect()
        self._initialize_collection()
    
    def _connect(self):
        """Connect to Milvus server"""
        try:
            connections.connect(
                alias="default",
                host=self.config.host,
                port=self.config.port,
                user=self.config.user,
                password=self.config.password,
                secure=self.config.secure,
                db_name=self.config.db_name,
                timeout=self.config.timeout
            )
            logging.info(f"Connected to Milvus at {self.config.host}:{self.config.port}")
        except MilvusException as e:
            logging.error(f"Failed to connect to Milvus: {e}")
            raise
    
    def _initialize_collection(self):
        """Initialize or create Milvus collection"""
        try:
            # Check if collection exists
            if utility.has_collection(self.config.collection_name):
                if self.config.drop_old:
                    utility.drop_collection(self.config.collection_name)
                    logging.info(f"Dropped existing collection: {self.config.collection_name}")
                else:
                    self.collection = Collection(self.config.collection_name)
                    logging.info(f"Using existing collection: {self.config.collection_name}")
                    return
            
            # Create new collection
            self._create_collection()
            
        except MilvusException as e:
            logging.error(f"Failed to initialize collection: {e}")
            raise
    
    def _create_collection(self):
        """Create a new Milvus collection with optimized schema"""
        # Define collection schema
        fields = [
            FieldSchema(
                name="id", 
                dtype=DataType.VARCHAR, 
                is_primary=True, 
                auto_id=self.config.auto_id,
                max_length=512
            ),
            FieldSchema(
                name="vector", 
                dtype=DataType.FLOAT_VECTOR, 
                dim=self.config.dimension
            ),
            FieldSchema(
                name="metadata", 
                dtype=DataType.JSON
            )
        ]
        
        schema = CollectionSchema(
            fields=fields, 
            description=f"Ryoma vector store collection: {self.config.collection_name}",
            enable_dynamic_field=True
        )
        
        # Create collection
        self.collection = Collection(
            name=self.config.collection_name,
            schema=schema,
            consistency_level=self.config.consistency_level
        )
        
        # Create index for vector field
        self._create_index()
        
        logging.info(f"Created new collection: {self.config.collection_name}")
    
    def _create_index(self):
        """Create optimized vector index"""
        index_params = {
            "metric_type": self.config.distance_metric,
            "index_type": self.config.index_type,
            "params": self.config.index_params
        }
        
        self.collection.create_index(
            field_name="vector",
            index_params=index_params,
            timeout=self.config.timeout
        )
        
        logging.info(f"Created {self.config.index_type} index with {self.config.distance_metric} metric")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.collection:
            self.collection.release()
        connections.disconnect("default")
    
    def index(
        self,
        ids: List[str],
        vectors: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Add or update vectors in Milvus collection"""
        if not ids or not vectors or len(ids) != len(vectors):
            raise ValueError("IDs and vectors must have same non-zero length")
        
        if metadatas and len(metadatas) != len(ids):
            raise ValueError("Metadatas length must match IDs length")
        
        # Validate vector dimensions
        for i, vector in enumerate(vectors):
            if len(vector) != self.config.dimension:
                raise ValueError(f"Vector {i} dimension {len(vector)} doesn't match expected {self.config.dimension}")
        
        try:
            # Prepare data for insertion
            data = [
                ids,
                vectors,
                metadatas if metadatas else [{}] * len(ids)
            ]
            
            # Insert data in batches
            batch_size = self.config.batch_size
            total_inserted = 0
            
            for i in range(0, len(ids), batch_size):
                batch_data = [
                    data[0][i:i + batch_size],  # ids
                    data[1][i:i + batch_size],  # vectors
                    data[2][i:i + batch_size],  # metadata
                ]
                
                insert_result = self.collection.insert(batch_data, timeout=self.config.timeout)
                total_inserted += len(batch_data[0])
                
                logging.debug(f"Inserted batch {i//batch_size + 1}, total: {total_inserted}")
            
            # Flush to ensure data is persisted
            self.collection.flush(timeout=self.config.timeout)
            
            logging.info(f"Successfully indexed {total_inserted} vectors in Milvus")
            
        except MilvusException as e:
            logging.error(f"Failed to index vectors: {e}")
            raise
    
    def search(self, query_vector: List[float], top_k: int = 5) -> List[SearchResult]:
        """Perform vector similarity search"""
        if len(query_vector) != self.config.dimension:
            raise ValueError(f"Query vector dimension {len(query_vector)} doesn't match expected {self.config.dimension}")
        
        try:
            # Load collection into memory if not loaded
            if not self.collection.is_loaded:
                self.collection.load()
            
            # Perform search
            search_results = self.collection.search(
                data=[query_vector],
                anns_field="vector",
                param=self.config.search_params,
                limit=top_k,
                output_fields=["id", "metadata"],
                consistency_level=self.config.consistency_level,
                timeout=self.config.timeout
            )
            
            # Convert results to SearchResult format
            results = []
            for hits in search_results:
                for hit in hits:
                    results.append(SearchResult(
                        id=hit.entity.get("id"),
                        score=float(hit.score),
                        metadata=hit.entity.get("metadata", {})
                    ))
            
            return results
            
        except MilvusException as e:
            logging.error(f"Failed to search vectors: {e}")
            raise
    
    def index_documents(
        self,
        ids: List[str],
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Embed and index documents (requires embedding function)"""
        raise NotImplementedError("Use DocumentProcessor.process_and_index() instead")
    
    def search_documents(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Search using text query (requires embedding function)"""
        raise NotImplementedError("Use DocumentProcessor.search_documents() instead")
    
    def delete(self, ids: List[str]) -> None:
        """Delete vectors by IDs"""
        if not ids:
            return
        
        try:
            # Build delete expression
            id_list = "', '".join(ids)
            expr = f"id in ['{id_list}']"
            
            delete_result = self.collection.delete(expr, timeout=self.config.timeout)
            
            # Flush to ensure deletion is persisted
            self.collection.flush(timeout=self.config.timeout)
            
            logging.info(f"Deleted {len(ids)} vectors from Milvus collection")
            
        except MilvusException as e:
            logging.error(f"Failed to delete vectors: {e}")
            raise
    
    def get_vector_count(self) -> int:
        """Get total number of vectors in collection"""
        try:
            self.collection.flush()
            return self.collection.num_entities
        except MilvusException as e:
            logging.error(f"Failed to get vector count: {e}")
            return 0
    
    def list_vectors(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List stored vectors with metadata"""
        try:
            # Load collection if not loaded
            if not self.collection.is_loaded:
                self.collection.load()
            
            # Query vectors with limit and offset
            results = self.collection.query(
                expr="",  # Empty expression means get all
                output_fields=["id", "metadata"],
                limit=limit,
                offset=offset,
                timeout=self.config.timeout
            )
            
            return [{"id": result["id"], "metadata": result.get("metadata", {})} for result in results]
            
        except MilvusException as e:
            logging.error(f"Failed to list vectors: {e}")
            return []
    
    def clear(self) -> None:
        """Clear all vectors from collection"""
        try:
            # Drop and recreate collection
            utility.drop_collection(self.config.collection_name)
            self._create_collection()
            
            logging.info(f"Cleared all vectors from collection: {self.config.collection_name}")
            
        except MilvusException as e:
            logging.error(f"Failed to clear collection: {e}")
            raise
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get detailed collection information"""
        try:
            return {
                "name": self.collection.name,
                "description": self.collection.description,
                "num_entities": self.collection.num_entities,
                "is_loaded": self.collection.is_loaded,
                "schema": {
                    "fields": [
                        {
                            "name": field.name,
                            "type": str(field.dtype),
                            "is_primary": field.is_primary,
                            "params": field.params
                        }
                        for field in self.collection.schema.fields
                    ]
                },
                "indexes": [
                    {
                        "field_name": index.field_name,
                        "index_name": index.index_name,
                        "params": index.params
                    }
                    for index in self.collection.indexes
                ]
            }
        except MilvusException as e:
            logging.error(f"Failed to get collection info: {e}")
            return {}
    
    def create_partition(self, partition_name: str) -> None:
        """Create a partition for better data organization"""
        try:
            self.collection.create_partition(partition_name)
            logging.info(f"Created partition: {partition_name}")
        except MilvusException as e:
            logging.error(f"Failed to create partition {partition_name}: {e}")
            raise
    
    def hybrid_search(
        self,
        query_vector: List[float],
        filter_expr: str,
        top_k: int = 5
    ) -> List[SearchResult]:
        """Perform hybrid search with metadata filtering"""
        try:
            if not self.collection.is_loaded:
                self.collection.load()
            
            search_results = self.collection.search(
                data=[query_vector],
                anns_field="vector",
                param=self.config.search_params,
                limit=top_k,
                expr=filter_expr,  # Filter expression
                output_fields=["id", "metadata"],
                consistency_level=self.config.consistency_level,
                timeout=self.config.timeout
            )
            
            results = []
            for hits in search_results:
                for hit in hits:
                    results.append(SearchResult(
                        id=hit.entity.get("id"),
                        score=float(hit.score),
                        metadata=hit.entity.get("metadata", {})
                    ))
            
            return results
            
        except MilvusException as e:
            logging.error(f"Failed to perform hybrid search: {e}")
            raise