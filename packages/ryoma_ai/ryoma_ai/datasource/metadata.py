from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field


class NumericStats(BaseModel):
    """Statistical information for numeric columns."""
    min_value: Optional[float] = Field(None, description="Minimum value")
    max_value: Optional[float] = Field(None, description="Maximum value")
    mean: Optional[float] = Field(None, description="Mean/average value")
    median: Optional[float] = Field(None, description="Median value")
    std_dev: Optional[float] = Field(None, description="Standard deviation")
    percentile_25: Optional[float] = Field(None, description="25th percentile")
    percentile_75: Optional[float] = Field(None, description="75th percentile")


class DateStats(BaseModel):
    """Statistical information for date/datetime columns."""
    min_date: Optional[datetime] = Field(None, description="Earliest date")
    max_date: Optional[datetime] = Field(None, description="Latest date")
    date_range_days: Optional[int] = Field(None, description="Range in days")
    common_date_formats: Optional[List[str]] = Field(None, description="Common date formats found")


class StringStats(BaseModel):
    """Statistical information for string columns."""
    min_length: Optional[int] = Field(None, description="Minimum string length")
    max_length: Optional[int] = Field(None, description="Maximum string length")
    avg_length: Optional[float] = Field(None, description="Average string length")
    character_types: Optional[Dict[str, int]] = Field(None, description="Character type distribution")
    common_patterns: Optional[List[str]] = Field(None, description="Common regex patterns")
    encoding_info: Optional[str] = Field(None, description="Character encoding information")


class LSHSketch(BaseModel):
    """Locality-Sensitive Hashing sketch for approximate similarity."""
    hash_values: List[int] = Field(..., description="MinHash signature values")
    num_hashes: int = Field(..., description="Number of hash functions used")
    jaccard_threshold: float = Field(0.8, description="Jaccard similarity threshold")

    def similarity(self, other: 'LSHSketch') -> float:
        """Calculate Jaccard similarity with another LSH sketch."""
        if self.num_hashes != other.num_hashes:
            raise ValueError("Cannot compare sketches with different hash counts")

        matches = sum(1 for a, b in zip(self.hash_values, other.hash_values) if a == b)
        return matches / self.num_hashes


class ColumnProfile(BaseModel):
    """Comprehensive profiling information for a database column."""
    column_name: str = Field(..., description="Name of the column")

    # Basic statistics
    row_count: Optional[int] = Field(None, description="Total number of rows")
    null_count: Optional[int] = Field(None, description="Number of NULL values")
    null_percentage: Optional[float] = Field(None, description="Percentage of NULL values")
    distinct_count: Optional[int] = Field(None, description="Number of distinct values")
    distinct_ratio: Optional[float] = Field(None, description="Distinct values / total rows ratio")

    # Top-k frequent values
    top_k_values: Optional[List[Dict[str, Any]]] = Field(
        None, description="Top-k most frequent values with counts"
    )

    # Type-specific statistics
    numeric_stats: Optional[NumericStats] = Field(None, description="Statistics for numeric columns")
    date_stats: Optional[DateStats] = Field(None, description="Statistics for date columns")
    string_stats: Optional[StringStats] = Field(None, description="Statistics for string columns")

    # Similarity and indexing
    lsh_sketch: Optional[LSHSketch] = Field(None, description="LSH sketch for similarity matching")

    # Semantic information
    semantic_type: Optional[str] = Field(None, description="Inferred semantic type (email, phone, etc.)")
    data_quality_score: Optional[float] = Field(None, description="Data quality score (0-1)")

    # Profiling metadata
    profiled_at: Optional[datetime] = Field(None, description="When this profile was created")
    sample_size: Optional[int] = Field(None, description="Number of rows sampled for profiling")


class Column(BaseModel):
    name: str = Field(..., description="Name of the column")
    type: Optional[str] = Field(
        None, description="Type of the column", alias="column_type"
    )
    nullable: Optional[bool] = Field(
        None, description="Whether the column is nullable", alias="nullable"
    )
    primary_key: Optional[bool] = Field(
        None, description="Whether the column is a primary key"
    )

    # Enhanced profiling information
    profile: Optional[ColumnProfile] = Field(
        None, description="Comprehensive profiling information for this column"
    )

    class Config:
        populate_by_name = True

    def get_profile_summary(self) -> str:
        """Get a human-readable summary of the column profile."""
        if not self.profile:
            return f"{self.name} ({self.type}): No profile available"

        summary = f"{self.name} ({self.type}):"

        if self.profile.null_percentage is not None:
            summary += f" {self.profile.null_percentage:.1f}% NULL"

        if self.profile.distinct_ratio is not None:
            summary += f", {self.profile.distinct_ratio:.2f} distinct ratio"

        if self.profile.top_k_values:
            top_val = self.profile.top_k_values[0]
            summary += f", most common: {top_val.get('value', 'N/A')}"

        return summary


