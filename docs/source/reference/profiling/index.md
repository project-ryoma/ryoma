# 📊 Database Profiling

Comprehensive database metadata extraction system based on research from "Automatic Metadata Extraction for Text-to-SQL" paper.

## 🎯 Overview

The Database Profiling system provides:
- **Statistical Analysis** - Row counts, NULL statistics, distinct-value ratios
- **Type-Specific Profiling** - Numeric, date, and string analysis  
- **Semantic Type Inference** - Automatic detection of emails, phones, URLs, etc.
- **Data Quality Scoring** - Multi-dimensional quality assessment
- **LSH Similarity** - Locality-sensitive hashing for column similarity
- **Ibis Integration** - Native database optimizations for better performance

## 🚀 Quick Start

### Enable Profiling
```python
from ryoma_ai.datasource.postgres import PostgresDataSource

# Enable profiling with default settings
datasource = PostgresDataSource(
    connection_string="postgresql://user:pass@localhost:5432/db",
    enable_profiling=True
)

# Profile a table
profile = datasource.profile_table("customers")
print(f"Rows: {profile['table_profile']['row_count']:,}")
print(f"Completeness: {profile['table_profile']['completeness_score']:.2%}")
```

### Custom Configuration
```python
# Advanced profiling configuration
datasource = PostgresDataSource(
    connection_string="postgresql://user:pass@localhost:5432/db",
    enable_profiling=True,
    profiler_config={
        "sample_size": 10000,      # Rows to analyze
        "top_k": 10,               # Top frequent values
        "enable_lsh": True,        # Column similarity
        "lsh_threshold": 0.8,      # Similarity threshold
        "num_hashes": 128          # LSH precision
    }
)
```

## 📋 Core Features

### Table-Level Profiling
```python
# Comprehensive table analysis
profile = datasource.profile_table("customers")

# Access table metrics
table_info = profile["table_profile"]
print(f"Row count: {table_info['row_count']:,}")
print(f"Column count: {table_info['column_count']}")
print(f"Completeness score: {table_info['completeness_score']:.3f}")
print(f"Consistency score: {table_info['consistency_score']:.3f}")
print(f"Profiling method: {profile['profiling_summary']['profiling_method']}")
```

### Column-Level Analysis
```python
# Individual column profiling
column_profile = datasource.profile_column("customers", "email")

# Check semantic type and quality
if column_profile["semantic_type"] == "email":
    quality = column_profile["data_quality_score"]
    null_pct = column_profile["null_percentage"]
    distinct_ratio = column_profile["distinct_ratio"]
    
    print(f"Email column quality: {quality:.3f}")
    print(f"NULL percentage: {null_pct:.1f}%")
    print(f"Distinct ratio: {distinct_ratio:.3f}")
    
    # Show top values
    for i, value_info in enumerate(column_profile["top_k_values"][:3], 1):
        print(f"{i}. {value_info['value']} ({value_info['count']} times)")
```

### Enhanced Catalog
```python
# Get catalog with profiling data
catalog = datasource.get_enhanced_catalog(include_profiles=True)

for schema in catalog.schemas:
    print(f"Schema: {schema.schema_name}")
    for table in schema.tables:
        if table.profile:
            print(f"  Table: {table.table_name} ({table.profile.row_count:,} rows)")
            
            # Find high-quality columns
            high_quality_cols = table.get_high_quality_columns(min_quality_score=0.8)
            print(f"    High-quality columns: {len(high_quality_cols)}")
            
            # Show profiled columns
            profiled_cols = table.get_profiled_columns()
            print(f"    Profiled columns: {len(profiled_cols)}")
```

## 🔍 Profiling Results

### Table Profile Structure
```json
{
  "table_profile": {
    "table_name": "customers",
    "row_count": 150000,
    "column_count": 12,
    "completeness_score": 0.95,
    "consistency_score": 0.88,
    "profiled_at": "2024-01-15T10:30:00Z",
    "profiling_duration_seconds": 2.34
  },
  "profiling_summary": {
    "profiling_method": "ibis_enhanced",
    "total_columns": 12
  }
}
```

