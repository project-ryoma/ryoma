# 📊 Database Profiling System

> **Comprehensive metadata extraction for Text-to-SQL applications**

## 🚀 Quick Start

```python
from ryoma_data import DataSource, DatabaseProfiler

# Create datasource
datasource = DataSource(
    "postgres",
    host="localhost",
    database="mydb",
    user="user",
    password="pass"
)

# Create profiler
profiler = DatabaseProfiler()

# Profile table
profile = profiler.profile_table(datasource, "customers")
print(f"Rows: {profile.row_count}")
print(f"Completeness: {profile.completeness_score}")
```

## 🎯 Core Features

| 📊 Feature | 💡 Use Case |
|------------|-------------|
| **Row counts & NULL stats** | Data completeness |
| **Distinct-value ratios** | Cardinality analysis |
| **Statistical measures** | Numeric profiling |
| **String analysis** | Text data insights |
| **Top-k frequent values** | Common patterns |
| **LSH similarity** | Column matching |

## 🔧 API Methods

```python
# Table profiling
profile = profiler.profile_table(datasource, "customers")

# Column analysis
column_profile = profiler.profile_column(datasource, "customers", "email")

# Configure profiler
profiler = DatabaseProfiler(
    sample_size=10000,
    top_k=20,
    enable_lsh=True
)
```

## 📊 Example Results

<details>
<summary>📋 Table Profile Example</summary>

```json
{
  "table_profile": {
    "row_count": 150000,
    "completeness_score": 0.95,
    "consistency_score": 0.88
  },
  "profiling_summary": {
    "profiling_method": "ibis_enhanced",
    "total_columns": 12
  }
}
```
</details>

<details>
<summary>📋 Column Profile Example</summary>

```json
{
  "email": {
    "semantic_type": "email",
    "data_quality_score": 0.92,
    "null_percentage": 5.2,
    "distinct_ratio": 0.98,
    "top_k_values": [
      {"value": "user@example.com", "count": 15, "percentage": 0.01}
    ]
  }
}
```
</details>

## 🎯 Advanced Features

### 🏷️ Semantic Type Detection
| 🔍 Type | 🎯 Use Case |
|---------|-------------|
| **📧 Email** | Contact analysis |
| **📞 Phone** | Communication data |
| **🌐 URL** | Web analytics |
| **🆔 ID** | Primary key detection |

### 📊 Data Quality Formula
```python
quality_score = (
    completeness * 0.5 +      # 1 - NULL%
    uniqueness * 0.3 +        # Distinct ratio
    reliability * 0.2         # Sample size
)
```

### 🔗 Column Similarity
```python
# Find similar columns
similar = datasource.find_similar_columns("customer_id", threshold=0.8)
# → ["user_id", "client_id", "account_id"]
```

## ⚙️ Configuration

### 🚀 Quick Setup
```python
from ryoma_data import DataSource, DatabaseProfiler

datasource = DataSource(
    "postgres",
    connection_string="postgresql://..."
)

profiler = DatabaseProfiler()
```

### 🎛️ Tuning Options
| 🎯 Use Case | 📊 Sample | 🔝 Top-K | 🔗 LSH |
|-------------|-----------|----------|--------|
| **🚀 Development** | 1K | 5 | Off |
| **⚖️ Production** | 10K | 10 | On |
| **🎯 High Accuracy** | 50K | 20 | On |

<details>
<summary>🔧 Custom Configuration</summary>

```python
from ryoma_data import DatabaseProfiler

profiler = DatabaseProfiler(
    sample_size=10000,
    top_k=10,
    enable_lsh=True
)
```
</details>

## 💻 Usage Examples

<details>
<summary>🚀 Basic Profiling</summary>

```python
from ryoma_data import DataSource, DatabaseProfiler

datasource = DataSource(
    "postgres",
    connection_string="postgresql://user:pass@host:5432/db"
)

# Profile table
profiler = DatabaseProfiler()
profile = profiler.profile_table(datasource, "customers")
method = profile["profiling_summary"]["profiling_method"]
print(f"Method: {method}")
```
</details>

<details>
<summary>🔍 Advanced Analysis</summary>

```python
# Column profiling
email_profile = datasource.profile_column("customers", "email")
if email_profile["semantic_type"] == "email":
    quality = email_profile["data_quality_score"]
    print(f"Email quality: {quality:.2f}")

# Enhanced catalog
catalog = datasource.get_enhanced_catalog(include_profiles=True)
for schema in catalog.schemas:
    for table in schema.tables:
        high_quality = table.get_high_quality_columns(min_quality_score=0.8)
        print(f"{table.table_name}: {len(high_quality)} high-quality columns")
```
</details>

<details>
<summary>⚡ Direct Ibis Access</summary>

