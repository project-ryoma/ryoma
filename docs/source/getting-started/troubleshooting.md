# 🔧 Troubleshooting Guide

Common issues and solutions for Ryoma AI deployment and usage.

## 🚨 Common Errors

### Store Configuration Issues

#### "Store parameter is required" Error
```
ValueError: store parameter is required - agents must receive stores from CLI
```

**Cause**: Attempting to create agents programmatically without providing unified stores.

**Solution**:
```python
# ❌ Wrong: Creating agent without stores
agent = SqlAgent("gpt-4o", mode="enhanced")

# ✅ Correct: Use CLI or provide stores
from langchain_core.stores import InMemoryStore
agent = SqlAgent(
    model="gpt-4o",
    mode="enhanced", 
    datasource=datasource,
    store=InMemoryStore()  # or unified_meta_store
)
```

#### "Catalog search requires vector store" Error
```
ValueError: Catalog search requires vector store and proper indexing
```

**Cause**: Vector store not configured or catalog not indexed.

**Solution**:
```bash
# Check configuration
ryoma-ai> /config

# Configure vector store and index
ryoma-ai> /index-catalog table
```

### Vector Store Issues

#### Dimension Mismatch Error
```
ValueError: Dimension mismatch: expected 1536, got 768
```

**Cause**: Embedding model dimensions don't match vector store configuration.

**Solution**:
```json
{
  "embedding_model": "text-embedding-ada-002",  // 1536 dimensions
  "vector_store": {
    "type": "chroma",
    "dimension": 1536  // Must match embedding model
  }
}
```

#### PGVector Table Name Issues
```
Tables created with names: langchain_pg_collection, langchain_pg_embedding
```

**Cause**: LangChain PGVector hardcodes table names with prefixes.

**Solution**:
```python
# Current limitation - table names are fixed
# For custom names, consider alternative vector stores:
{
  "vector_store": {
    "type": "chroma",  // Use Chroma instead
    "collection_name": "custom_name"  // Full control over names
  }
}
```

### Data Source Connection Issues

#### Connection Timeout
```
OperationalError: could not connect to server: Connection timed out
```

**Cause**: Network connectivity or incorrect connection parameters.

**Solution**:
```json
{
  "datasources": [
    {
      "type": "postgres",
      "host": "correct-host",
      "port": 5432,
      "options": {
        "connect_timeout": 30,  // Increase timeout
        "sslmode": "prefer"     // Handle SSL issues
      }
    }
  ]
}
```

#### Authentication Failure
```
OperationalError: FATAL: password authentication failed
```

**Solution**:
```bash
# Check credentials
ryoma-ai> /setup

# Or update configuration
{
  "datasources": [
    {
      "type": "postgres",
      "connection_string": "postgresql://correct_user:correct_pass@host:5432/db"
    }
  ]
}
```

### Agent Execution Issues

#### SQL Validation Errors
```
ValidationError: Query blocked by safety policy
```

**Cause**: SQL safety policies blocking legitimate queries.

**Solution**:
```json
{
  "agent": {
    "safety_config": {
      "enable_validation": true,
      "allowed_operations": ["SELECT", "WITH", "CTE"],
      "require_where_clause": false,  // Relax if needed
      "max_rows": 100000             // Increase limit
    }
  }
}
```

#### Model API Errors
```
RateLimitError: You exceeded your current quota
```

**Solution**:
```python
# Configure retry and fallback
agent_config = {
    "model": "gpt-4o",
    "model_parameters": {
        "max_retries": 5,
        "retry_delay": 2.0
    },
    "fallback_model": "gpt-3.5-turbo"  // Fallback model
}
```

## 🔍 Debugging Tools

### Configuration Validation
```bash
# Check all configurations
ryoma-ai --validate-config

# Test store connectivity  
ryoma-ai --test-stores

# Validate specific components
ryoma-ai --test-stores meta_store
ryoma-ai --test-stores vector_store
ryoma-ai --test-datasources
```

### CLI Debugging Commands
```bash
# Show detailed configuration
ryoma-ai> /config

# Check agent status
ryoma-ai> /agents

# View agent statistics
ryoma-ai> /stats

# Test data source connection
ryoma-ai> /datasources
```

### Enable Debug Logging
```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
ryoma_logger = logging.getLogger('ryoma_ai')
ryoma_logger.setLevel(logging.DEBUG)

# Create agent with debug info
agent = SqlAgent("gpt-4o", mode="enhanced")
```

### Store Validation
```python
# Validate store functionality
from ryoma_ai.store.validator import StoreValidator

validator = StoreValidator()

# Test metadata store
meta_result = validator.test_metadata_store(meta_store)
print(f"Meta store status: {meta_result['status']}")

# Test vector store
vector_result = validator.test_vector_store(vector_store)
print(f"Vector store status: {vector_result['status']}")
```

