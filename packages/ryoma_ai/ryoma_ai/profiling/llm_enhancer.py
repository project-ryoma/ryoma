"""
LLM-based Database Profile Enhancement

Provides LLM-powered metadata generation on top of statistical profiling.
Separated from base profiling to maintain clean architecture.
"""

import json
import logging
from typing import Any, Dict, Optional

from ryoma_data.metadata import ColumnProfile


class LLMProfileEnhancer:
    """Enhances statistical profiles with LLM-generated metadata."""

    def __init__(self, model, enable_caching: bool = True):
        """
        Initialize the LLM profile enhancer.

        Args:
            model: LLM model instance (LangChain compatible)
            enable_caching: Whether to cache LLM responses
        """
        self.model = model
        self.enable_caching = enable_caching
        self._llm_cache: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)

    def generate_field_description(
        self, profile: ColumnProfile, table_name: str, schema: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate LLM-enhanced field description and metadata.

        Implements the LLM summarization technique for enhanced metadata.

        Args:
            profile: Statistical column profile
            table_name: Name of the table
            schema: Optional schema name

        Returns:
            Dict with description, business_purpose, sql_hints, join_candidate_score
        """
        cache_key = (
            f"{schema}.{table_name}.{profile.column_name}"
            if schema
            else f"{table_name}.{profile.column_name}"
        )

        if self.enable_caching and cache_key in self._llm_cache:
            return self._llm_cache[cache_key]

        try:
            prompt = self._create_field_analysis_prompt(profile, table_name, schema)
            response = self.model.invoke([{"role": "user", "content": prompt}])

            # Handle different response types
            if hasattr(response, "content"):
                response_text = response.content
            else:
                response_text = str(response)

            enhanced_metadata = self._parse_llm_response(response_text, profile)

            # Cache the result
            if self.enable_caching:
                self._llm_cache[cache_key] = enhanced_metadata

            return enhanced_metadata

        except Exception as e:
            self.logger.error(
                f"LLM enhancement failed for {profile.column_name}: {str(e)}"
            )
            return self._create_fallback_description(profile)

    def _create_field_analysis_prompt(
        self, profile: ColumnProfile, table_name: str, schema: Optional[str] = None
    ) -> str:
        """Create detailed prompt for LLM field analysis optimized for SQL generation."""

        # Prepare sample values
        sample_values = []
        if profile.top_k_values:
            sample_values = [
                str(item.get("value", "")) for item in profile.top_k_values[:5]
            ]
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
"""

        if profile.string_stats:
            type_specific_stats += f"""
String Stats:
- Length range: {profile.string_stats.min_length} to {profile.string_stats.max_length}
- Average length: {profile.string_stats.avg_length:.1f}
"""

        prompt = f"""
Analyze this database field to generate metadata optimized for text-to-SQL generation.

Table: {table_name} {f"(Schema: {schema})" if schema else ""}
Field: {profile.column_name}
Semantic Type: {profile.semantic_type or "general"}

{stats_summary}{type_specific_stats}

Sample Values: {sample_str}

Provide a JSON response:
{{
    "description": "Clear description focusing on field content and role",
    "business_purpose": "Business purpose (e.g., 'Primary identifier', 'Customer contact')",
    "sql_hints": [
        "List 2-4 SQL generation hints like:",
        "- 'Use for JOIN operations'",
        "- 'Filter with LIKE operator'",
        "- 'Good for GROUP BY aggregations'"
    ]
}}

Focus on SQL generation insights.
        """

        return prompt

    def _parse_llm_response(
        self, response_text: str, profile: ColumnProfile
    ) -> Dict[str, Any]:
        """Parse LLM response to extract structured analysis."""
        try:
            # Try to extract JSON from the response
            start = response_text.find("{")
            end = response_text.rfind("}") + 1

            if start >= 0 and end > start:
                json_str = response_text[start:end]
                parsed = json.loads(json_str)

                result = {
                    "description": parsed.get(
                        "description", "Field description unavailable"
                    ),
                    "business_purpose": parsed.get(
                        "business_purpose", "Unknown purpose"
                    ),
                    "sql_hints": parsed.get("sql_hints", []),
                    "join_candidate_score": self._calculate_join_candidate_score(
                        profile
                    ),
                }

                return result

        except Exception as e:
            self.logger.debug(f"Failed to parse LLM response as JSON: {str(e)}")

        # Fallback: extract key information from text
        return {
            "description": (
                response_text[:200] + "..."
                if len(response_text) > 200
                else response_text
            ),
            "business_purpose": "Analysis required",
            "sql_hints": [],
            "join_candidate_score": self._calculate_join_candidate_score(profile),
        }

    def _create_fallback_description(self, profile: ColumnProfile) -> Dict[str, Any]:
        """Create fallback description when LLM analysis fails."""
        hints = []

        # Generate basic SQL hints based on profile
        if profile.semantic_type == "identifier":
            hints.append("Likely used for JOIN operations with other tables")
            hints.append("Use exact equality comparisons (=) in WHERE clauses")
        elif profile.semantic_type == "email":
            hints.append("Use LIKE operator for domain-based filtering")
        elif profile.null_percentage and profile.null_percentage > 20:
            hints.append("Field contains nulls - consider using COALESCE")

        if profile.distinct_ratio and profile.distinct_ratio < 0.1:
            hints.append("Low cardinality - good for GROUP BY aggregations")

        return {
            "description": f"Field containing {profile.semantic_type or 'general'} data",
            "business_purpose": "Requires analysis",
            "sql_hints": hints,
            "join_candidate_score": self._calculate_join_candidate_score(profile),
        }

    def _calculate_join_candidate_score(self, profile: ColumnProfile) -> float:
        """Calculate join candidate score based on profile characteristics."""
        score = 0.0

        # Primary key characteristics
        if profile.distinct_count and profile.row_count:
            distinct_ratio = profile.distinct_count / profile.row_count
            if distinct_ratio == 1.0 and (profile.null_count or 0) == 0:
                score += 0.4  # Perfect uniqueness + no nulls
            # Foreign key characteristics
            elif 0.05 <= distinct_ratio <= 0.8:
                score += 0.25  # Moderate cardinality suggests FK

        # Naming patterns
        field_lower = profile.column_name.lower()
        if field_lower.endswith("_id") or field_lower.endswith("id"):
            score += 0.2
        elif "key" in field_lower:
            score += 0.15

        # Semantic type considerations
        if profile.semantic_type == "identifier":
            score += 0.15

        return min(score, 1.0)  # Cap at 1.0

    def get_enhanced_column_context(
        self,
        profile: ColumnProfile,
        table_name: str,
        schema: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get enhanced column context optimized for SQL generation.

        Combines statistical profiling with LLM-enhanced metadata.

        Args:
            profile: Statistical column profile
            table_name: Name of the table
            schema: Optional schema name

        Returns:
            Dict with comprehensive column context
        """
        # Get LLM enhancement
        enhanced_metadata = self.generate_field_description(profile, table_name, schema)

        return {
            "column_name": profile.column_name,
            "table_name": table_name,
            "description": enhanced_metadata["description"],
            "business_purpose": enhanced_metadata["business_purpose"],
            "semantic_type": profile.semantic_type,
            "nullable": (profile.null_percentage or 0) > 0,
            "sql_hints": enhanced_metadata["sql_hints"],
            "join_score": enhanced_metadata["join_candidate_score"],
            "sample_values": [
                item.get("value") for item in (profile.top_k_values or [])[:3]
            ],
            "data_quality_score": profile.data_quality_score,
            "distinct_ratio": profile.distinct_ratio,
        }
