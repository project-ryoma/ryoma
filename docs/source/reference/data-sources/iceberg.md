# Apache Iceberg Data Source

The Apache Iceberg data source provides advanced metadata integration for text-to-SQL applications by leveraging Iceberg's rich catalog metadata instead of runtime profiling.

## Overview

Apache Iceberg is an open table format that provides:

- **Rich Metadata**: Pre-computed statistics, schema evolution, partition information
- **ACID Transactions**: Consistent table snapshots and isolation
- **Schema Evolution**: Safe schema changes with backward compatibility  
- **Time Travel**: Access to historical table states
- **Hidden Partitioning**: Automatic partition management

The Ryoma Iceberg integration leverages these capabilities to provide superior metadata for text-to-SQL generation without the overhead of runtime data sampling.

## Key Advantages over Traditional SQL Sources

| Feature | Traditional SQL | Iceberg Integration |
|---------|----------------|-------------------|
| Metadata Source | Runtime profiling | Native catalog metadata |
| Statistics Accuracy | Sample-based estimates | Full table statistics |
| Performance | Slow for large tables | Instant metadata access |
| Schema Evolution | Manual tracking | Automatic evolution history |
| Partitioning | Manual analysis | Native partition awareness |
| Data Freshness | Unknown | Snapshot timestamps |

## Installation

```bash
pip install pyiceberg
```

For specific catalog backends:

```bash
# For AWS Glue
pip install pyiceberg[glue]

# For Google Cloud
pip install pyiceberg[gcs] 

# For Azure
pip install pyiceberg[adls]
```

## Configuration

### REST Catalog

```python
from ryoma_data.iceberg import IcebergDataSource

# REST catalog (recommended for production)
iceberg_ds = IcebergDataSource(
    catalog_name="production",
    catalog_type="rest",
    catalog_uri="http://iceberg-catalog:8181",
    warehouse="s3a://data-lake/warehouse",
    properties={
        "s3.endpoint": "http://s3:9000",
        "s3.access-key-id": "your-access-key",
        "s3.secret-access-key": "your-secret-key"
    }
)
```

### Hive Metastore Catalog

```python
# Hive Metastore catalog
iceberg_ds = IcebergDataSource(
    catalog_name="hive_catalog", 
    catalog_type="hive",
    catalog_uri="thrift://hive-metastore:9083",
    warehouse="/user/hive/warehouse",
    properties={
        "hive.metastore.uris": "thrift://hive-metastore:9083"
    }
)
```

### AWS Glue Catalog

```python
# AWS Glue catalog
iceberg_ds = IcebergDataSource(
    catalog_name="glue_catalog",
    catalog_type="glue", 
    properties={
        "glue.region": "us-west-2",
        "glue.catalog-id": "123456789012"
    }
)
```

## Usage with SQL Agent

```python
from ryoma_ai.agent.sql import SqlAgent

# Create enhanced SQL agent with Iceberg
sql_agent = SqlAgent(
    model="gpt-4",
    datasource=iceberg_ds,
    use_enhanced_mode=True,
    safety_config={
        "max_result_rows": 1000,
        "blocked_functions": ["DROP", "DELETE"]
    }
)

# Ask questions - the agent uses rich Iceberg metadata
response = sql_agent.invoke({
    "messages": [("human", "Show top 10 customers by revenue this quarter")]
})
```

## Enhanced Metadata Features

### Rich Column Profiles

Iceberg provides comprehensive column statistics without sampling:

```python
# Get detailed table profile using native metadata
profile = iceberg_ds.profile_table("orders", schema="sales")

print(f"Profiling method: {profile['profiling_summary']['profiling_method']}")
# Output: "iceberg_metadata" (no runtime sampling needed)

print(f"Row count: {profile['table_profile']['row_count']:,}")
# Exact count from Iceberg snapshots

for col_name, col_profile in profile['column_profiles'].items():
    print(f"{col_name}: {col_profile['null_percentage']:.1f}% NULL")
    # Accurate null percentages from Iceberg statistics
```

### Schema Evolution Awareness

The agent understands schema changes over time:

```python
# Get catalog with evolution history
catalog = iceberg_ds.get_catalog(schema="ecommerce")

for table in catalog.schemas[0].tables:
    if table.profile and table.profile.last_updated:
        print(f"Table {table.table_name} last updated: {table.profile.last_updated}")
```