### Column Profile Structure
```json
{
  "column_name": "email",
  "semantic_type": "email",
  "data_quality_score": 0.92,
  "row_count": 150000,
  "null_count": 7800,
  "null_percentage": 5.2,
  "distinct_count": 147200,
  "distinct_ratio": 0.98,
  "top_k_values": [
    {"value": "user@example.com", "count": 15, "percentage": 0.01}
  ],
  "string_stats": {
    "min_length": 8,
    "max_length": 64,
    "avg_length": 24.5,
    "character_types": {
      "alphabetic": 15420,
      "numeric": 3240,
      "special": 890
    }
  }
}
```

## 🎯 Advanced Features

### Semantic Type Detection
Automatically detects column semantic types:

```python
# Check detected semantic types
column_profile = datasource.profile_column("users", "phone_number")

semantic_type = column_profile["semantic_type"]
if semantic_type == "phone":
    print("📞 Phone number column detected")
elif semantic_type == "email":
    print("📧 Email column detected")
elif semantic_type == "url":
    print("🌐 URL column detected")
elif semantic_type == "identifier":
    print("🆔 ID column detected")
```

**Supported Types:**
- **📧 Email** - Pattern-based email detection
- **📞 Phone** - Phone number format recognition
- **🌐 URL** - Web URL identification
- **🆔 Identifier** - High-uniqueness ID detection
- **📝 General** - Default text classification

### Data Quality Scoring
Multi-dimensional quality assessment:

```python
# Quality score calculation
def explain_quality_score(profile):
    completeness = 1 - (profile["null_percentage"] / 100)
    uniqueness = min(1.0, profile["distinct_ratio"] * 2)
    reliability = min(1.0, profile["sample_size"] / 1000)
    
    quality_score = (
        completeness * 0.5 +      # 50% weight
        uniqueness * 0.3 +        # 30% weight  
        reliability * 0.2         # 20% weight
    )
    
    print(f"Completeness: {completeness:.3f}")
    print(f"Uniqueness: {uniqueness:.3f}")
    print(f"Reliability: {reliability:.3f}")
    print(f"Overall Quality: {quality_score:.3f}")

column_profile = datasource.profile_column("customers", "customer_id")
explain_quality_score(column_profile)
```

### Column Similarity Analysis
Find similar columns using LSH (Locality-Sensitive Hashing):

```python
# Find similar columns
similar_columns = datasource.find_similar_columns("customer_id", threshold=0.8)
print(f"Columns similar to 'customer_id': {similar_columns}")
# Output: ["user_id", "client_id", "account_id"]

# Use for schema linking
if similar_columns:
    print("Found potential join candidates:")
    for col in similar_columns:
        print(f"  - {col}")
```

## ⚙️ Configuration Options

### Performance Tuning
```python
# Development configuration (fast)
dev_config = {
    "sample_size": 1000,
    "top_k": 5,
    "enable_lsh": False
}

# Production configuration (balanced)
prod_config = {
    "sample_size": 10000,
    "top_k": 10,
    "enable_lsh": True,
    "lsh_threshold": 0.8
}

# High accuracy configuration (thorough)
accuracy_config = {
    "sample_size": 50000,
    "top_k": 20,
    "enable_lsh": True,
    "lsh_threshold": 0.9,
    "num_hashes": 256
}
```

### Backend-Specific Optimizations
```python
# PostgreSQL with advanced features
postgres_ds = PostgresDataSource(
    connection_string="postgresql://localhost:5432/db",
    enable_profiling=True,
    profiler_config={
        "use_pg_stats": True,      # Leverage pg_stats views
        "use_histograms": True,    # Use histogram data
        "sample_size": 10000
    }
)

# BigQuery with ML functions
bigquery_ds = BigQueryDataSource(
    project_id="my-project",
    enable_profiling=True,
    profiler_config={
        "use_ml_functions": True,  # Use ML.FEATURE_INFO
        "sample_size": 20000
    }
)
```

