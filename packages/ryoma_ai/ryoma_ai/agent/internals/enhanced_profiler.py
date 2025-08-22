"""
Enhanced Database Profiler with LLM Summarization

Builds on the existing DatabaseProfiler to implement the LLM-based metadata
generation techniques from the AT&T research paper "Automatic Metadata
Extraction for Text-to-SQL" (2505.19988v2).

This module adds:
1. LLM-generated field descriptions and business purpose analysis
2. Task-aligned metadata generation focused on SQL generation
3. Enhanced semantic type inference using LLM understanding
4. Join candidate scoring based on profiling + LLM analysis
"""

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage
from ryoma_ai.datasource.metadata import ColumnProfile, TableProfile
from ryoma_ai.datasource.profiler import DatabaseProfiler
from ryoma_ai.datasource.sql import SqlDataSource

logger = logging.getLogger(__name__)


@dataclass
class EnhancedFieldMetadata:
    """Enhanced field metadata with LLM-generated insights."""

    base_profile: ColumnProfile
    llm_description: str
    business_purpose: str
    sql_generation_hints: List[str]
    join_candidate_score: float
    semantic_tags: List[str]
    data_quality_assessment: str
    usage_patterns: List[str]


@dataclass
class EnhancedTableMetadata:
    """Enhanced table metadata with comprehensive analysis."""

    base_profile: TableProfile
    table_description: str
    primary_purpose: str
    common_join_patterns: List[Dict[str, Any]]
    business_domain: str
    data_freshness_assessment: str
    field_metadata: Dict[str, EnhancedFieldMetadata]


