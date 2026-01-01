# 📊 Database Profiling

Comprehensive database metadata extraction system based on research from "Automatic Metadata Extraction for Text-to-SQL" paper.

## 🎯 Overview

The Database Profiling system provides comprehensive metadata extraction with two profiling modes:

### 📊 **Statistical Profiling** (Base Layer)
- **Row counts & NULL statistics** - Data completeness analysis
- **Type-specific profiling** - Numeric, date, and string analysis
- **Semantic type inference** - Automatic detection of emails, phones, URLs, etc.
- **Data quality scoring** - Multi-dimensional quality assessment
- **LSH similarity** - Locality-sensitive hashing for column similarity
- **Database-native operations** - Optimal performance with universal compatibility

### 🤖 **LLM-Enhanced Profiling** (Advanced Layer)
- **Business purpose analysis** - LLM-generated field descriptions and context
- **SQL generation hints** - Task-aligned metadata for better query generation
- **Join candidate scoring** - Intelligent relationship discovery
- **Usage pattern analysis** - Common query patterns and optimization suggestions
- **Domain classification** - Business domain and data freshness assessment

## 🚀 Quick Start

### Database Profiling
```python
from ryoma_data import DataSource, DatabaseProfiler

# Create datasource
datasource = DataSource(
    "postgres",
    connection_string="postgresql://user:pass@localhost:5432/db"
)

# Create profiler
profiler = DatabaseProfiler()

# Profile a table
profile = profiler.profile_table(datasource, "customers")
print(f"Rows: {profile['table_profile']['row_count']:,}")
print(f"Completeness: {profile['table_profile']['completeness_score']:.2%}")
```

### LLM-Enhanced Profiling
```python
from ryoma_ai.agent.internals.enhanced_profiler import EnhancedDatabaseProfiler
from ryoma_ai.llm.provider import load_model_provider

# Create enhanced profiler with LLM analysis
model = load_model_provider(
    model_id="gpt-4",
    model_type="chat"
)
enhanced_profiler = EnhancedDatabaseProfiler(
    datasource=datasource,
    model=model,
    enable_llm_analysis=True
)

# Get enhanced table metadata
enhanced_metadata = enhanced_profiler.profile_table_enhanced("customers")
print(f"Table purpose: {enhanced_metadata.primary_purpose}")
print(f"Business domain: {enhanced_metadata.business_domain}")

# Get enhanced field metadata
field_metadata = enhanced_profiler.profile_field_enhanced("customers", "email")
print(f"Field description: {field_metadata.llm_description}")
print(f"Business purpose: {field_metadata.business_purpose}")
print(f"SQL hints: {field_metadata.sql_generation_hints}")
```

### Custom Configuration
```python
from ryoma_data import DataSource, DatabaseProfiler

# Create datasource
datasource = DataSource(
    "postgres",
    connection_string="postgresql://user:pass@localhost:5432/db"
)

# Configure profiler
profiler = DatabaseProfiler(
    sample_size=10000,
    top_k=10,
    enable_lsh=True
)

# Enhanced profiler with LLM
enhanced_profiler = EnhancedDatabaseProfiler(
    datasource=datasource,
    model=model,
    enable_llm_analysis=True,
    analysis_sample_size=100
)
```

## 🤖 LLM-Enhanced Profiling

### Enhanced Field Metadata
The `EnhancedDatabaseProfiler` provides AI-powered metadata generation:

```python
from ryoma_ai.agent.internals.enhanced_profiler import EnhancedDatabaseProfiler

# Create enhanced profiler
enhanced_profiler = EnhancedDatabaseProfiler(
    datasource=datasource,
    model=model,
    enable_llm_analysis=True
)

# Get enhanced field analysis
field_metadata = enhanced_profiler.profile_field_enhanced("orders", "customer_id")

# Access enhanced information
print(f"Description: {field_metadata.llm_description}")
print(f"Business purpose: {field_metadata.business_purpose}")
print(f"SQL hints: {field_metadata.sql_generation_hints}")
print(f"Join score: {field_metadata.join_candidate_score}")
print(f"Semantic tags: {field_metadata.semantic_tags}")
print(f"Usage patterns: {field_metadata.usage_patterns}")
```

