# Database Profiling System

## Overview

The Database Profiling System implements comprehensive metadata extraction capabilities based on the "Automatic Metadata Extraction for Text-to-SQL" paper. It provides deep insights into database structure, data quality, and statistical characteristics that are essential for effective Text-to-SQL generation.

## Research Foundation

This implementation is based on the database profiling techniques described in the research paper, which identified these key profiling components as crucial for effective schema linking and query generation:

### Core Profiling Features

1. **Row counts & NULL statistics** - Basic data completeness metrics
2. **Distinct-value ratio per column** - Cardinality and uniqueness analysis
3. **Numeric/date min, max, mean** - Statistical distribution analysis
4. **String length & character-type stats** - Text pattern analysis
5. **Top-k frequent values** - Most common data patterns
6. **Locality-sensitive hashing / MinHash sketches** - Approximate similarity matching

## Architecture

### Core Components

#### DatabaseProfiler
The main profiling engine that extracts comprehensive metadata from database tables.

**Key Features:**
- Configurable sampling for large datasets
- Type-specific statistical analysis
- LSH-based similarity indexing
- Semantic type inference
- Data quality scoring

#### Enhanced Metadata Models
Extended metadata structures that store profiling information:

- **ColumnProfile** - Comprehensive column statistics
- **TableProfile** - Table-level metadata and quality metrics
- **NumericStats** - Statistical measures for numeric data
- **DateStats** - Temporal data analysis
- **StringStats** - Text pattern and character analysis
- **LSHSketch** - Similarity matching capabilities

#### SqlDataSource Integration
Seamless integration with existing SQL datasources:

- **profile_table()** - Complete table profiling
- **profile_column()** - Individual column analysis
- **get_enhanced_catalog()** - Schema with profiling data
- **find_similar_columns()** - LSH-based similarity search

## Profiling Capabilities

### Table-Level Profiling

```python
# Basic table profiling
table_profile = datasource.profile_table("customers")

# Results include:
{
    "table_profile": {
        "row_count": 150000,
        "column_count": 12,
        "completeness_score": 0.95,
        "consistency_score": 0.88,
        "profiled_at": "2024-01-15T10:30:00Z"
    },
    "column_profiles": { ... },
    "profiling_summary": { ... }
}
```

### Column-Level Profiling

#### Numeric Columns
```python
# Numeric statistics
{
    "numeric_stats": {
        "min_value": 0.0,
        "max_value": 999999.99,
        "mean": 45678.23,
        "median": 32100.50,
        "std_dev": 28934.12,
        "percentile_25": 15000.00,
        "percentile_75": 67500.00
    }
}
```

#### String Columns
```python
# String analysis
{
    "string_stats": {
        "min_length": 5,
        "max_length": 255,
        "avg_length": 28.5,
        "character_types": {
            "alphabetic": 15420,
            "numeric": 3240,
            "special": 890,
            "whitespace": 1250
        },
        "common_patterns": ["email_pattern", "phone_pattern"]
    }
}
```

#### Date/DateTime Columns
```python
# Temporal analysis
{
    "date_stats": {
        "min_date": "2020-01-01T00:00:00Z",
        "max_date": "2024-01-15T23:59:59Z",
        "date_range_days": 1475,
        "common_date_formats": ["%Y-%m-%d", "%m/%d/%Y"]
    }
}
```

### Advanced Features

#### Semantic Type Inference
Automatically detects column semantic types:
- **Email addresses** - Pattern-based detection
- **Phone numbers** - Format recognition
- **URLs** - Protocol identification
- **Identifiers** - High uniqueness detection
- **General text** - Default classification

#### Data Quality Scoring
Multi-dimensional quality assessment:
- **Completeness** - Based on NULL percentage
- **Uniqueness** - Distinct value ratio analysis
- **Consistency** - Type and pattern consistency
- **Sample reliability** - Based on sample size

#### LSH-Based Similarity
Locality-Sensitive Hashing for approximate similarity:
- **MinHash sketches** - Efficient similarity computation
- **Configurable thresholds** - Adjustable similarity sensitivity
- **Column similarity search** - Find related columns across tables

## Configuration Options

### Basic Configuration
```python
datasource = PostgresDataSource(
    connection_string="postgresql://...",
    enable_profiling=True,
    profiler_config={
        "sample_size": 10000,
        "top_k": 10,
        "lsh_threshold": 0.8,
        "num_hashes": 128,
        "enable_lsh": True
    }
)
```

### Performance Tuning

#### Large Database Configuration
```python
large_db_config = {
    "sample_size": 50000,    # Larger sample for accuracy
    "top_k": 20,             # More frequent values
    "lsh_threshold": 0.9,    # Higher precision
    "num_hashes": 256,       # Better similarity detection
    "enable_lsh": True
}
```

#### Fast Profiling Configuration
```python
fast_config = {
    "sample_size": 1000,     # Smaller sample for speed
    "top_k": 5,              # Fewer values
    "lsh_threshold": 0.7,    # Lower precision
    "num_hashes": 64,        # Faster computation
    "enable_lsh": False      # Disable for speed
}
```

## Usage Examples