class EnhancedDatabaseProfiler:
    """
    Enhanced database profiler that combines statistical profiling with
    LLM-based metadata generation for text-to-SQL optimization.

    Implements the techniques from "Automatic Metadata Extraction for Text-to-SQL".
    """

    def __init__(
        self,
        datasource: SqlDataSource,
        model: BaseChatModel,
        base_profiler: Optional[DatabaseProfiler] = None,
        enable_llm_analysis: bool = True,
        analysis_sample_size: int = 100,
    ):
        self.datasource = datasource
        self.model = model
        self.enable_llm_analysis = enable_llm_analysis
        self.analysis_sample_size = analysis_sample_size

        # Use existing profiler or create new one
        self.base_profiler = base_profiler or DatabaseProfiler()

        # Cache for enhanced metadata
        self._enhanced_cache: Dict[str, EnhancedFieldMetadata] = {}
        self._table_cache: Dict[str, EnhancedTableMetadata] = {}

    def profile_table_enhanced(
        self, table_name: str, schema: Optional[str] = None
    ) -> EnhancedTableMetadata:
        """
        Generate enhanced table metadata with LLM analysis.

        This is the main method that implements the paper's approach.
        """
        cache_key = f"{schema}.{table_name}" if schema else table_name
        if cache_key in self._table_cache:
            return self._table_cache[cache_key]

        logger.info(f"Generating enhanced metadata for table: {table_name}")

        # Step 1: Get base profiling data
        base_table_profile = self.base_profiler.profile_table(
            self.datasource, table_name, schema
        )

        # Step 2: Profile all columns with enhanced analysis
        field_metadata = {}
        try:
            # Get table schema to find all columns
            catalog = self.datasource.get_catalog(schema=schema, table=table_name)
            if catalog.schemas:
                table_obj = None
                for schema_obj in catalog.schemas:
                    table_obj = schema_obj.get_table(table_name)
                    if table_obj:
                        break

                if table_obj:
                    for column in table_obj.columns:
                        enhanced_field = self.profile_field_enhanced(
                            table_name, column.name, schema
                        )
                        field_metadata[column.name] = enhanced_field
        except Exception as e:
            logger.error(f"Error getting table schema for {table_name}: {str(e)}")

        # Step 3: Generate table-level LLM analysis
        table_analysis = self._generate_table_analysis(
            table_name, base_table_profile, field_metadata, schema
        )

        # Step 4: Analyze join patterns
        join_patterns = self._analyze_join_patterns(table_name, field_metadata, schema)

        # Create enhanced table metadata
        enhanced_metadata = EnhancedTableMetadata(
            base_profile=base_table_profile,
            table_description=table_analysis.get("description", ""),
            primary_purpose=table_analysis.get("primary_purpose", ""),
            common_join_patterns=join_patterns,
            business_domain=table_analysis.get("business_domain", ""),
            data_freshness_assessment=table_analysis.get("data_freshness", ""),
            field_metadata=field_metadata,
        )

        # Cache the result
        self._table_cache[cache_key] = enhanced_metadata

        return enhanced_metadata

    def profile_field_enhanced(
        self, table_name: str, field_name: str, schema: Optional[str] = None
    ) -> EnhancedFieldMetadata:
        """Generate enhanced field metadata with LLM analysis."""
        cache_key = (
            f"{schema}.{table_name}.{field_name}"
            if schema
            else f"{table_name}.{field_name}"
        )
        if cache_key in self._enhanced_cache:
            return self._enhanced_cache[cache_key]

        # Step 1: Get base column profile
        base_profile = self.base_profiler.profile_column(
            self.datasource, table_name, field_name, schema
        )

        # Step 2: Generate LLM analysis
        llm_analysis = {}
        if self.enable_llm_analysis:
            llm_analysis = self._generate_field_analysis(
                base_profile, table_name, schema
            )

        # Step 3: Calculate enhanced join candidate score
        join_score = self._calculate_enhanced_join_score(base_profile, llm_analysis)

        # Step 4: Generate SQL-specific usage patterns
        usage_patterns = self._generate_sql_usage_patterns(base_profile, llm_analysis)

        # Create enhanced metadata
        enhanced_metadata = EnhancedFieldMetadata(
            base_profile=base_profile,
            llm_description=llm_analysis.get(
                "description", f"Field containing {base_profile.column_name} data"
            ),
            business_purpose=llm_analysis.get("business_purpose", "Unknown"),
            sql_generation_hints=llm_analysis.get("sql_hints", []),
            join_candidate_score=join_score,
            semantic_tags=self._generate_enhanced_semantic_tags(
                base_profile, llm_analysis
            ),
            data_quality_assessment=llm_analysis.get(
                "data_quality", "Assessment unavailable"
            ),
            usage_patterns=usage_patterns,
        )

        # Cache the result
        self._enhanced_cache[cache_key] = enhanced_metadata

        return enhanced_metadata

    def _generate_field_analysis(
        self, profile: ColumnProfile, table_name: str, schema: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate LLM-based field analysis following the research paper approach."""
        if not self.enable_llm_analysis:
            return {}

        # Create comprehensive prompt for field analysis
        prompt = self._create_field_analysis_prompt(profile, table_name, schema)

        try:
            response = self.model.invoke([HumanMessage(content=prompt)])
            if isinstance(response, BaseMessage):
                response_text = response.content
            else:
                response_text = str(response)

            # Parse LLM response
            return self._parse_field_analysis_response(response_text)

        except Exception as e:
            logger.error(
                f"LLM field analysis failed for {profile.column_name}: {str(e)}"
            )
            return self._create_fallback_analysis(profile)

    def _create_field_analysis_prompt(
        self, profile: ColumnProfile, table_name: str, schema: Optional[str] = None
    ) -> str:
        """Create detailed prompt for LLM field analysis optimized for SQL generation."""

        # Prepare sample values
        sample_values = []
        if profile.top_k_values:
            sample_values = [item.get("value", "") for item in profile.top_k_values[:5]]
        sample_str = (
            ", ".join([f"'{v}'" for v in sample_values if v]) or "No samples available"
        )

        # Prepare statistics summary
        stats_summary = f"""
Statistics:
- Total records: {profile.row_count or "Unknown"}
- Null percentage: {profile.null_percentage or 0:.1f}%
- Distinct values: {profile.distinct_count or "Unknown"}
- Distinct ratio: {profile.distinct_ratio or 0:.3f}
"""

        # Add type-specific stats
        type_specific_stats = ""
        if profile.numeric_stats:
            type_specific_stats += f"""
Numeric Stats:
- Range: {profile.numeric_stats.min_value} to {profile.numeric_stats.max_value}
- Average: {profile.numeric_stats.mean:.2f}
- Standard deviation: {profile.numeric_stats.std_dev:.2f}
"""

        if profile.string_stats:
            type_specific_stats += f"""
String Stats:
- Length range: {profile.string_stats.min_length} to {profile.string_stats.max_length} characters
- Average length: {profile.string_stats.avg_length:.1f}
- Character types: {profile.string_stats.character_types}
"""

        prompt = f"""
You are analyzing a database field to generate metadata optimized for text-to-SQL generation.
Focus on information that would help an AI system understand how to use this field in SQL queries.

Table: {table_name} {f"(Schema: {schema})" if schema else ""}
Field: {profile.column_name}
Data Type: {getattr(profile, "data_type", "Unknown")}
Semantic Type: {profile.semantic_type or "general"}

{stats_summary}{type_specific_stats}

Sample Values: {sample_str}

Please analyze this field and provide a JSON response with the following structure:
{{
    "description": "Clear, concise description focusing on what this field contains and its role in the table",
    "business_purpose": "What business purpose this field serves (e.g., 'Primary identifier', 'Customer contact info', 'Transaction timestamp')",
    "sql_hints": [
        "List of 2-4 specific hints for SQL generation, such as:",
        "- 'Use for JOIN operations with customer_id fields in other tables'",
        "- 'Filter with date ranges using BETWEEN operator'",
        "- 'Group by this field for aggregation queries'",
        "- 'Use LIKE operator for partial matching'"
    ],
    "data_quality": "Assessment of data quality and any SQL-relevant considerations (e.g., 'High quality, suitable for joins', 'Contains nulls, use COALESCE', 'Low cardinality, good for grouping')",
    "join_indicators": [
        "List potential join relationships based on naming and content patterns"
    ]
}}

Focus on practical SQL generation insights rather than general descriptions.
Consider how this field would be used in WHERE clauses, JOINs, GROUP BY, and SELECT statements.
"""

        return prompt

    def _parse_field_analysis_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response to extract structured analysis."""
        try:
            # Try to extract JSON from the response
            start = response_text.find("{")
            end = response_text.rfind("}") + 1

            if start >= 0 and end > start:
                json_str = response_text[start:end]
                parsed = json.loads(json_str)

                # Ensure required fields exist with defaults
                return {
                    "description": parsed.get(
                        "description", "Field description unavailable"
                    ),
                    "business_purpose": parsed.get(
                        "business_purpose", "Unknown purpose"
                    ),
                    "sql_hints": parsed.get("sql_hints", []),
                    "data_quality": parsed.get(
                        "data_quality", "Quality assessment unavailable"
                    ),
                    "join_indicators": parsed.get("join_indicators", []),
                }
        except Exception as e:
            logger.debug(f"Failed to parse LLM response as JSON: {str(e)}")

        # Fallback: extract key information from text
        return {
            "description": (
                response_text[:200] + "..."
                if len(response_text) > 200
                else response_text
            ),
            "business_purpose": "Analysis required",
            "sql_hints": [],
            "data_quality": "Manual review needed",
            "join_indicators": [],
        }

    def _create_fallback_analysis(self, profile: ColumnProfile) -> Dict[str, Any]:
        """Create fallback analysis when LLM analysis fails."""
        hints = []

        # Generate basic SQL hints based on profile
        if profile.semantic_type == "identifier":
            hints.append("Likely used for JOIN operations with other tables")
            hints.append("Use exact equality comparisons (=) in WHERE clauses")
        elif profile.semantic_type == "email":
            hints.append("Use LIKE operator for domain-based filtering")
            hints.append("Consider LOWER() for case-insensitive searches")
        elif profile.null_percentage and profile.null_percentage > 20:
            hints.append(
                "Field contains nulls - consider using COALESCE or IS NULL checks"
            )

        if profile.distinct_ratio and profile.distinct_ratio < 0.1:
            hints.append("Low cardinality - good for GROUP BY aggregations")

        return {
            "description": f"Field containing {profile.semantic_type or 'general'} data",
            "business_purpose": "Requires manual analysis",
            "sql_hints": hints,
            "data_quality": f"Null percentage: {profile.null_percentage:.1f}%",
            "join_indicators": [],
        }

    def _calculate_enhanced_join_score(
        self, profile: ColumnProfile, llm_analysis: Dict[str, Any]
    ) -> float:
        """Calculate enhanced join candidate score using base profile + LLM insights."""
        score = 0.0

        # Base score from statistical characteristics
        if profile.distinct_count and profile.row_count:
            distinct_ratio = profile.distinct_count / profile.row_count

            # Primary key characteristics
            if distinct_ratio == 1.0 and (profile.null_count or 0) == 0:
                score += 0.4  # Perfect uniqueness + no nulls
            # Foreign key characteristics
            elif 0.05 <= distinct_ratio <= 0.8:
                score += 0.25  # Moderate cardinality suggests FK

        # Naming patterns
        field_lower = profile.column_name.lower()
        if field_lower.endswith("_id") or field_lower.endswith("id"):
            score += 0.2
        elif "key" in field_lower or field_lower.startswith("fk_"):
            score += 0.15

        # LLM analysis boost
        join_indicators = llm_analysis.get("join_indicators", [])
        if join_indicators:
            score += min(0.2, len(join_indicators) * 0.05)

        # SQL hints mentioning joins
        sql_hints = llm_analysis.get("sql_hints", [])
        join_mentions = sum(1 for hint in sql_hints if "join" in hint.lower())
        if join_mentions > 0:
            score += 0.1

        # Semantic type considerations
        if profile.semantic_type == "identifier":
            score += 0.15

        return min(score, 1.0)  # Cap at 1.0

    def _generate_enhanced_semantic_tags(
        self, profile: ColumnProfile, llm_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate enhanced semantic tags combining profile + LLM analysis."""
        tags = []

        # Base tags from profile
        if profile.semantic_type:
            tags.append(profile.semantic_type)

        # Cardinality-based tags
        if profile.distinct_count and profile.row_count:
            distinct_ratio = profile.distinct_count / profile.row_count
            if distinct_ratio == 1.0:
                tags.append("unique")
            elif distinct_ratio < 0.05:
                tags.append("low_cardinality")
            elif distinct_ratio > 0.9:
                tags.append("high_cardinality")

        # Null handling
        if profile.null_percentage:
            if profile.null_percentage == 0:
                tags.append("not_null")
            elif profile.null_percentage > 50:
                tags.append("high_nulls")

        # Extract tags from LLM analysis
        business_purpose = llm_analysis.get("business_purpose", "").lower()
        if "primary" in business_purpose and "identifier" in business_purpose:
            tags.append("primary_key")
        elif "foreign" in business_purpose or "reference" in business_purpose:
            tags.append("foreign_key")
        elif "timestamp" in business_purpose or "datetime" in business_purpose:
            tags.append("temporal")

        # Data quality tags
        data_quality = llm_analysis.get("data_quality", "").lower()
        if "high quality" in data_quality:
            tags.append("high_quality")
        elif "suitable for joins" in data_quality:
            tags.append("join_ready")

        return list(set(tags))  # Remove duplicates

    def _generate_sql_usage_patterns(
        self, profile: ColumnProfile, llm_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate SQL usage patterns for this field."""
        patterns = []

        # Extract from LLM hints
        sql_hints = llm_analysis.get("sql_hints", [])
        for hint in sql_hints:
            hint_lower = hint.lower()
            if "join" in hint_lower:
                patterns.append("join_operations")
            elif "filter" in hint_lower or "where" in hint_lower:
                patterns.append("filtering")
            elif "group" in hint_lower:
                patterns.append("grouping")
            elif "like" in hint_lower:
                patterns.append("pattern_matching")
            elif "order" in hint_lower:
                patterns.append("ordering")

        # Infer from profile characteristics
        if profile.semantic_type == "identifier":
            patterns.extend(["exact_matching", "join_operations"])
        elif profile.semantic_type == "email":
            patterns.extend(["pattern_matching", "domain_filtering"])

        if profile.null_percentage and profile.null_percentage > 10:
            patterns.append("null_handling")

        if profile.distinct_ratio and profile.distinct_ratio < 0.1:
            patterns.append("aggregation")

        return list(set(patterns))

    def _generate_table_analysis(
        self,
        table_name: str,
        table_profile: TableProfile,
        field_metadata: Dict[str, EnhancedFieldMetadata],
        schema: Optional[str] = None,
    ) -> Dict[str, str]:
        """Generate table-level LLM analysis."""
        if not self.enable_llm_analysis or not field_metadata:
            return {
                "description": f"Table {table_name} with {table_profile.column_count or 0} columns",
                "primary_purpose": "Unknown",
                "business_domain": "Unknown",
                "data_freshness": "Unknown",
            }

        # Summarize field information for context
        field_summary = []
        for field_name, metadata in list(field_metadata.items())[
            :10
        ]:  # Limit for prompt size
            field_summary.append(f"- {field_name}: {metadata.llm_description[:100]}")

        prompt = f"""
Analyze this database table to understand its business purpose and usage patterns:

Table: {table_name} {f"(Schema: {schema})" if schema else ""}
Columns: {table_profile.column_count or 0}
Rows: {table_profile.row_count or "Unknown"}

Key Fields:
{chr(10).join(field_summary[:10])}

Provide a JSON response:
{{
    "description": "Concise description of what this table stores and its role in the database",
    "primary_purpose": "Main business purpose (e.g., 'Customer management', 'Transaction logging', 'Product catalog')",
    "business_domain": "Business domain this table belongs to (e.g., 'Sales', 'HR', 'Inventory', 'Finance')",
    "data_freshness": "Assessment of data freshness based on patterns observed"
}}
"""

        try:
            response = self.model.invoke([HumanMessage(content=prompt)])
            if isinstance(response, BaseMessage):
                response_text = response.content
            else:
                response_text = str(response)

            # Parse response
            try:
                start = response_text.find("{")
                end = response_text.rfind("}") + 1
                if start >= 0 and end > start:
                    return json.loads(response_text[start:end])
            except (json.JSONDecodeError, ValueError):
                pass

        except Exception as e:
            logger.error(f"Table analysis failed for {table_name}: {str(e)}")

        # Fallback
        return {
            "description": f"Database table {table_name} containing {table_profile.column_count or 0} columns",
            "primary_purpose": "Data storage",
            "business_domain": "Unknown",
            "data_freshness": "Assessment needed",
        }

    def _analyze_join_patterns(
        self,
        table_name: str,
        field_metadata: Dict[str, EnhancedFieldMetadata],
        schema: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Analyze potential join patterns for the table."""
        join_patterns = []

        for field_name, metadata in field_metadata.items():
            if metadata.join_candidate_score > 0.5:  # High join candidate score
                pattern = {
                    "field": field_name,
                    "score": metadata.join_candidate_score,
                    "type": (
                        "primary_key"
                        if metadata.join_candidate_score > 0.8
                        else "foreign_key"
                    ),
                    "indicators": metadata.base_profile.semantic_type,
                    "usage_hint": f"Likely joins with other tables on {field_name}",
                }
                join_patterns.append(pattern)

        return sorted(join_patterns, key=lambda x: x["score"], reverse=True)

    def get_enhanced_metadata_summary(
        self, table_name: str, schema: Optional[str] = None
    ) -> str:
        """Get human-readable summary of enhanced table metadata."""
        enhanced_metadata = self.profile_table_enhanced(table_name, schema)

        # Summarize key fields
        key_fields = []
        for field_name, field_meta in enhanced_metadata.field_metadata.items():
            if field_meta.join_candidate_score > 0.5:
                key_fields.append(f"- {field_name}: {field_meta.business_purpose}")

        summary = f"""
Table: {enhanced_metadata.base_profile.table_name}
Description: {enhanced_metadata.table_description}
Primary Purpose: {enhanced_metadata.primary_purpose}
Business Domain: {enhanced_metadata.business_domain}

Statistics:
- Rows: {enhanced_metadata.base_profile.row_count:,} 
- Columns: {enhanced_metadata.base_profile.column_count}
- Completeness: {enhanced_metadata.base_profile.completeness_score:.1%} if enhanced_metadata.base_profile.completeness_score else 'Unknown'

Key Fields for SQL Generation:
{chr(10).join(key_fields[:5]) if key_fields else "- No high-confidence join candidates identified"}

Join Patterns:
{chr(10).join([f"- {p['field']}: {p['type']} (score: {p['score']:.2f})" for p in enhanced_metadata.common_join_patterns[:3]]) if enhanced_metadata.common_join_patterns else "- No join patterns identified"}

Data Quality: {enhanced_metadata.data_freshness_assessment}
        """

        return summary.strip()

    def get_sql_generation_context(
        self, table_name: str, schema: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get optimized context for SQL generation tasks.

        This provides the metadata in a format optimized for text-to-SQL models.
        """
        enhanced_metadata = self.profile_table_enhanced(table_name, schema)

        # Prepare field context optimized for SQL generation
        field_contexts = {}
        for field_name, field_meta in enhanced_metadata.field_metadata.items():
            field_contexts[field_name] = {
                "description": field_meta.llm_description,
                "type": field_meta.base_profile.semantic_type,
                "nullable": (field_meta.base_profile.null_percentage or 0) > 0,
                "sql_hints": field_meta.sql_generation_hints,
                "join_score": field_meta.join_candidate_score,
                "sample_values": [
                    item.get("value")
                    for item in (field_meta.base_profile.top_k_values or [])[:3]
                ],
                "usage_patterns": field_meta.usage_patterns,
            }

        return {
            "table_name": table_name,
            "table_description": enhanced_metadata.table_description,
            "primary_purpose": enhanced_metadata.primary_purpose,
            "business_domain": enhanced_metadata.business_domain,
            "total_rows": enhanced_metadata.base_profile.row_count,
            "fields": field_contexts,
            "join_candidates": [
                {
                    "field": pattern["field"],
                    "type": pattern["type"],
                    "score": pattern["score"],
                }
                for pattern in enhanced_metadata.common_join_patterns
            ],
        }
