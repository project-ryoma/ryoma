"""
Metadata Manager - Flexible Batch and Real-time Metadata Processing

Implements both batch preprocessing and real-time integrated approaches for
metadata acquisition as described in the AT&T research paper.

Architecture:
- Batch Mode: Pre-process entire database metadata for high-volume systems
- Real-time Mode: On-demand metadata generation for fresh, task-specific context
- Hybrid Mode: Batch preprocessing with real-time updates
"""

import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from langchain_core.language_models import BaseChatModel
from ryoma_ai.datasource.profiler import DatabaseProfiler
from ryoma_ai.datasource.sql import SqlDataSource

logger = logging.getLogger(__name__)


class MetadataMode(Enum):
    """Metadata processing modes."""

    BATCH = "batch"  # Pre-process all metadata
    REALTIME = "realtime"  # On-demand metadata generation
    HYBRID = "hybrid"  # Batch with real-time updates


@dataclass
class MetadataContext:
    """Complete metadata context for SQL generation."""

    tables: Dict[str, Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    query_patterns: List[Dict[str, Any]]
    last_updated: datetime
    coverage_stats: Dict[str, Any]


@dataclass
class BatchProcessingConfig:
    """Configuration for batch processing."""

    max_workers: int = 4
    chunk_size: int = 10
    update_interval_hours: int = 24
    enable_parallel_processing: bool = True
    include_system_tables: bool = False


class MetadataManager:
    """
    Manages database metadata with flexible batch and real-time processing.

    Supports multiple operational modes:
    1. Batch: Pre-process entire database for high-volume query systems
    2. Real-time: Generate metadata on-demand for fresh context
    3. Hybrid: Use cached metadata with selective real-time updates
    """

    def __init__(
        self,
        datasource: SqlDataSource,
        model: BaseChatModel,
        mode: MetadataMode = MetadataMode.HYBRID,
        batch_config: Optional[BatchProcessingConfig] = None,
        storage_backend: Optional[Any] = None,  # For persistent storage
    ):
        self.datasource = datasource
        self.model = model
        self.mode = mode
        self.batch_config = batch_config or BatchProcessingConfig()
        self.storage_backend = storage_backend

        # Initialize enhanced profiler
        self.profiler = DatabaseProfiler(
            model=model, enable_llm_enhancement=True, sample_size=10000, enable_lsh=True
        )

        # In-memory metadata cache
        self._metadata_cache: Dict[str, Dict[str, Any]] = {}
        self._relationship_cache: Dict[str, List[Dict[str, Any]]] = {}
        self._query_pattern_cache: Dict[str, List[Dict[str, Any]]] = {}

        # Batch processing state
        self._last_batch_update: Optional[datetime] = None
        self._batch_in_progress: bool = False
        self._coverage_stats: Dict[str, Any] = {}

        self.logger = logging.getLogger(__name__)

    # ================================
    # BATCH PROCESSING MODE
    # ================================

    async def initialize_batch_metadata(
        self,
        schemas: Optional[List[str]] = None,
        tables: Optional[List[str]] = None,
        force_refresh: bool = False,
    ) -> MetadataContext:
        """
        Initialize complete database metadata in batch mode.

        This implements the batch preprocessing approach from the pipeline.
        """
        if self._batch_in_progress and not force_refresh:
            self.logger.warning("Batch processing already in progress")
            return self.get_current_metadata_context()

        self.logger.info(
            f"Starting batch metadata initialization (mode: {self.mode.value})"
        )
        start_time = time.time()

        try:
            self._batch_in_progress = True

            # Step 1: Schema Ingestion
            all_tables = await self._discover_database_schema(schemas, tables)
            self.logger.info(f"Discovered {len(all_tables)} tables for processing")

            # Step 2: Batch Profiling
            if self.batch_config.enable_parallel_processing:
                metadata_results = await self._parallel_batch_profiling(all_tables)
            else:
                metadata_results = await self._sequential_batch_profiling(all_tables)

            # Step 3: Relationship Discovery
            relationships = await self._discover_table_relationships(all_tables)

            # Step 4: Query Pattern Mining (if enabled)
            query_patterns = await self._mine_query_patterns(all_tables)

            # Step 5: Build unified context
            metadata_context = self._build_metadata_context(
                metadata_results, relationships, query_patterns
            )

            # Step 6: Persist if storage backend available
            if self.storage_backend:
                await self._persist_metadata_context(metadata_context)

            # Update state
            self._last_batch_update = datetime.now()
            duration = time.time() - start_time

            self.logger.info(
                f"Batch metadata initialization completed in {duration:.2f}s. "
                f"Processed {len(metadata_results)} tables, "
                f"found {len(relationships)} relationships"
            )

            return metadata_context

        finally:
            self._batch_in_progress = False

    async def _discover_database_schema(
        self, schemas: Optional[List[str]] = None, tables: Optional[List[str]] = None
    ) -> List[Tuple[str, Optional[str]]]:
        """Discover all tables in the database."""
        discovered_tables = []

        try:
            if tables:
                # Use provided table list
                for table in tables:
                    if "." in table:
                        schema, table_name = table.split(".", 1)
                        discovered_tables.append((table_name, schema))
                    else:
                        discovered_tables.append((table, None))
            else:
                # Auto-discover from database
                if schemas:
                    for schema in schemas:
                        catalog = self.datasource.get_catalog(schema=schema)
                        for schema_obj in catalog.schemas or []:
                            for table in schema_obj.tables or []:
                                if self._should_include_table(table.table_name, schema):
                                    discovered_tables.append((table.table_name, schema))
                else:
                    # Get all schemas - Warning: may be slow for large databases
                    logger.warning(
                        "Loading full catalog to discover tables - this may be slow for large databases. "
                        "Consider running '/index-catalog' command to enable optimized catalog search."
                    )
                    catalog = self.datasource.get_catalog()
                    for schema_obj in catalog.schemas or []:
                        for table in schema_obj.tables or []:
                            if self._should_include_table(
                                table.table_name, schema_obj.schema_name
                            ):
                                discovered_tables.append(
                                    (table.table_name, schema_obj.schema_name)
                                )

        except Exception as e:
            self.logger.error(f"Error discovering database schema: {str(e)}")

        return discovered_tables

    def _should_include_table(self, table_name: str, schema: Optional[str]) -> bool:
        """Determine if table should be included in batch processing."""
        if not self.batch_config.include_system_tables:
            # Filter out system tables
            system_patterns = ["pg_", "information_schema", "sys_", "sqlite_"]
            if any(
                table_name.lower().startswith(pattern) for pattern in system_patterns
            ):
                return False
            if schema and schema.lower() in [
                "information_schema",
                "pg_catalog",
                "mysql",
                "sys",
            ]:
                return False

        return True

    async def _parallel_batch_profiling(
        self, tables: List[Tuple[str, Optional[str]]]
    ) -> Dict[str, Dict[str, Any]]:
        """Process tables in parallel for faster batch processing."""
        metadata_results = {}

        # Split tables into chunks
        chunks = [
            tables[i : i + self.batch_config.chunk_size]
            for i in range(0, len(tables), self.batch_config.chunk_size)
        ]

        with ThreadPoolExecutor(max_workers=self.batch_config.max_workers) as executor:
            # Submit chunks for processing
            future_to_chunk = {
                executor.submit(self._process_table_chunk, chunk): chunk
                for chunk in chunks
            }

            # Collect results
            for future in as_completed(future_to_chunk):
                chunk = future_to_chunk[future]
                try:
                    chunk_results = future.result()
                    metadata_results.update(chunk_results)
                    self.logger.info(f"Processed chunk with {len(chunk)} tables")
                except Exception as e:
                    self.logger.error(f"Error processing chunk {chunk}: {str(e)}")

        return metadata_results

    def _process_table_chunk(
        self, table_chunk: List[Tuple[str, Optional[str]]]
    ) -> Dict[str, Dict[str, Any]]:
        """Process a chunk of tables synchronously."""
        chunk_results = {}

        for table_name, schema in table_chunk:
            try:
                # Get enhanced table metadata
                table_key = f"{schema}.{table_name}" if schema else table_name

                # Use the enhanced profiler
                table_profile = self.profiler.profile_table(
                    self.datasource, table_name, schema
                )

                # Get enhanced column metadata
                column_metadata = {}
                catalog = self.datasource.get_catalog(schema=schema, table=table_name)

                if catalog.schemas:
                    for schema_obj in catalog.schemas:
                        table_obj = schema_obj.get_table(table_name)
                        if table_obj:
                            for column in table_obj.columns:
                                column_profile = self.profiler.profile_column(
                                    self.datasource, table_name, column.name, schema
                                )
                                enhanced_metadata = (
                                    self.profiler.generate_field_description(
                                        column_profile, table_name, schema
                                    )
                                )
                                column_metadata[column.name] = {
                                    "profile": (
                                        column_profile.model_dump()
                                        if hasattr(column_profile, "model_dump")
                                        else column_profile.__dict__
                                    ),
                                    "enhanced": enhanced_metadata,
                                }

                chunk_results[table_key] = {
                    "table_profile": (
                        table_profile.model_dump()
                        if hasattr(table_profile, "model_dump")
                        else table_profile.__dict__
                    ),
                    "columns": column_metadata,
                    "processed_at": datetime.now().isoformat(),
                }

            except Exception as e:
                self.logger.error(f"Error processing table {table_name}: {str(e)}")
                chunk_results[f"{schema}.{table_name}" if schema else table_name] = {
                    "error": str(e),
                    "processed_at": datetime.now().isoformat(),
                }

        return chunk_results

    async def _sequential_batch_profiling(
        self, tables: List[Tuple[str, Optional[str]]]
    ) -> Dict[str, Dict[str, Any]]:
        """Process tables sequentially."""
        return self._process_table_chunk(tables)

    async def _discover_table_relationships(
        self, tables: List[Tuple[str, Optional[str]]]
    ) -> List[Dict[str, Any]]:
        """Discover relationships between tables."""
        relationships = []

        try:
            # Analyze foreign key relationships
            for table_name, schema in tables:
                table_key = f"{schema}.{table_name}" if schema else table_name

                if table_key in self._metadata_cache:
                    table_metadata = self._metadata_cache[table_key]

                    # Look for potential join relationships
                    for column_name, column_data in table_metadata.get(
                        "columns", {}
                    ).items():
                        enhanced = column_data.get("enhanced", {})
                        join_score = enhanced.get("join_candidate_score", 0)

                        if join_score > 0.5:  # High join candidate
                            relationships.append(
                                {
                                    "from_table": table_name,
                                    "from_column": column_name,
                                    "join_score": join_score,
                                    "relationship_type": "potential_join",
                                    "discovered_at": datetime.now().isoformat(),
                                }
                            )

        except Exception as e:
            self.logger.error(f"Error discovering relationships: {str(e)}")

        return relationships

    async def _mine_query_patterns(
        self, tables: List[Tuple[str, Optional[str]]]
    ) -> List[Dict[str, Any]]:
        """Mine query patterns from logs or heuristics."""
        # Placeholder for query log mining implementation
        patterns = []

        # For now, generate basic patterns based on table metadata
        for table_name, schema in tables:
            table_key = f"{schema}.{table_name}" if schema else table_name

            if table_key in self._metadata_cache:
                self._metadata_cache[table_key]

                # Generate common patterns
                patterns.append(
                    {
                        "table": table_name,
                        "pattern_type": "select_all",
                        "frequency": 1.0,
                        "example_sql": f"SELECT * FROM {table_name}",
                        "discovered_at": datetime.now().isoformat(),
                    }
                )

        return patterns

    # ================================
    # REAL-TIME MODE
    # ================================

    async def get_realtime_metadata(
        self,
        question: str,
        relevant_tables: Optional[List[str]] = None,
        max_tables: int = 5,
    ) -> MetadataContext:
        """
        Generate metadata on-demand for real-time SQL generation.

        This implements the real-time integrated approach.
        """
        self.logger.info(
            f"Generating real-time metadata for question: {question[:100]}..."
        )
        start_time = time.time()

        try:
            # Step 1: Determine relevant tables
            if not relevant_tables:
                relevant_tables = await self._select_relevant_tables_for_question(
                    question, max_tables
                )

            # Step 2: Generate fresh metadata for selected tables
            fresh_metadata = {}
            for table in relevant_tables:
                schema, table_name = self._parse_table_identifier(table)

                # Generate on-demand profiling
                table_profile = self.profiler.profile_table(
                    self.datasource, table_name, schema
                )

                # Get enhanced column metadata
                column_metadata = await self._generate_enhanced_column_metadata(
                    table_name, schema, question
                )

                fresh_metadata[table] = {
                    "table_profile": (
                        table_profile.model_dump()
                        if hasattr(table_profile, "model_dump")
                        else table_profile.__dict__
                    ),
                    "columns": column_metadata,
                    "generated_for_question": question,
                    "processed_at": datetime.now().isoformat(),
                }

            # Step 3: Quick relationship analysis
            relationships = await self._analyze_realtime_relationships(relevant_tables)

            # Step 4: Build context
            metadata_context = MetadataContext(
                tables=fresh_metadata,
                relationships=relationships,
                query_patterns=[],  # Skip expensive pattern mining in real-time
                last_updated=datetime.now(),
                coverage_stats={
                    "mode": "realtime",
                    "tables_analyzed": len(relevant_tables),
                },
            )

            duration = time.time() - start_time
            self.logger.info(f"Real-time metadata generated in {duration:.2f}s")

            return metadata_context

        except Exception as e:
            self.logger.error(f"Error generating real-time metadata: {str(e)}")
            raise

    async def _select_relevant_tables_for_question(
        self, question: str, max_tables: int
    ) -> List[str]:
        """Select most relevant tables for a given question."""
        # Simple keyword-based selection for now
        # In a full implementation, this would use more sophisticated NLP

        question_lower = question.lower()
        relevant_tables = []

        try:
            # Get all tables - Warning: may be slow for large databases
            logger.warning(
                "Loading full catalog for table selection - this may be slow for large databases. "
                "Consider running '/index-catalog' command to enable optimized catalog search."
            )
            catalog = self.datasource.get_catalog()

            for schema_obj in catalog.schemas or []:
                for table in schema_obj.tables or []:
                    table_name = table.table_name.lower()

                    # Simple keyword matching
                    if table_name in question_lower or any(
                        word in table_name for word in question_lower.split()
                    ):
                        full_name = (
                            f"{schema_obj.schema_name}.{table.table_name}"
                            if schema_obj.schema_name
                            else table.table_name
                        )
                        relevant_tables.append(full_name)

                        if len(relevant_tables) >= max_tables:
                            break

                if len(relevant_tables) >= max_tables:
                    break

        except Exception as e:
            self.logger.error(f"Error selecting relevant tables: {str(e)}")

        return relevant_tables[:max_tables]

    async def _generate_enhanced_column_metadata(
        self, table_name: str, schema: Optional[str], question: str
    ) -> Dict[str, Dict[str, Any]]:
        """Generate enhanced column metadata optimized for the specific question."""
        column_metadata = {}

        try:
            catalog = self.datasource.get_catalog(schema=schema, table=table_name)

            if catalog.schemas:
                for schema_obj in catalog.schemas:
                    table_obj = schema_obj.get_table(table_name)
                    if table_obj:
                        for column in table_obj.columns:
                            # Profile column
                            column_profile = self.profiler.profile_column(
                                self.datasource, table_name, column.name, schema
                            )

                            # Generate question-specific enhancement
                            enhanced_metadata = (
                                self.profiler.generate_field_description(
                                    column_profile, table_name, schema
                                )
                            )

                            # Add question-specific context
                            enhanced_metadata["question_relevance"] = (
                                self._assess_column_relevance(column.name, question)
                            )

                            column_metadata[column.name] = {
                                "profile": (
                                    column_profile.model_dump()
                                    if hasattr(column_profile, "model_dump")
                                    else column_profile.__dict__
                                ),
                                "enhanced": enhanced_metadata,
                            }

        except Exception as e:
            self.logger.error(f"Error generating enhanced column metadata: {str(e)}")

        return column_metadata

    # ================================
    # HYBRID MODE
    # ================================

    async def get_hybrid_metadata(
        self,
        question: str,
        relevant_tables: Optional[List[str]] = None,
        force_refresh_tables: Optional[List[str]] = None,
    ) -> MetadataContext:
        """
        Get metadata using hybrid approach: cached + selective real-time updates.

        This provides the best of both worlds.
        """
        self.logger.info(f"Using hybrid metadata approach for: {question[:100]}...")

        # Step 1: Check if batch metadata needs refresh
        needs_batch_refresh = self._needs_batch_refresh()

        if needs_batch_refresh and not self._batch_in_progress:
            # Trigger background batch update (non-blocking)
            asyncio.create_task(self._background_batch_update())

        # Step 2: Get cached metadata
        cached_context = self.get_current_metadata_context()

        # Step 3: Determine tables needing real-time updates
        if not relevant_tables:
            relevant_tables = await self._select_relevant_tables_for_question(
                question, 10
            )

        tables_to_refresh = set()

        # Add explicitly requested refresh tables
        if force_refresh_tables:
            tables_to_refresh.update(force_refresh_tables)

        # Add tables missing from cache
        for table in relevant_tables:
            if table not in cached_context.tables:
                tables_to_refresh.add(table)

        # Step 4: Generate real-time updates for selected tables
        if tables_to_refresh:
            self.logger.info(f"Refreshing {len(tables_to_refresh)} tables in real-time")

            realtime_updates = {}
            for table in tables_to_refresh:
                schema, table_name = self._parse_table_identifier(table)

                table_profile = self.profiler.profile_table(
                    self.datasource, table_name, schema
                )

                column_metadata = await self._generate_enhanced_column_metadata(
                    table_name, schema, question
                )

                realtime_updates[table] = {
                    "table_profile": (
                        table_profile.model_dump()
                        if hasattr(table_profile, "model_dump")
                        else table_profile.__dict__
                    ),
                    "columns": column_metadata,
                    "generated_for_question": question,
                    "processed_at": datetime.now().isoformat(),
                }

            # Merge with cached context
            updated_tables = {**cached_context.tables, **realtime_updates}
        else:
            updated_tables = cached_context.tables

        # Step 5: Return hybrid context
        return MetadataContext(
            tables=updated_tables,
            relationships=cached_context.relationships,
            query_patterns=cached_context.query_patterns,
            last_updated=datetime.now(),
            coverage_stats={
                "mode": "hybrid",
                "cached_tables": len(cached_context.tables),
                "refreshed_tables": len(tables_to_refresh),
                "total_tables": len(updated_tables),
            },
        )

    # ================================
    # UTILITY METHODS
    # ================================

    def get_current_metadata_context(self) -> MetadataContext:
        """Get current metadata context from cache."""
        return MetadataContext(
            tables=self._metadata_cache,
            relationships=self._relationship_cache.get("all", []),
            query_patterns=self._query_pattern_cache.get("all", []),
            last_updated=self._last_batch_update or datetime.now(),
            coverage_stats=self._coverage_stats,
        )

    def _needs_batch_refresh(self) -> bool:
        """Check if batch metadata needs refresh."""
        if not self._last_batch_update:
            return True

        hours_since_update = (
            datetime.now() - self._last_batch_update
        ).total_seconds() / 3600
        return hours_since_update >= self.batch_config.update_interval_hours

    async def _background_batch_update(self):
        """Perform batch update in background."""
        try:
            await self.initialize_batch_metadata()
        except Exception as e:
            self.logger.error(f"Background batch update failed: {str(e)}")

    def _parse_table_identifier(
        self, table_identifier: str
    ) -> Tuple[Optional[str], str]:
        """Parse schema.table or just table."""
        if "." in table_identifier:
            parts = table_identifier.split(".", 1)
            return parts[0], parts[1]
        return None, table_identifier

    def _assess_column_relevance(self, column_name: str, question: str) -> float:
        """Assess how relevant a column is to the specific question."""
        question_lower = question.lower()
        column_lower = column_name.lower()

        # Simple relevance scoring
        score = 0.0

        if column_lower in question_lower:
            score += 0.8

        # Check for partial matches
        question_words = question_lower.split()
        for word in question_words:
            if len(word) > 3 and word in column_lower:
                score += 0.2

        return min(score, 1.0)

    def _build_metadata_context(
        self,
        metadata_results: Dict[str, Dict[str, Any]],
        relationships: List[Dict[str, Any]],
        query_patterns: List[Dict[str, Any]],
    ) -> MetadataContext:
        """Build unified metadata context."""
        # Update caches
        self._metadata_cache = metadata_results
        self._relationship_cache["all"] = relationships
        self._query_pattern_cache["all"] = query_patterns

        # Update coverage stats
        self._coverage_stats = {
            "total_tables": len(metadata_results),
            "total_relationships": len(relationships),
            "total_patterns": len(query_patterns),
            "last_batch_update": datetime.now().isoformat(),
            "processing_mode": self.mode.value,
        }

        return MetadataContext(
            tables=metadata_results,
            relationships=relationships,
            query_patterns=query_patterns,
            last_updated=datetime.now(),
            coverage_stats=self._coverage_stats,
        )

    async def _analyze_realtime_relationships(
        self, tables: List[str]
    ) -> List[Dict[str, Any]]:
        """Quick relationship analysis for real-time mode."""
        # Simplified relationship discovery for speed
        relationships = []

        # This would be more sophisticated in a full implementation
        return relationships

    async def _persist_metadata_context(self, context: MetadataContext):
        """Persist metadata context to storage backend."""
        if not self.storage_backend:
            return

        try:
            # Convert to serializable format
            context_dict = asdict(context)
            context_dict["last_updated"] = context.last_updated.isoformat()

            # Store (implementation depends on storage backend)
            await self.storage_backend.store("metadata_context", context_dict)

        except Exception as e:
            self.logger.error(f"Error persisting metadata context: {str(e)}")

    # ================================
    # PUBLIC API
    # ================================

    async def get_metadata_for_question(
        self,
        question: str,
        relevant_tables: Optional[List[str]] = None,
        max_tables: int = 5,
    ) -> MetadataContext:
        """
        Main entry point for getting metadata based on operational mode.
        """
        if self.mode == MetadataMode.BATCH:
            return self.get_current_metadata_context()
        elif self.mode == MetadataMode.REALTIME:
            return await self.get_realtime_metadata(
                question, relevant_tables, max_tables
            )
        elif self.mode == MetadataMode.HYBRID:
            return await self.get_hybrid_metadata(question, relevant_tables)
        else:
            raise ValueError(f"Unknown metadata mode: {self.mode}")

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get current processing statistics."""
        return {
            "mode": self.mode.value,
            "last_batch_update": (
                self._last_batch_update.isoformat() if self._last_batch_update else None
            ),
            "batch_in_progress": self._batch_in_progress,
            "cache_size": len(self._metadata_cache),
            "coverage_stats": self._coverage_stats,
            "needs_refresh": self._needs_batch_refresh(),
        }
