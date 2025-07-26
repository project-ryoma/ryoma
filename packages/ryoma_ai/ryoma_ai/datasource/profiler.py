"""
Database Profiler Implementation

This module implements comprehensive database profiling capabilities based on the
"Automatic Metadata Extraction for Text-to-SQL" paper, including:

- Row counts & NULL statistics
- Distinct-value ratio per column
- Numeric/date min, max, mean
- String length & character-type stats
- Top-k frequent values
- Locality-sensitive hashing / MinHash sketches for approximate similarity
"""

import hashlib
import re
import statistics
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple
import logging

import pandas as pd
import numpy as np
from datasketch import MinHashLSH, MinHash

from ryoma_ai.datasource.metadata import (
    ColumnProfile, TableProfile, NumericStats, DateStats, StringStats, LSHSketch
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
        enable_lsh: bool = True
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

    def profile_table(self, datasource, table_name: str, schema: Optional[str] = None) -> TableProfile:
        """
        Profile a complete table including all columns.
        
        Args:
            datasource: The SQL datasource to profile
            table_name: Name of the table to profile
            schema: Optional schema name
            
        Returns:
            TableProfile with comprehensive metadata
        """
        start_time = datetime.now()
        
        try:
            # Get table data sample
            query = self._build_sample_query(table_name, schema)
            df = datasource.query(query, result_format="pandas")
            
            if df.empty:
                self.logger.warning(f"Table {table_name} is empty")
                return TableProfile(
                    table_name=table_name,
                    row_count=0,
                    column_count=0,
                    profiled_at=datetime.now(),
                    profiling_duration_seconds=0.0
                )
            
            # Get actual row count
            count_query = f"SELECT COUNT(*) as row_count FROM {self._quote_identifier(table_name, schema)}"
            row_count_result = datasource.query(count_query, result_format="pandas")
            actual_row_count = int(row_count_result.iloc[0]['row_count'])
            
            # Calculate table-level metrics
            completeness_scores = []
            for column in df.columns:
                null_ratio = df[column].isnull().sum() / len(df)
                completeness_scores.append(1.0 - null_ratio)
            
            completeness_score = statistics.mean(completeness_scores) if completeness_scores else 0.0
            
            # Create table profile
            duration = (datetime.now() - start_time).total_seconds()
            
            return TableProfile(
                table_name=table_name,
                row_count=actual_row_count,
                column_count=len(df.columns),
                completeness_score=completeness_score,
                consistency_score=self._calculate_consistency_score(df),
                profiled_at=datetime.now(),
                profiling_duration_seconds=duration
            )
            
        except Exception as e:
            self.logger.error(f"Error profiling table {table_name}: {str(e)}")
            return TableProfile(
                table_name=table_name,
                profiled_at=datetime.now(),
                profiling_duration_seconds=(datetime.now() - start_time).total_seconds()
            )

    def profile_column(
        self, 
        datasource, 
        table_name: str, 
        column_name: str, 
        schema: Optional[str] = None
    ) -> ColumnProfile:
        """
        Profile a single column with comprehensive statistics.
        
        Args:
            datasource: The SQL datasource to profile
            table_name: Name of the table
            column_name: Name of the column to profile
            schema: Optional schema name
            
        Returns:
            ColumnProfile with detailed statistics
        """
        try:
            # Get column data sample
            query = self._build_column_sample_query(table_name, column_name, schema)
            df = datasource.query(query, result_format="pandas")
            
            if df.empty or column_name not in df.columns:
                self.logger.warning(f"Column {column_name} not found or empty")
                return ColumnProfile(column_name=column_name, profiled_at=datetime.now())
            
            column_data = df[column_name]
            
            # Basic statistics
            row_count = len(column_data)
            null_count = column_data.isnull().sum()
            null_percentage = (null_count / row_count) * 100 if row_count > 0 else 0
            
            # Remove nulls for further analysis
            non_null_data = column_data.dropna()
            distinct_count = non_null_data.nunique()
            distinct_ratio = distinct_count / len(non_null_data) if len(non_null_data) > 0 else 0
            
            # Top-k frequent values
            top_k_values = self._get_top_k_values(non_null_data)
            
            # Type-specific statistics
            numeric_stats = self._compute_numeric_stats(non_null_data)
            date_stats = self._compute_date_stats(non_null_data)
            string_stats = self._compute_string_stats(non_null_data)
            
            # LSH sketch for similarity
            lsh_sketch = None
            if self.enable_lsh and len(non_null_data) > 0:
                lsh_sketch = self._compute_lsh_sketch(non_null_data, column_name)
            
            # Semantic type inference
            semantic_type = self._infer_semantic_type(non_null_data, column_name)
            
            # Data quality score
            data_quality_score = self._calculate_data_quality_score(
                null_percentage, distinct_ratio, len(non_null_data)
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
                sample_size=len(column_data)
            )
            
        except Exception as e:
            self.logger.error(f"Error profiling column {column_name}: {str(e)}")
            return ColumnProfile(
                column_name=column_name,
                profiled_at=datetime.now()
            )

    def _build_sample_query(self, table_name: str, schema: Optional[str] = None) -> str:
        """Build a query to sample data from a table."""
        full_table_name = self._quote_identifier(table_name, schema)
        return f"SELECT * FROM {full_table_name} LIMIT {self.sample_size}"

    def _build_column_sample_query(
        self, 
        table_name: str, 
        column_name: str, 
        schema: Optional[str] = None
    ) -> str:
        """Build a query to sample data from a specific column."""
        full_table_name = self._quote_identifier(table_name, schema)
        quoted_column = f'"{column_name}"'
        return f"SELECT {quoted_column} FROM {full_table_name} LIMIT {self.sample_size}"

    def _quote_identifier(self, table_name: str, schema: Optional[str] = None) -> str:
        """Quote database identifiers properly."""
        if schema:
            return f'"{schema}"."{table_name}"'
        return f'"{table_name}"'

    def _get_top_k_values(self, data: pd.Series) -> List[Dict[str, Any]]:
        """Get top-k most frequent values."""
        if len(data) == 0:
            return []
        
        value_counts = data.value_counts().head(self.top_k)
        return [
            {
                "value": str(value),
                "count": int(count),
                "percentage": (count / len(data)) * 100
            }
            for value, count in value_counts.items()
        ]

    def _compute_numeric_stats(self, data: pd.Series) -> Optional[NumericStats]:
        """Compute statistics for numeric columns."""
        try:
            # Try to convert to numeric
            numeric_data = pd.to_numeric(data, errors='coerce').dropna()
            
            if len(numeric_data) == 0:
                return None
            
            return NumericStats(
                min_value=float(numeric_data.min()),
                max_value=float(numeric_data.max()),
                mean=float(numeric_data.mean()),
                median=float(numeric_data.median()),
                std_dev=float(numeric_data.std()),
                percentile_25=float(numeric_data.quantile(0.25)),
                percentile_75=float(numeric_data.quantile(0.75))
            )
        except Exception:
            return None

    def _compute_date_stats(self, data: pd.Series) -> Optional[DateStats]:
        """Compute statistics for date/datetime columns."""
        try:
            # Try to convert to datetime
            date_data = pd.to_datetime(data, errors='coerce', infer_datetime_format=True).dropna()
            
            if len(date_data) == 0:
                return None
            
            min_date = date_data.min()
            max_date = date_data.max()
            date_range = (max_date - min_date).days
            
            # Detect common date formats
            sample_strings = data.astype(str).head(100).tolist()
            common_formats = self._detect_date_formats(sample_strings)
            
            return DateStats(
                min_date=min_date,
                max_date=max_date,
                date_range_days=date_range,
                common_date_formats=common_formats
            )
        except Exception:
            return None

    def _compute_string_stats(self, data: pd.Series) -> Optional[StringStats]:
        """Compute statistics for string columns."""
        try:
            string_data = data.astype(str)
            
            if len(string_data) == 0:
                return None
            
            lengths = string_data.str.len()
            
            # Character type analysis
            char_types = defaultdict(int)
            for text in string_data.head(1000):  # Sample for performance
                for char in text:
                    if char.isalpha():
                        char_types['alphabetic'] += 1
                    elif char.isdigit():
                        char_types['numeric'] += 1
                    elif char.isspace():
                        char_types['whitespace'] += 1
                    else:
                        char_types['special'] += 1
            
            # Common patterns detection
            patterns = self._detect_string_patterns(string_data.head(1000))
            
            return StringStats(
                min_length=int(lengths.min()),
                max_length=int(lengths.max()),
                avg_length=float(lengths.mean()),
                character_types=dict(char_types),
                common_patterns=patterns
            )
        except Exception:
            return None

    def _compute_lsh_sketch(self, data: pd.Series, column_name: str) -> Optional[LSHSketch]:
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
                    minhash.update(shingle.encode('utf-8'))
            
            # Store in LSH index
            if hasattr(self, 'lsh_index'):
                self.lsh_index.insert(column_name, minhash)
            
            return LSHSketch(
                hash_values=list(minhash.hashvalues),
                num_hashes=self.num_hashes,
                jaccard_threshold=self.lsh_threshold
            )
        except Exception:
            return None

    def _create_shingles(self, text: str, k: int = 3) -> List[str]:
        """Create k-shingles from text."""
        if len(text) < k:
            return [text]
        return [text[i:i+k] for i in range(len(text) - k + 1)]

    def _infer_semantic_type(self, data: pd.Series, column_name: str) -> Optional[str]:
        """Infer semantic type of the column."""
        if len(data) == 0:
            return None
        
        sample_data = data.head(100).astype(str)
        
        # Email pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if sample_data.str.match(email_pattern).mean() > 0.8:
            return "email"
        
        # Phone pattern
        phone_pattern = r'^[\+]?[1-9]?[0-9]{7,15}$'
        if sample_data.str.replace(r'[^\d+]', '', regex=True).str.match(phone_pattern).mean() > 0.8:
            return "phone"
        
        # URL pattern
        url_pattern = r'^https?://'
        if sample_data.str.match(url_pattern).mean() > 0.8:
            return "url"
        
        # ID pattern (based on column name and data characteristics)
        if 'id' in column_name.lower() and data.nunique() / len(data) > 0.9:
            return "identifier"
        
        return "general"

    def _calculate_data_quality_score(
        self, 
        null_percentage: float, 
        distinct_ratio: float, 
        sample_size: int
    ) -> float:
        """Calculate overall data quality score."""
        # Completeness score (inverse of null percentage)
        completeness = max(0, 1 - (null_percentage / 100))
        
        # Uniqueness score (higher distinct ratio is generally better)
        uniqueness = min(1.0, distinct_ratio * 2)  # Cap at 1.0
        
        # Sample size score (larger samples are more reliable)
        sample_score = min(1.0, sample_size / 1000)  # Cap at 1.0
        
        # Weighted average
        quality_score = (completeness * 0.5 + uniqueness * 0.3 + sample_score * 0.2)
        
        return round(quality_score, 3)

    def _calculate_consistency_score(self, df: pd.DataFrame) -> float:
        """Calculate data consistency score for the table."""
        if df.empty:
            return 0.0
        
        consistency_scores = []
        
        for column in df.columns:
            # Check for consistent data types within the column
            non_null_data = df[column].dropna()
            if len(non_null_data) == 0:
                continue
            
            # Try to infer consistent type
            try:
                # Check if all values can be converted to the same type
                pd.to_numeric(non_null_data, errors='raise')
                consistency_scores.append(1.0)  # All numeric
            except:
                try:
                    pd.to_datetime(non_null_data, errors='raise')
                    consistency_scores.append(1.0)  # All datetime
                except:
                    # Check string consistency (similar lengths, patterns)
                    if non_null_data.dtype == 'object':
                        lengths = non_null_data.astype(str).str.len()
                        length_cv = lengths.std() / lengths.mean() if lengths.mean() > 0 else 1
                        consistency_scores.append(max(0, 1 - length_cv))
                    else:
                        consistency_scores.append(0.5)  # Mixed types
        
        return statistics.mean(consistency_scores) if consistency_scores else 0.0

    def _detect_date_formats(self, sample_strings: List[str]) -> List[str]:
        """Detect common date formats in string data."""
        formats = []
        
        # Common date format patterns
        format_patterns = [
            (r'\d{4}-\d{2}-\d{2}', '%Y-%m-%d'),
            (r'\d{2}/\d{2}/\d{4}', '%m/%d/%Y'),
            (r'\d{2}-\d{2}-\d{4}', '%m-%d-%Y'),
            (r'\d{4}/\d{2}/\d{2}', '%Y/%m/%d'),
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
            (r'^[A-Z]{2,3}\d{3,6}$', 'code_pattern'),
            (r'^\d{3}-\d{2}-\d{4}$', 'ssn_pattern'),
            (r'^[A-Z][a-z]+ [A-Z][a-z]+$', 'full_name_pattern'),
            (r'^\d+\.\d+$', 'decimal_pattern'),
        ]
        
        for pattern, name in pattern_checks:
            matches = data.astype(str).str.match(pattern).sum()
            if matches > len(data) * 0.3:  # More than 30% match
                patterns.append(name)
        
        return patterns

    def find_similar_columns(self, column_name: str, threshold: float = None) -> List[str]:
        """Find columns similar to the given column using LSH."""
        if not self.enable_lsh or not hasattr(self, 'lsh_index'):
            return []
        
        threshold = threshold or self.lsh_threshold
        
        try:
            # This would require the column to be already indexed
            similar = self.lsh_index.query(column_name)
            return [col for col in similar if col != column_name]
        except:
            return []