class TableProfile(BaseModel):
    """Comprehensive profiling information for a database table."""
    table_name: str = Field(..., description="Name of the table")

    # Basic table statistics
    row_count: Optional[int] = Field(None, description="Total number of rows")
    column_count: Optional[int] = Field(None, description="Total number of columns")
    table_size_bytes: Optional[int] = Field(None, description="Table size in bytes")

    # Data quality metrics
    completeness_score: Optional[float] = Field(None, description="Overall data completeness (0-1)")
    consistency_score: Optional[float] = Field(None, description="Data consistency score (0-1)")

    # Relationship information
    foreign_keys: Optional[List[Dict[str, str]]] = Field(None, description="Foreign key relationships")
    referenced_by: Optional[List[str]] = Field(None, description="Tables that reference this table")

    # Usage patterns
    query_frequency: Optional[int] = Field(None, description="How often this table is queried")
    last_updated: Optional[datetime] = Field(None, description="When the table was last updated")

    # Profiling metadata
    profiled_at: Optional[datetime] = Field(None, description="When this profile was created")
    profiling_duration_seconds: Optional[float] = Field(None, description="Time taken to profile")


class Table(BaseModel):
    table_name: str = Field(..., description="Name of the table")
    columns: List[Column] = Field(..., description="List of columns in the table")

    # Enhanced profiling information
    profile: Optional[TableProfile] = Field(
        None, description="Comprehensive profiling information for this table"
    )

    class Config:
        populate_by_name = True

    def get_column(self, column_name: str) -> Optional[Column]:
        """
        Get a column by its name from the table.

        Args:
              column_name: The name of the column to retrieve.

        Returns:
              Column object if found, otherwise None.
        """
        for column in self.columns:
            if column.name == column_name:
                return column
        return None

    def get_profiled_columns(self) -> List[Column]:
        """Get all columns that have profiling information."""
        return [col for col in self.columns if col.profile is not None]

    def get_high_quality_columns(self, min_quality_score: float = 0.8) -> List[Column]:
        """Get columns with high data quality scores."""
        return [
            col for col in self.columns
            if col.profile and col.profile.data_quality_score and
            col.profile.data_quality_score >= min_quality_score
        ]


class Schema(BaseModel):
    schema_name: str = Field(..., description="Name of the schema")
    tables: Optional[List[Table]] = Field(
        None, description="List of tables in the schema"
    )

    class Config:
        populate_by_name = True

    def get_table(self, table_name: str) -> Optional[Table]:
        """
        Get a table by its name from the schema.

        Args:
            table_name: The name of the table to retrieve.

        Returns:
            Table object if found, otherwise None.
        """
        for table in self.tables or []:
            if table.table_name == table_name:
                return table
        return None


class Catalog(BaseModel):
    catalog_name: str = Field(
        ..., description="Name of the catalog, also known as the database name"
    )
    schemas: Optional[List[Schema]] = Field(
        None, description="List of catalog schemas in the catalog"
    )

    class Config:
        populate_by_name = True

    def get_schema(self, schema_name: str) -> Optional[Schema]:
        """
        Get a schema by its name from the catalog.

        Args:
            schema_name: The name of the schema to retrieve.

        Returns:
            Schema object if found, otherwise None.
        """
        for schema in self.schemas or []:
            if schema.schema_name == schema_name:
                return schema
        return None

    @property
    def prompt(self):
        """
        Generate a prompt for the catalog.

        Returns:
            str: A prompt string summarizing the catalog.
        """
        prompt = f"Catalog: {self.catalog_name}\n"
        for schema in self.schemas or []:
            prompt += f"  Schema: {schema.schema_name}\n"
            for table in schema.tables or []:
                prompt += f"    Table: {table.table_name}\n"
                for column in table.columns:
                    prompt += f"      Column: {column.name} ({column.type})\n"
        return prompt