### Enhanced Table Metadata
```python
# Get comprehensive table analysis
table_metadata = enhanced_profiler.profile_table_enhanced("customers")

# Access table-level insights
print(f"Table description: {table_metadata.table_description}")
print(f"Primary purpose: {table_metadata.primary_purpose}")
print(f"Business domain: {table_metadata.business_domain}")
print(f"Data freshness: {table_metadata.data_freshness_assessment}")

# Access join patterns
for pattern in table_metadata.common_join_patterns:
    print(f"Join pattern: {pattern}")

# Access all field metadata
for field_name, field_meta in table_metadata.field_metadata.items():
    print(f"{field_name}: {field_meta.business_purpose}")
```

### SQL Generation Context
Get optimized metadata for SQL generation tasks:

```python
# Get context optimized for SQL generation
sql_context = enhanced_profiler.get_sql_generation_context("customers")

# This provides metadata in a format optimized for text-to-SQL models
print(f"Table context: {sql_context['table_context']}")
print(f"Field contexts: {sql_context['field_contexts']}")
print(f"Join suggestions: {sql_context['join_suggestions']}")
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

### Basic Table Profile Structure
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

### Enhanced Table Metadata Structure
```json
{
  "base_profile": {
    "table_name": "customers",
    "row_count": 150000,
    "column_count": 12
  },
  "table_description": "Customer information table containing contact details and account data",
  "primary_purpose": "Store customer profiles and contact information for CRM operations",
  "business_domain": "Customer Relationship Management",
  "data_freshness_assessment": "Updated daily via ETL pipeline",
  "common_join_patterns": [
    {
      "target_table": "orders",
      "join_column": "customer_id",
      "join_type": "one_to_many",
      "confidence": 0.95
    }
  ],
  "field_metadata": {
    "customer_id": {
      "llm_description": "Unique identifier for customer records",
      "business_purpose": "Primary key for customer identification",
      "sql_generation_hints": ["Use for JOINs", "Always include in GROUP BY"],
      "join_candidate_score": 0.98
    }
  }
}
```

### Enhanced Field Metadata Structure
```json
{
  "base_profile": {
    "column_name": "email",
    "semantic_type": "email",
    "data_quality_score": 0.92,
    "null_percentage": 5.2,
    "distinct_ratio": 0.98
  },
  "llm_description": "Customer email addresses for communication and account identification",
  "business_purpose": "Primary contact method for customer communications and login",
  "sql_generation_hints": [
    "Use for customer identification",
    "Good for filtering active customers",
    "Consider NULL handling in queries"
  ],
  "join_candidate_score": 0.85,
  "semantic_tags": ["contact_info", "identifier", "communication"],
  "data_quality_assessment": "High quality with 95% completeness and valid email format",
  "usage_patterns": [
    "Frequently used in WHERE clauses",
    "Common in customer lookup queries",
    "Often joined with user_accounts table"
  ]
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
# Development configuration (fast Ibis profiling)
dev_config = {
    "sample_size": 1000,    # For LSH only (Ibis handles all stats natively)
    "top_k": 5,             # Ibis value_counts limit
    "enable_lsh": False,    # Skip similarity analysis
    "enable_llm_enhancement": False
}

# Production configuration (optimized Ibis + LLM)
prod_config = {
    "sample_size": 10000,   # LSH sample size (Ibis stats are full table)
    "top_k": 10,            # Ibis value_counts limit
    "enable_lsh": True,     # Column similarity via LSH
    "lsh_threshold": 0.8,
    "enable_llm_enhancement": True,
    "analysis_sample_size": 50
}

# High accuracy configuration (full Ibis + comprehensive LLM)
accuracy_config = {
    "sample_size": 50000,   # Large LSH sample (Ibis always uses full data)
    "top_k": 20,            # More frequent values via Ibis
    "enable_lsh": True,
    "lsh_threshold": 0.9,
    "num_hashes": 256,
    "enable_llm_enhancement": True,
    "analysis_sample_size": 200
}

# LLM-focused configuration (efficient Ibis + deep business analysis)
llm_focused_config = {
    "sample_size": 5000,    # Minimal LSH (Ibis stats are always complete)
    "enable_llm_enhancement": True,
    "analysis_sample_size": 500,  # Large LLM analysis sample
    "enable_business_context": True,
    "enable_join_analysis": True
}
```

### Backend-Specific Examples
```python
from ryoma_data import DataSource, DatabaseProfiler

# PostgreSQL profiling
postgres_ds = DataSource("postgres", connection_string="postgresql://localhost:5432/db")
profiler = DatabaseProfiler(sample_size=10000)
profile = profiler.profile_table(postgres_ds, "customers")

# BigQuery profiling
bigquery_ds = DataSource(
    "bigquery",
    project_id="my-project"
)
profile = profiler.profile_table(bigquery_ds, "events")
```

## 🔧 Direct Profiler Usage

### Optimized Ibis Profiler
```python
from ryoma_data.profiler import DatabaseProfiler

# Create optimized profiler instance (always uses Ibis)
profiler = DatabaseProfiler(
    sample_size=10000,  # Used for LSH analysis only
    top_k=10,           # Ibis value_counts limit
    enable_lsh=True,    # Column similarity matching
    enable_llm_enhancement=False  # Statistical only
)

# Profile table directly - uses Ibis native methods
table_profile = profiler.profile_table(datasource, "customers")
print(f"Profiled {table_profile.table_name} in {table_profile.profiling_duration_seconds:.2f}s")

# Profile individual column - uses Ibis statistical functions
column_profile = profiler.profile_column(datasource, "customers", "email")
print(f"Email quality score: {column_profile.data_quality_score:.3f}")
```

### Enhanced Profiler with LLM Analysis
```python
from ryoma_ai.agent.internals.enhanced_profiler import EnhancedDatabaseProfiler
from ryoma_ai.llm.provider import load_model_provider

# Create enhanced profiler with LLM capabilities
model = load_model_provider(
    model_id="gpt-4",
    model_type="chat"
)
enhanced_profiler = EnhancedDatabaseProfiler(
    datasource=datasource,
    model=model,
    enable_llm_analysis=True,
    analysis_sample_size=100
)

# Profile table with LLM enhancement
enhanced_table = enhanced_profiler.profile_table_enhanced("customers")
print(f"Table purpose: {enhanced_table.primary_purpose}")
print(f"Business domain: {enhanced_table.business_domain}")

# Profile field with LLM enhancement
enhanced_field = enhanced_profiler.profile_field_enhanced("customers", "email")
print(f"Field description: {enhanced_field.llm_description}")
print(f"SQL hints: {enhanced_field.sql_generation_hints}")
```

### Hybrid Approach (Ibis + LLM)
```python
# Combine optimized Ibis profiling with LLM enhancement
base_profiler = DatabaseProfiler(sample_size=10000, enable_lsh=True)  # Always uses Ibis
enhanced_profiler = EnhancedDatabaseProfiler(
    datasource=datasource,
    model=model,
    base_profiler=base_profiler,  # Reuse optimized Ibis profiler
    enable_llm_analysis=True
)

# Get both Ibis statistical data and LLM-enhanced metadata
enhanced_metadata = enhanced_profiler.profile_table_enhanced("customers")

# Access Ibis-generated statistical data
base_stats = enhanced_metadata.base_profile
print(f"Row count: {base_stats.row_count:,}")  # From Ibis COUNT()
print(f"Completeness: {base_stats.completeness_score:.2%}")  # From Ibis NULL analysis

# Access LLM-enhanced insights
print(f"Business purpose: {enhanced_metadata.primary_purpose}")
print(f"Data freshness: {enhanced_metadata.data_freshness_assessment}")
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

## 🤖 LLM-Enhanced Features

### Business Purpose Analysis
The enhanced profiler uses LLM analysis to understand the business context of your data:

```python
# Get business context for a field
field_metadata = enhanced_profiler.profile_field_enhanced("orders", "total_amount")

print(f"Business purpose: {field_metadata.business_purpose}")
# Output: "Monetary value of customer orders for revenue tracking and financial reporting"

print(f"Usage patterns: {field_metadata.usage_patterns}")
# Output: ["Used in revenue calculations", "Filtered for large orders", "Aggregated for reporting"]
```

### SQL Generation Optimization
Enhanced metadata provides specific hints for better SQL generation:

```python
# Get SQL-optimized context
sql_context = enhanced_profiler.get_sql_generation_context("customers")

# Use in SQL agent for better query generation
from ryoma_ai.agent.sql import SqlAgent

agent = SqlAgent(model="gpt-4", mode="enhanced")
agent.add_datasource(datasource)

# The agent automatically uses enhanced metadata for:
# - Better table selection based on business purpose
# - Smarter column selection using SQL hints
# - Optimized joins using join candidate scores
# - Appropriate filtering based on data quality scores

response = agent.stream("Find high-value customers from last quarter")
```

### Join Pattern Discovery
Automatically discover and score potential join relationships:

```python
# Get table metadata with join patterns
table_metadata = enhanced_profiler.profile_table_enhanced("customers")

for pattern in table_metadata.common_join_patterns:
    print(f"Can join with {pattern['target_table']} on {pattern['join_column']}")
    print(f"Join type: {pattern['join_type']}, Confidence: {pattern['confidence']:.2%}")
```

### Data Quality Assessment
LLM-powered data quality analysis provides actionable insights:

```python
field_metadata = enhanced_profiler.profile_field_enhanced("customers", "phone")

print(f"Quality assessment: {field_metadata.data_quality_assessment}")
# Output: "Moderate quality with 15% missing values and inconsistent formatting.
#          Recommend data cleaning for phone number standardization."

# Use quality scores for column selection
high_quality_fields = [
    field_name for field_name, field_meta in table_metadata.field_metadata.items()
    if field_meta.base_profile.data_quality_score > 0.8
]
print(f"High quality fields: {high_quality_fields}")
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

### 1. **Choose the Right Profiling Mode**
- **Ibis-only**: Fast, consistent, database-native profiling
- **Ibis + LLM**: Production use with business context analysis
- **Hybrid**: Optimized Ibis base with cached LLM enhancement

```python
# Development: Fast Ibis-only profiling
dev_profiler = DatabaseProfiler(sample_size=1000, enable_llm_enhancement=False)

# Production: Ibis + LLM enhancement with caching
prod_profiler = EnhancedDatabaseProfiler(
    datasource=datasource,
    model=model,
    enable_llm_analysis=True,
    analysis_sample_size=100
)
```

### 2. **Optimize LLM Usage**
- Cache enhanced metadata to reduce API calls
- Use appropriate sample sizes for LLM analysis
- Enable LLM analysis only for critical tables

```python
# Cache enhanced metadata
enhanced_metadata = enhanced_profiler.profile_table_enhanced("customers")
# Subsequent calls use cached results

# Selective LLM analysis
important_tables = ["customers", "orders", "products"]
for table in important_tables:
    enhanced_profiler.profile_table_enhanced(table)
```

### 3. **Leverage Enhanced Insights**
- Use business purpose for better table selection
- Apply SQL hints for query optimization
- Utilize join scores for relationship discovery

```python
# Use enhanced metadata in SQL generation
sql_context = enhanced_profiler.get_sql_generation_context("customers")
# Pass to SQL agent for better query generation
```

### 4. **Monitor Performance and Costs**
- Track LLM API usage and costs
- Monitor profiling duration for large tables
- Cache profiles for frequently used tables
- Set up alerts for profiling failures

### 5. **Production Deployment**
- Schedule regular profile updates
- Use hybrid approach for cost optimization
- Implement proper error handling and fallbacks
- Monitor data quality trends over time

## 🔗 Related Documentation

- **[Enhanced SQL Agent](../agent/sql.md)** - Uses profiling for better queries
- **[Data Sources](../data-sources/index.md)** - Database connectors with profiling
- **[Architecture Guide](../../architecture/database-profiling.md)** - Technical details
