"""
Database Profiler Implementation

This module implements comprehensive database profiling capabilities based on the
"Automatic Metadata Extraction for Text-to-SQL" paper (2505.19988v2), including:

- Row counts & NULL statistics
- Distinct-value ratio per column
- Numeric/date min, max, mean
- String length & character-type stats
- Top-k frequent values
- Locality-sensitive hashing / MinHash sketches for approximate similarity

This implementation leverages Ibis's native profiling capabilities where possible
for better performance and backend compatibility.
"""

import logging
import re
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from datasketch import MinHash, MinHashLSH
from ryoma_data.metadata import (
    ColumnProfile,
    DateStats,
    LSHSketch,
    NumericStats,
    StringStats,
    TableProfile,
)


class DatabaseProfiler:
    """
    Comprehensive database profiler that extracts detailed metadata from database tables.

    Implements the profiling techniques described in the "Automatic Metadata Extraction
    for Text-to-SQL" paper.
    """

    def __init__(
        self,
        sample_size: int = 10000,
        top_k: int = 10,
        lsh_threshold: float = 0.8,
        num_hashes: int = 128,
        enable_lsh: bool = True,
    ):
        """
        Initialize the database profiler.

        Args:
            sample_size: Maximum number of rows to sample for profiling
            top_k: Number of top frequent values to store
            lsh_threshold: Jaccard similarity threshold for LSH
            num_hashes: Number of hash functions for MinHash
            enable_lsh: Whether to compute LSH sketches
        """
        self.sample_size = sample_size
        self.top_k = top_k
        self.lsh_threshold = lsh_threshold
        self.num_hashes = num_hashes
        self.enable_lsh = enable_lsh

        # LSH index for similarity search
        if enable_lsh:
            self.lsh_index = MinHashLSH(threshold=lsh_threshold, num_perm=num_hashes)

        self.logger = logging.getLogger(__name__)

    def profile_table(
        self, datasource, table_name: str, schema: Optional[str] = None
    ) -> TableProfile:
        """
        Profile a table using Ibis's native profiling capabilities for optimal performance.

        Args:
            datasource: The SQL datasource to profile
            table_name: Name of the table to profile
            schema: Optional schema name

        Returns:
            TableProfile with comprehensive metadata using Ibis native methods
        """
        start_time = datetime.now()

        try:
            # Get the database table object
            conn = datasource.connect()

            # Build the table reference
            if schema:
                table = conn.table(table_name, database=schema)
            else:
                table = conn.table(table_name)

            # Use native describe() method for comprehensive statistics
            describe_result = table.describe().to_pandas()
            self.logger.info(
                f"Successfully profiled table {table_name} using native methods"
            )

            # Extract table-level metrics from describe result
            row_count = (
                int(describe_result["count"].iloc[0])
                if not describe_result.empty
                else 0
            )
            column_count = len(describe_result)

            # Calculate completeness from null fractions
            if "null_frac" in describe_result.columns:
                null_fractions = describe_result["null_frac"].fillna(0)
                completeness_score = float(1.0 - null_fractions.mean())
            else:
                # Fallback: calculate completeness from count vs non-null count
                if "count" in describe_result.columns and row_count > 0:
                    non_null_counts = describe_result["count"].fillna(0)
                    completeness_score = float(non_null_counts.mean() / row_count)
                else:
                    completeness_score = 1.0

            # Calculate consistency score from describe result
            consistency_score = self._calculate_consistency_from_describe(
                describe_result
            )

            # Get actual row count
            actual_row_count = int(table.count().to_pandas())

            duration = (datetime.now() - start_time).total_seconds()

            return TableProfile(
                table_name=table_name,
                row_count=actual_row_count,
                column_count=column_count,
                completeness_score=completeness_score,
                consistency_score=consistency_score,
                profiled_at=datetime.now(),
                profiling_duration_seconds=duration,
            )

        except Exception as e:
            self.logger.error(f"Error profiling table {table_name}: {str(e)}")
            # Return minimal profile on error
            return TableProfile(
                table_name=table_name,
                row_count=0,
                column_count=0,
                completeness_score=0.0,
                consistency_score=0.0,
                profiled_at=datetime.now(),
                profiling_duration_seconds=(
                    datetime.now() - start_time
                ).total_seconds(),
            )

    def profile_column(
        self,
        datasource,
        table_name: str,
        column_name: str,
        schema: Optional[str] = None,
    ) -> ColumnProfile:
        """
        Profile a single column using database-native capabilities for optimal performance.

        Args:
            datasource: The SQL datasource to profile
            table_name: Name of the table
            column_name: Name of the column to profile
            schema: Optional schema name

        Returns:
            ColumnProfile with detailed statistics using database-native methods
        """
        try:
            # Get the database table object
            conn = datasource.connect()

            if schema:
                table = conn.table(table_name, database=schema)
            else:
                table = conn.table(table_name)

            # Get the specific column
            if column_name not in table.columns:
                self.logger.warning(
                    f"Column {column_name} not found in table {table_name}"
                )
                return ColumnProfile(
                    column_name=column_name, profiled_at=datetime.now()
                )

            column = table[column_name]

            # Use database-native statistical methods
            try:
                # Basic statistics using native methods
                row_count = int(table.count().to_pandas())

                # Count non-null values
                non_null_count = int(column.count().to_pandas())
                null_count = row_count - non_null_count
                null_percentage = (null_count / row_count) * 100 if row_count > 0 else 0

                # Distinct count using native functions
                distinct_count = int(column.nunique().to_pandas())
                distinct_ratio = (
                    distinct_count / non_null_count if non_null_count > 0 else 0
                )

                # Top-k frequent values using native value_counts
                top_k_values = self._get_top_k_values(column)

                # Type-specific statistics using native methods
                numeric_stats = self._compute_numeric_stats(column)
                date_stats = self._compute_date_stats(column)
                string_stats = self._compute_string_stats(column)

                # LSH sketch (still need to sample data for this)
                lsh_sketch = None
                if self.enable_lsh:
                    try:
                        # Sample data for LSH computation
                        sample_data = (
                            column.limit(min(1000, self.sample_size))
                            .to_pandas()
                            .dropna()
                        )
                        if len(sample_data) > 0:
                            lsh_sketch = self._compute_lsh_sketch(
                                sample_data, column_name
                            )
                    except Exception as e:
                        self.logger.debug(
                            f"LSH computation failed for {column_name}: {e}"
                        )

                # Semantic type inference
                semantic_type = self._infer_semantic_type(column, column_name)

                # Data quality score
                data_quality_score = self._calculate_data_quality_score(
                    null_percentage, distinct_ratio, non_null_count
                )

                return ColumnProfile(
                    column_name=column_name,
                    row_count=row_count,
                    null_count=null_count,
                    null_percentage=null_percentage,
                    distinct_count=distinct_count,
                    distinct_ratio=distinct_ratio,
                    top_k_values=top_k_values,
                    numeric_stats=numeric_stats,
                    date_stats=date_stats,
                    string_stats=string_stats,
                    lsh_sketch=lsh_sketch,
                    semantic_type=semantic_type,
                    data_quality_score=data_quality_score,
                    profiled_at=datetime.now(),
                    sample_size=min(row_count, self.sample_size),
                )

            except Exception as e:
                self.logger.error(
                    f"Native profiling failed for column {column_name}: {e}"
                )
                # Return minimal profile on error
                return ColumnProfile(
                    column_name=column_name,
                    row_count=0,
                    null_count=0,
                    null_percentage=100.0,
                    distinct_count=0,
                    distinct_ratio=0.0,
                    profiled_at=datetime.now(),
                    sample_size=0,
                )

        except Exception as e:
            self.logger.error(f"Error profiling column {column_name}: {str(e)}")
            # Return minimal profile on error
            return ColumnProfile(
                column_name=column_name,
                row_count=0,
                null_count=0,
                null_percentage=100.0,
                distinct_count=0,
                distinct_ratio=0.0,
                profiled_at=datetime.now(),
                sample_size=0,
            )

    def _compute_lsh_sketch(
        self, data: pd.Series, column_name: str
    ) -> Optional[LSHSketch]:
        """Compute LSH sketch for similarity matching."""
        try:
            # Create MinHash object
            minhash = MinHash(num_perm=self.num_hashes)

            # Add data to MinHash
            for value in data.head(1000):  # Sample for performance
                # Convert value to string and create shingles
                text = str(value).lower()
                shingles = self._create_shingles(text, k=3)
                for shingle in shingles:
                    minhash.update(shingle.encode("utf-8"))

            # Store in LSH index
            if hasattr(self, "lsh_index"):
                self.lsh_index.insert(column_name, minhash)

            return LSHSketch(
                hash_values=list(minhash.hashvalues),
                num_hashes=self.num_hashes,
                jaccard_threshold=self.lsh_threshold,
            )
        except Exception:
            return None

    def _create_shingles(self, text: str, k: int = 3) -> List[str]:
        """Create k-shingles from text."""
        if len(text) < k:
            return [text]
        return [text[i : i + k] for i in range(len(text) - k + 1)]

    def _calculate_data_quality_score(
        self, null_percentage: float, distinct_ratio: float, sample_size: int
    ) -> float:
        """Calculate overall data quality score."""
        # Completeness score (inverse of null percentage)
        completeness = max(0, 1 - (null_percentage / 100))

        # Uniqueness score (higher distinct ratio is generally better)
        uniqueness = min(1.0, distinct_ratio * 2)  # Cap at 1.0

        # Sample size score (larger samples are more reliable)
        sample_score = min(1.0, sample_size / 1000)  # Cap at 1.0

        # Weighted average
        quality_score = completeness * 0.5 + uniqueness * 0.3 + sample_score * 0.2

        return round(quality_score, 3)

    def _detect_date_formats(self, sample_strings: List[str]) -> List[str]:
        """Detect common date formats in string data."""
        formats = []

        # Common date format patterns
        format_patterns = [
            (r"\d{4}-\d{2}-\d{2}", "%Y-%m-%d"),
            (r"\d{2}/\d{2}/\d{4}", "%m/%d/%Y"),
            (r"\d{2}-\d{2}-\d{4}", "%m-%d-%Y"),
            (r"\d{4}/\d{2}/\d{2}", "%Y/%m/%d"),
        ]

        for pattern, format_str in format_patterns:
            matches = sum(1 for s in sample_strings if re.match(pattern, str(s)))
            if matches > len(sample_strings) * 0.5:  # More than 50% match
                formats.append(format_str)

        return formats

    def _detect_string_patterns(self, data: pd.Series) -> List[str]:
        """Detect common string patterns."""
        patterns = []

        # Common patterns to detect
        pattern_checks = [
            (r"^[A-Z]{2,3}\d{3,6}$", "code_pattern"),
            (r"^\d{3}-\d{2}-\d{4}$", "ssn_pattern"),
            (r"^[A-Z][a-z]+ [A-Z][a-z]+$", "full_name_pattern"),
            (r"^\d+\.\d+$", "decimal_pattern"),
        ]

        for pattern, name in pattern_checks:
            matches = data.astype(str).str.match(pattern).sum()
            if matches > len(data) * 0.3:  # More than 30% match
                patterns.append(name)

        return patterns

    def find_similar_columns(
        self, column_name: str, threshold: float = None
    ) -> List[str]:
        """Find columns similar to the given column using LSH."""
        if not self.enable_lsh or not hasattr(self, "lsh_index"):
            return []

        threshold = threshold or self.lsh_threshold

        try:
            # This would require the column to be already indexed
            similar = self.lsh_index.query(column_name)
            return [col for col in similar if col != column_name]
        except (AttributeError, KeyError, ValueError):
            return []

    # Database-native helper methods
    def _get_top_k_values(self, column) -> List[Dict[str, Any]]:
        """Get top-k most frequent values using native value_counts."""
        try:
            value_counts = column.value_counts().limit(self.top_k).to_pandas()
            total_count = int(column.count().to_pandas())

            result = []
            for _, row in value_counts.iterrows():
                value = row.iloc[0]  # First column is the value
                count = int(row.iloc[1])  # Second column is the count
                percentage = (count / total_count) * 100 if total_count > 0 else 0

                result.append(
                    {
                        "value": str(value) if value is not None else None,
                        "count": count,
                        "percentage": percentage,
                    }
                )

            return result
        except Exception as e:
            self.logger.debug(f"Native value_counts failed: {e}")
            return []

    def _compute_numeric_stats(self, column) -> Optional[NumericStats]:
        """Compute statistics for numeric columns using native methods."""
        try:
            # Check if column is numeric by trying to compute mean
            mean_val = column.mean().to_pandas()

            # If we get here, it's numeric
            min_val = float(column.min().to_pandas())
            max_val = float(column.max().to_pandas())
            mean_val = float(mean_val)
            std_val = float(column.std().to_pandas())

            # For percentiles, we might need to use a different approach
            # Some backends support quantile, others don't
            try:
                # Try to get percentiles if supported
                percentile_25 = float(column.quantile(0.25).to_pandas())
                percentile_75 = float(column.quantile(0.75).to_pandas())
                median = float(column.quantile(0.5).to_pandas())
            except Exception:
                # Fallback: use min/max as rough estimates
                percentile_25 = min_val + (max_val - min_val) * 0.25
                percentile_75 = min_val + (max_val - min_val) * 0.75
                median = (min_val + max_val) / 2

            return NumericStats(
                min_value=min_val,
                max_value=max_val,
                mean=mean_val,
                median=median,
                std_dev=std_val,
                percentile_25=percentile_25,
                percentile_75=percentile_75,
            )
        except Exception:
            return None

    def _compute_date_stats(self, column) -> Optional[DateStats]:
        """Compute statistics for date/datetime columns using native methods."""
        try:
            # Try to get min/max dates
            min_date = column.min().to_pandas()
            max_date = column.max().to_pandas()

            # Convert to datetime if they're not already
            if hasattr(min_date, "to_pydatetime"):
                min_date = min_date.to_pydatetime()
            if hasattr(max_date, "to_pydatetime"):
                max_date = max_date.to_pydatetime()

            # Calculate date range
            if min_date and max_date:
                date_range_days = (max_date - min_date).days
            else:
                date_range_days = None

            # For date formats, we'd need to sample some data
            common_formats = []
            try:
                sample_data = column.limit(100).to_pandas()
                common_formats = self._detect_date_formats(
                    sample_data.astype(str).tolist()
                )
            except Exception:
                pass

            return DateStats(
                min_date=min_date,
                max_date=max_date,
                date_range_days=date_range_days,
                common_date_formats=common_formats,
            )
        except Exception:
            return None

    def _compute_string_stats(self, column) -> Optional[StringStats]:
        """Compute statistics for string columns using native methods."""
        try:
            # Check if it's a string column by trying string operations
            # Get length statistics using native string functions
            length_col = column.length()

            min_length = int(length_col.min().to_pandas())
            max_length = int(length_col.max().to_pandas())
            avg_length = float(length_col.mean().to_pandas())

            # For character type analysis, we need to sample data
            char_types = {}
            patterns = []

            try:
                sample_data = column.limit(1000).to_pandas().dropna()
                if len(sample_data) > 0:
                    # Character type analysis
                    char_types = defaultdict(int)
                    for text in sample_data.head(100):  # Limit for performance
                        text_str = str(text)
                        for char in text_str:
                            if char.isalpha():
                                char_types["alphabetic"] += 1
                            elif char.isdigit():
                                char_types["numeric"] += 1
                            elif char.isspace():
                                char_types["whitespace"] += 1
                            else:
                                char_types["special"] += 1

                    # Pattern detection
                    patterns = self._detect_string_patterns(sample_data.head(100))
            except Exception:
                pass

            return StringStats(
                min_length=min_length,
                max_length=max_length,
                avg_length=avg_length,
                character_types=dict(char_types),
                common_patterns=patterns,
            )
        except Exception:
            return None

    def _infer_semantic_type(self, column, column_name: str) -> Optional[str]:
        """Infer semantic type using native column operations."""
        try:
            # Sample some data for pattern analysis
            sample_data = column.limit(100).to_pandas().dropna()

            if len(sample_data) == 0:
                return None

            # Use the existing semantic type inference
            return self._infer_semantic_type(sample_data, column_name)
        except Exception:
            return "general"

    def _calculate_consistency_from_describe(
        self, describe_result: pd.DataFrame
    ) -> float:
        """Calculate consistency score from Ibis describe() result."""
        try:
            if describe_result.empty:
                return 0.0

            # Use null fractions as a proxy for consistency
            if "null_frac" in describe_result.columns:
                null_fractions = describe_result["null_frac"].fillna(0)
                # Lower null fractions indicate better consistency
                consistency_score = float(1.0 - null_fractions.mean())
                return max(0.0, min(1.0, consistency_score))

            return 0.5  # Default moderate consistency
        except Exception:
            return 0.0