### Comprehensive Table Analysis
```python
from ryoma_ai.datasource.postgres import PostgresDataSource

# Initialize with profiling
datasource = PostgresDataSource(
    connection_string="postgresql://user:pass@host:5432/db",
    enable_profiling=True
)

# Profile entire table
profile = datasource.profile_table("customers")

# Access table-level metrics
table_info = profile["table_profile"]
print(f"Rows: {table_info['row_count']}")
print(f"Completeness: {table_info['completeness_score']:.2f}")

# Access column-level details
for col_name, col_profile in profile["column_profiles"].items():
    print(f"{col_name}: {col_profile['semantic_type']}")
    print(f"  Quality: {col_profile['data_quality_score']:.2f}")
    print(f"  NULL%: {col_profile['null_percentage']:.1f}%")
```

### Individual Column Analysis
```python
# Profile specific column
column_profile = datasource.profile_column("customers", "email")

# Check semantic type
if column_profile["semantic_type"] == "email":
    print("✅ Email column detected")

# Analyze data quality
quality = column_profile["data_quality_score"]
if quality > 0.8:
    print("✅ High quality data")
else:
    print("⚠️ Data quality issues detected")
```

### Enhanced Catalog with Profiling
```python
# Get catalog with profiling data
catalog = datasource.get_enhanced_catalog(include_profiles=True)

# Access enhanced information
for schema in catalog.schemas:
    for table in schema.tables:
        if table.profile:
            print(f"Table {table.table_name}: {table.profile.row_count} rows")
        
        # Find high-quality columns
        high_quality_cols = table.get_high_quality_columns(min_quality_score=0.8)
        print(f"High quality columns: {len(high_quality_cols)}")
```

### Similarity Analysis
```python
# Find similar columns
similar_cols = datasource.find_similar_columns("customer_id", threshold=0.8)
print(f"Similar to customer_id: {similar_cols}")

# Use for schema linking
if similar_cols:
    print("Found potential join candidates")
```

## Integration with Enhanced SQL Agent

### Schema Linking Enhancement
The profiling data significantly improves schema linking:

1. **Table Selection** - Uses row counts and completeness scores
2. **Column Relevance** - Leverages semantic types and quality scores
3. **Join Detection** - Uses similarity analysis for relationship discovery
4. **Data Distribution** - Informs query optimization decisions

### Query Generation Improvements
Profiling data enhances query generation:

1. **WHERE Clause Generation** - Uses top-k values for better literals
2. **GROUP BY Selection** - Leverages distinct ratios for grouping columns
3. **Aggregation Functions** - Uses numeric statistics for appropriate functions
4. **Data Type Handling** - Uses semantic types for proper formatting

### Error Prevention
Quality scores help prevent common errors:

1. **NULL Handling** - Warns about high NULL percentage columns
2. **Data Type Mismatches** - Uses inferred semantic types
3. **Cardinality Issues** - Uses distinct ratios for optimization
4. **Performance Problems** - Uses statistical data for query planning

## Performance Considerations

### Sampling Strategy
- **Adaptive Sampling** - Adjusts sample size based on table size
- **Stratified Sampling** - Ensures representative data distribution
- **Incremental Profiling** - Updates profiles incrementally

### Caching and Storage
- **Profile Caching** - Stores computed profiles for reuse
- **Incremental Updates** - Updates only changed data
- **Compression** - Efficient storage of profiling data

### Scalability
- **Parallel Processing** - Profiles multiple columns simultaneously
- **Resource Management** - Configurable memory and CPU usage
- **Batch Processing** - Handles large datasets efficiently

## Best Practices

### Production Deployment
1. **Configure Appropriate Sampling** - Balance accuracy vs. performance
2. **Monitor Resource Usage** - Track profiling overhead
3. **Schedule Regular Updates** - Keep profiles current
4. **Quality Thresholds** - Set appropriate quality score thresholds

### Data Privacy
1. **Sample Data Handling** - Secure handling of sampled data
2. **Sensitive Data Detection** - Identify and protect PII
3. **Access Control** - Restrict profiling permissions
4. **Audit Logging** - Track profiling activities

### Integration Guidelines
1. **Gradual Rollout** - Start with non-critical tables
2. **Performance Testing** - Measure impact on database performance
3. **Fallback Mechanisms** - Handle profiling failures gracefully
4. **Monitoring and Alerting** - Track profiling success rates

## Troubleshooting

### Common Issues
1. **Memory Usage** - Reduce sample size or disable LSH
2. **Performance Impact** - Adjust profiling frequency
3. **Data Type Errors** - Handle mixed-type columns
4. **Permission Issues** - Ensure appropriate database permissions

### Debug Mode
```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Profile with error handling
try:
    profile = datasource.profile_table("problematic_table")
except Exception as e:
    print(f"Profiling failed: {e}")
```

## Future Enhancements

### Planned Features
1. **Advanced Pattern Detection** - ML-based pattern recognition
2. **Cross-Table Analysis** - Relationship discovery across tables
3. **Temporal Profiling** - Track data changes over time
4. **Custom Semantic Types** - User-defined semantic type detection
5. **Distributed Profiling** - Support for distributed databases

### Research Integration
Continuous integration of latest research:
- Advanced statistical methods
- Improved similarity algorithms
- Better semantic type inference
- Enhanced data quality metrics

## References

1. "Automatic Metadata Extraction for Text-to-SQL" (arXiv:2505.19988)
2. MinHash and LSH algorithms for similarity detection
3. Statistical methods for data profiling
4. Data quality assessment frameworks