### Enhanced Prompt Generation

Iceberg metadata creates richer prompts for better SQL generation:

```python
prompt = iceberg_ds.prompt(schema="ecommerce", table="orders")
print(prompt)
```

Output includes:
- Exact row counts from snapshots
- Column null percentages  
- Data freshness timestamps
- Partition information
- Schema evolution context

## Partition-Aware Queries

Iceberg's partition metadata helps generate optimized queries:

```python
# The SQL agent automatically understands partitioning
response = sql_agent.invoke({
    "messages": [("human", "Show sales data for last month")]
})
# Generates partition-aware SQL leveraging date partitions
```

## Time Travel Capabilities

Access historical data states:

```python
# Query historical table state (if supported by underlying engine)
response = sql_agent.invoke({
    "messages": [("human", "Compare current sales with sales from last quarter")]
})
# Can leverage Iceberg's time travel for historical comparisons
```

## Best Practices

### Production Deployment

1. **Use REST Catalog**: Provides best performance and scalability
2. **Configure Caching**: Enable metadata caching for faster access
3. **Monitor Snapshots**: Track snapshot creation for data freshness
4. **Partition Strategy**: Design partitions for query patterns

### Performance Optimization

1. **Catalog Properties**: Tune catalog configuration for your workload
2. **Metadata Refresh**: Configure appropriate refresh intervals
3. **Connection Pooling**: Use connection pools for high-throughput scenarios

### Security Considerations

1. **Access Control**: Implement proper catalog-level security
2. **Credential Management**: Use secure credential storage
3. **Network Security**: Secure catalog communication channels

## Integration with Enhanced SQL Agent

The Iceberg data source works seamlessly with Ryoma's enhanced SQL agent features:

### Multi-Step Reasoning

```python
# Enhanced agent uses Iceberg metadata for better reasoning
sql_agent = SqlAgent(
    model="gpt-4",
    datasource=iceberg_ds,
    use_enhanced_mode=True  # Leverages rich metadata
)
```

### Schema Linking

Rich metadata improves table and column selection:

```python
# Better schema linking with detailed statistics
analysis = sql_agent.analyze_schema("customer purchase patterns")
# Uses null percentages, distinct ratios, and data freshness
```

### Query Planning

Partition awareness enables better query optimization:

```python
# Query planner understands Iceberg partitions
plan = sql_agent.create_query_plan("monthly sales analysis")
# Generates partition-pruned queries automatically
```

## Troubleshooting

### Common Issues

1. **PyIceberg Import Error**
   ```bash
   pip install pyiceberg[rest]  # Install with REST support
   ```

2. **Catalog Connection Failed**
   ```python
   # Verify catalog URI and credentials
   properties = {
       "uri": "http://your-catalog:8181",
       "credential": "your-token"
   }
   ```

3. **Missing Statistics**
   ```python
   # Some tables may lack comprehensive statistics
   # Iceberg computes stats during writes/compaction
   ```

### Debug Mode

Enable detailed logging:

```python
import logging
logging.getLogger("ryoma_data.iceberg").setLevel(logging.DEBUG)
```

## Comparison with Other Formats

| Feature | Iceberg | Delta Lake | Hudi |
|---------|---------|------------|------|
| Schema Evolution | ✅ Full | ✅ Full | ✅ Limited |
| Statistics | ✅ Rich | ✅ Good | ⚠️ Basic |
| Time Travel | ✅ Yes | ✅ Yes | ✅ Yes |
| Catalog Support | ✅ Multiple | ⚠️ Limited | ⚠️ Limited |
| Ryoma Integration | ✅ Native | 🔄 Planned | 🔄 Planned |

## Future Enhancements

Planned improvements for Iceberg integration:

1. **Advanced Statistics**: Histogram and sketch statistics
2. **Query Optimization**: Cost-based optimization using Iceberg metrics
3. **Real-time Metadata**: Stream metadata updates for fresh statistics
4. **Multi-Engine Support**: Enhanced support for Spark, Trino, Flink
5. **Machine Learning**: ML-based query pattern analysis

## Examples

See [example_iceberg.py](../../../example/example_iceberg.py) for comprehensive usage examples including:

- REST catalog configuration
- SQL agent integration  
- Metadata profiling
- Enhanced prompt generation
- Performance comparisons