## 🚀 Performance Troubleshooting

### Slow Query Performance
```bash
# Index catalogs for faster search
ryoma-ai> /index-catalog table

# Check indexing status
ryoma-ai> /search-catalog test query
```

### High Memory Usage
```json
{
  "vector_store": {
    "type": "chroma",  // Use persistent storage
    "extra_configs": {
      "persist_directory": "./data/vectors"  // Reduce memory usage
    }
  },
  "agent": {
    "cache_size": 100,      // Limit cache size
    "max_context_length": 8000  // Reduce context
  }
}
```

### API Rate Limiting
```json
{
  "model_parameters": {
    "max_retries": 5,
    "retry_delay": 2.0,
    "exponential_backoff": true
  },
  "agent": {
    "request_throttle": 0.5  // Add delay between requests
  }
}
```

## 🔧 Recovery Procedures

### Reset Configuration
```bash
# Backup current config
cp ~/.ryoma/config.json ~/.ryoma/config.json.backup

# Reset to defaults
rm ~/.ryoma/config.json
ryoma-ai --setup
```

### Clear Vector Store
```bash
# Clear and rebuild vector indexes
ryoma-ai> /clear-vectors
ryoma-ai> /index-catalog table
```

### Rebuild Metadata
```bash
# Clear metadata and re-profile
ryoma-ai> /clear-metadata  
ryoma-ai> /profile-datasource
```

## 📊 Health Checks

### System Health Check
```python
from ryoma_ai.diagnostics import HealthChecker

checker = HealthChecker()

# Comprehensive health check
health = checker.check_system_health()
print(f"Overall status: {health['status']}")

for component, status in health['components'].items():
    print(f"  {component}: {status['status']}")
    if status['issues']:
        print(f"    Issues: {status['issues']}")
```

### Store Health Check
```python
# Check individual store health
meta_health = checker.check_metadata_store(meta_store)
vector_health = checker.check_vector_store(vector_store)

print(f"Meta store: {meta_health['status']}")
print(f"Vector store: {vector_health['status']}")
```

## 🛠️ Advanced Troubleshooting

### Memory Leak Investigation
```python
import tracemalloc

# Start memory tracing
tracemalloc.start()

# Run operations
agent = SqlAgent("gpt-4o")
agent.stream("SELECT * FROM large_table LIMIT 10")

# Check memory usage
current, peak = tracemalloc.get_traced_memory()
print(f"Current memory: {current / 1024 / 1024:.1f} MB")
print(f"Peak memory: {peak / 1024 / 1024:.1f} MB")
```

### Circular Import Debugging
```python
# Check import dependencies
from ryoma_ai.diagnostics import ImportAnalyzer

analyzer = ImportAnalyzer()
circular_imports = analyzer.find_circular_imports('ryoma_ai')

if circular_imports:
    print("Circular import detected:")
    for cycle in circular_imports:
        print(f"  {' → '.join(cycle)}")
```

### Store State Investigation
```python
# Inspect store state
def debug_store_state(store):
    if hasattr(store, 'mget'):
        # Get all stored keys
        try:
            keys = store.mget(['datasource_main', 'catalog_metadata'])
            for i, key in enumerate(['datasource_main', 'catalog_metadata']):
                print(f"{key}: {keys[i] is not None}")
        except Exception as e:
            print(f"Store access error: {e}")
    
debug_store_state(meta_store)
```

## 📞 Getting Help

### Support Channels
- **GitHub Issues**: [Report bugs and feature requests](https://github.com/project-ryoma/ryoma/issues)
- **Documentation**: [Complete documentation](https://docs.ryoma.dev)
- **Community**: Join discussions for community support

### Diagnostic Information
When reporting issues, include:

```bash
# System information
ryoma-ai --version
ryoma-ai --system-info

# Configuration dump (remove sensitive data)
ryoma-ai --config-dump > config-debug.json

# Recent logs
tail -100 ~/.ryoma/logs/ryoma.log
```

### Error Report Template
```markdown
**Environment:**
- OS: [macOS/Linux/Windows]
- Python version: [3.9/3.10/3.11]
- Ryoma version: [from ryoma-ai --version]

**Configuration:**
[Paste relevant config sections, remove passwords]

**Error:**
[Full error message and traceback]

**Steps to Reproduce:**
1. [Step 1]
2. [Step 2]
3. [Error occurs]

**Expected vs Actual:**
- Expected: [What should happen]
- Actual: [What actually happened]
```

## 🔗 Related Documentation

- **[Configuration Reference](configuration-reference.md)** - Complete config options
- **[Store Architecture](../architecture/store-architecture.md)** - Storage system
- **[CLI Usage](cli-usage.md)** - Command-line interface
- **[Advanced Setup](advanced-setup.md)** - Production deployment