```python
# Custom analysis with Ibis
conn = datasource.connect()
ibis_table = conn.table("customers")

stats = ibis_table.describe().to_pandas()
age_mean = ibis_table.age.mean().to_pandas()
top_cities = ibis_table.city.value_counts().limit(5).to_pandas()
```
</details>

## 🔧 Backend Support

| 🗄️ Database | 🚀 Native Features | 🎯 Best For |
|-------------|-------------------|-------------|
| **PostgreSQL** | `pg_stats`, histograms | Production OLTP |
| **BigQuery** | ML functions, `INFORMATION_SCHEMA` | Analytics |
| **DuckDB** | Advanced analytics | OLAP workloads |
| **SQLite** | `PRAGMA` optimizations | Development |
| **Snowflake** | Cloud-native views | Data warehouse |
| **MySQL** | `INFORMATION_SCHEMA` | Web backends |

## 🤖 Text-to-SQL Benefits

### 🔗 Enhanced Schema Linking
| 🎯 Feature | 💡 How It Helps |
|------------|-----------------|
| **Statistical relevance** | Uses row counts for table selection |
| **Semantic types** | Detects emails, phones, IDs |
| **Quality scores** | Filters low-quality columns |
| **Similarity analysis** | Finds related columns |

### ⚡ Smarter Query Generation
```python
# Profiling-informed optimization
if column_profile["distinct_ratio"] > 0.8:
    query += f"GROUP BY {column_name}"  # High cardinality
elif column_profile["null_percentage"] < 5:
    query += f"WHERE {column_name} IS NOT NULL"  # Low nulls
```

### 🛡️ Error Prevention
- **NULL handling** based on actual percentages
- **Type safety** using semantic types
- **Cardinality awareness** for optimization

## 🚀 Production Guide

### ✅ Deployment Checklist
- [ ] Create `DatabaseProfiler` instance
- [ ] Configure sampling for your data size
- [ ] Set quality thresholds
- [ ] Monitor profiling overhead
- [ ] Schedule regular updates

### 📊 Scaling Guide
| 📏 Table Size | ⚙️ Config | 📝 Notes |
|---------------|-----------|----------|
| < 100K rows | Default | Full analysis |
| 100K-1M rows | `sample_size=5000` | Balanced |
| > 1M rows | `sample_size=10000` | Optimized |

<details>
<summary>🔍 Monitoring & Troubleshooting</summary>

```python
# Check method used
method = profile["profiling_summary"]["profiling_method"]
if method == "standard":
    print("⚠️ Ibis not used - check compatibility")

# Monitor duration
duration = profile["table_profile"]["profiling_duration_seconds"]
if duration > 10:
    print("⚠️ Consider reducing sample_size")
```
</details>

## 📚 API Reference

<details>
<summary>🔧 Core Methods</summary>

```python
# Table profiling
profile = datasource.profile_table(table_name, schema=None)

# Column profiling
column_profile = datasource.profile_column(table_name, column_name, schema=None)

# Enhanced catalog
catalog = datasource.get_enhanced_catalog(include_profiles=True)

# Column similarity
similar = datasource.find_similar_columns(column_name, threshold=0.8)
```
</details>

<details>
<summary>⚙️ Configuration Options</summary>

```python
from ryoma_data import DatabaseProfiler

profiler = DatabaseProfiler(
    sample_size=10000,
    top_k=10,
    enable_lsh=True
)
```
</details>

## 🚨 Troubleshooting

| ⚠️ Issue | 💡 Solution |
|----------|-------------|
| **Slow profiling** | Reduce `sample_size` |
| **Memory errors** | Set `enable_lsh=False` |
| **Permission errors** | Check DB user permissions |
| **Type errors** | Auto-handled by fallback |

<details>
<summary>🔍 Debug Examples</summary>

```python
# Check profiling method
method = profile["profiling_summary"]["profiling_method"]
if method == "standard":
    print("Ibis not used - check compatibility")

# Reduce sample for large tables
profiler = DatabaseProfiler(sample_size=1000)
```
</details>

## 🔮 Roadmap

### 🚀 Upcoming Features
- **🤖 ML-based pattern detection** - Advanced semantic types
- **🔗 Cross-table relationships** - Statistical correlation analysis
- **⏰ Temporal profiling** - Data quality tracking over time
- **🎯 Custom semantic types** - Domain-specific definitions

---

## 📖 References

| 📚 Resource | 🔗 Link |
|-------------|---------|
| **Research Paper** | "Automatic Metadata Extraction for Text-to-SQL" |
| **Ibis Framework** | [ibis-project.org](https://ibis-project.org) |
| **MinHash/LSH** | Locality-Sensitive Hashing algorithms |
| **Statistical Methods** | Database profiling techniques |