## 🔧 Direct Profiler Usage

### Standalone Profiler
```python
from ryoma_ai.datasource.profiler import DatabaseProfiler

# Create profiler instance
profiler = DatabaseProfiler(
    sample_size=10000,
    top_k=10,
    enable_lsh=True
)

# Profile table directly
table_profile = profiler.profile_table(datasource, "customers")
print(f"Profiled {table_profile.table_name} in {table_profile.profiling_duration_seconds:.2f}s")

# Profile individual column
column_profile = profiler.profile_column(datasource, "customers", "email")
print(f"Email quality score: {column_profile.data_quality_score:.3f}")
```

### Batch Profiling
```python
# Profile multiple tables
tables_to_profile = ["customers", "orders", "products"]
profiles = {}

for table_name in tables_to_profile:
    print(f"Profiling {table_name}...")
    profile = datasource.profile_table(table_name)
    profiles[table_name] = profile
    
    # Show summary
    table_info = profile["table_profile"]
    print(f"  Rows: {table_info['row_count']:,}")
    print(f"  Completeness: {table_info['completeness_score']:.2%}")
```

## 📊 Integration with SQL Agent

### Enhanced Query Generation
```python
from ryoma_ai.agent.sql import SqlAgent

# Create agent with profiled datasource
agent = SqlAgent(model="gpt-4", mode="enhanced")
agent.add_datasource(datasource)  # Profiling data automatically used

# Profiling improves query generation
response = agent.stream("""
Find high-value customers who haven't purchased recently.
Focus on customers with good data quality.
""")

# Agent uses profiling data for:
# - Better table selection (row counts, completeness)
# - Smarter column selection (quality scores, semantic types)
# - Optimized joins (similarity analysis)
# - Appropriate filtering (NULL percentages)
```

## 🛡️ Production Considerations

### Performance Monitoring
```python
# Monitor profiling performance
profile = datasource.profile_table("large_table")
duration = profile["table_profile"]["profiling_duration_seconds"]

if duration > 10:
    print("⚠️ Profiling took too long, consider:")
    print("  - Reducing sample_size")
    print("  - Disabling LSH (enable_lsh=False)")
    print("  - Using cached profiles")
```

### Caching Profiles
```python
# Cache profiles for reuse
import json
from datetime import datetime, timedelta

def cache_profile(table_name, profile):
    cache_data = {
        "profile": profile,
        "cached_at": datetime.now().isoformat()
    }
    with open(f"profiles/{table_name}.json", "w") as f:
        json.dump(cache_data, f)

def load_cached_profile(table_name, max_age_hours=24):
    try:
        with open(f"profiles/{table_name}.json", "r") as f:
            cache_data = json.load(f)
        
        cached_at = datetime.fromisoformat(cache_data["cached_at"])
        if datetime.now() - cached_at < timedelta(hours=max_age_hours):
            return cache_data["profile"]
    except FileNotFoundError:
        pass
    return None

# Use cached profile if available
cached = load_cached_profile("customers")
if cached:
    profile = cached
else:
    profile = datasource.profile_table("customers")
    cache_profile("customers", profile)
```

## 🎯 Best Practices

### 1. **Configure Appropriately**
- Use smaller samples for development
- Enable LSH for large schemas
- Adjust thresholds based on your data

### 2. **Monitor Performance**
- Track profiling duration
- Cache profiles for frequently used tables
- Use appropriate sample sizes

### 3. **Leverage Results**
- Use quality scores for column selection
- Apply semantic types for better formatting
- Utilize similarity for schema linking

### 4. **Production Deployment**
- Schedule regular profile updates
- Monitor profiling overhead
- Set up alerts for failures

## 🔗 Related Documentation

- **[Enhanced SQL Agent](../agent/sql.md)** - Uses profiling for better queries
- **[Data Sources](../data-sources/index.md)** - Database connectors with profiling
- **[Architecture Guide](../../architecture/database-profiling.md)** - Technical details
