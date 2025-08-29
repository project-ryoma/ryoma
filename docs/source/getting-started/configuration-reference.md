# ⚙️ Configuration Reference

Complete reference for configuring Ryoma AI's three-tier architecture: metadata stores, vector stores, and data sources.

## 📋 Configuration Structure

### Complete Configuration Schema
```json
{
  "model": "gpt-4o",
  "mode": "enhanced", 
  "embedding_model": "text-embedding-ada-002",
  
  "meta_store": {
    "type": "memory",
    "connection_string": null,
    "options": {}
  },
  
  "vector_store": {
    "type": "chroma",
    "collection_name": "ryoma_vectors", 
    "dimension": 768,
    "distance_metric": "cosine",
    "extra_configs": {
      "persist_directory": "./data/vectors"
    }
  },
  
  "datasources": [
    {
      "name": "default",
      "type": "postgres",
      "host": "localhost",
      "port": 5432,
      "database": "mydb",
      "user": "postgres",
      "password": "password"
    }
  ],
  
  "agent": {
    "auto_approve_all": false,
    "retry_count": 3,
    "timeout_seconds": 300
  }
}
```

## 🗄️ Metadata Store Configuration

### Memory Store (Default)
```json
{
  "meta_store": {
    "type": "memory"
  }
}
```

**Use Cases:**
- Development and testing
- Single-session usage
- No persistence required

### PostgreSQL Store
```json
{
  "meta_store": {
    "type": "postgres",
    "connection_string": "postgresql://user:password@localhost:5432/metadata_db",
    "options": {
      "pool_size": 10,
      "max_overflow": 20,
      "echo": false
    }
  }
}
```

**Use Cases:**
- Production deployments
- Multi-user environments
- Persistent metadata required

### Redis Store
```json
{
  "meta_store": {
    "type": "redis",
    "connection_string": "redis://localhost:6379/0",
    "options": {
      "decode_responses": true,
      "socket_timeout": 30,
      "retry_on_timeout": true
    }
  }
}
```

**Use Cases:**
- Distributed deployments
- High-performance caching
- Microservices architecture

## 🔍 Vector Store Configuration

### Chroma (Recommended for Development)
```json
{
  "vector_store": {
    "type": "chroma",
    "collection_name": "ryoma_vectors",
    "dimension": 1536,
    "distance_metric": "cosine",
    "extra_configs": {
      "persist_directory": "./data/chroma",
      "anonymized_telemetry": false
    }
  }
}
```

### FAISS (In-Memory)
```json
{
  "vector_store": {
    "type": "faiss", 
    "collection_name": "ryoma_vectors",
    "dimension": 1536,
    "distance_metric": "cosine",
    "extra_configs": {
      "index_type": "IndexFlatIP",
      "normalize_vectors": true
    }
  }
}
```

### Qdrant (Production)
```json
{
  "vector_store": {
    "type": "qdrant",
    "collection_name": "ryoma_vectors",
    "dimension": 1536, 
    "distance_metric": "cosine",
    "extra_configs": {
      "url": "http://localhost:6333",
      "api_key": "your-qdrant-api-key",
      "timeout": 30
    }
  }
}
```

### PGVector (PostgreSQL Extension)
```json
{
  "vector_store": {
    "type": "pgvector",
    "collection_name": "ryoma_vectors",
    "dimension": 1536,
    "distance_metric": "cosine", 
    "extra_configs": {
      "connection_string": "postgresql://user:password@localhost:5432/vector_db",
      "table_name": "langchain_pg_embedding",
      "collection_table_name": "langchain_pg_collection"
    }
  }
}
```

**Note**: PGVector uses fixed table names with `langchain_pg_` prefix. For custom table names, consider using a custom vector store implementation.

## 💾 Data Source Configuration

### PostgreSQL
```json
{
  "name": "main_db",
  "type": "postgres", 
  "host": "localhost",
  "port": 5432,
  "database": "myapp",
  "user": "postgres",
  "password": "password",
  "options": {
    "sslmode": "require",
    "connect_timeout": 10
  }
}
```

### MySQL
```json
{
  "name": "mysql_db",
  "type": "mysql",
  "host": "localhost", 
  "port": 3306,
  "database": "myapp",
  "user": "root",
  "password": "password",
  "options": {
    "charset": "utf8mb4",
    "autocommit": true
  }
}
```

### Snowflake
```json
{
  "name": "warehouse",
  "type": "snowflake",
  "account": "your-account",
  "user": "your-username", 
  "password": "your-password",
  "database": "ANALYTICS",
  "schema": "PUBLIC",
  "warehouse": "COMPUTE_WH",
  "role": "DATA_ANALYST"
}
```

### SQLite
```json
{
  "name": "local_db",
  "type": "sqlite",
  "database": "/path/to/database.db"
}
```

### BigQuery
```json
{
  "name": "bigquery_ds",
  "type": "bigquery",
  "project_id": "your-project-id",
  "dataset_id": "analytics",
  "credentials_path": "/path/to/service-account.json"
}
```

### DuckDB
```json
{
  "name": "analytics_db",
  "type": "duckdb",
  "database": "/path/to/analytics.duckdb",
  "options": {
    "read_only": false,
    "memory_limit": "2GB"
  }
}
```

## 🎛️ Agent Configuration

### Basic Agent Settings
```json
{
  "agent": {
    "auto_approve_all": false,
    "retry_count": 3,
    "timeout_seconds": 300,
    "enable_logging": true,
    "log_level": "INFO"
  }
}
```

### SQL Agent Specific
```json
{
  "agent": {
    "sql_mode": "enhanced",
    "safety_config": {
      "enable_validation": true,
      "allowed_operations": ["SELECT", "WITH", "CTE"],
      "blocked_operations": ["DROP", "DELETE", "UPDATE"],
      "max_rows": 50000,
      "max_execution_time": 300,
      "require_where_clause": false
    },
    "reforce_config": {
      "enable_self_refinement": true,
      "parallel_generation": true,
      "consensus_voting": true,
      "exploration_depth": 3
    }
  }
}
```

## 🌍 Environment-Based Configuration

### Development Environment
```json
{
  "model": "gpt-3.5-turbo",
  "mode": "basic",
  "embedding_model": "text-embedding-ada-002",
  
  "meta_store": {"type": "memory"},
  "vector_store": {"type": "faiss"},
  "datasources": [
    {"type": "sqlite", "database": ":memory:"}
  ],
  
  "agent": {
    "auto_approve_all": true,
    "retry_count": 1,
    "timeout_seconds": 60
  }
}
```

### Production Environment
```json
{
  "model": "gpt-4o",
  "mode": "enhanced", 
  "embedding_model": "text-embedding-ada-002",
  
  "meta_store": {
    "type": "postgres",
    "connection_string": "postgresql://user:pass@prod-meta:5432/metadata"
  },
  "vector_store": {
    "type": "qdrant",
    "extra_configs": {
      "url": "http://qdrant-prod:6333",
      "api_key": "${QDRANT_API_KEY}"
    }
  },
  "datasources": [
    {
      "name": "warehouse",
      "type": "snowflake", 
      "account": "${SNOWFLAKE_ACCOUNT}",
      "user": "${SNOWFLAKE_USER}",
      "password": "${SNOWFLAKE_PASSWORD}"
    }
  ],
  
  "agent": {
    "auto_approve_all": false,
    "retry_count": 3,
    "timeout_seconds": 300,
    "safety_config": {
      "enable_validation": true,
      "max_rows": 100000,
      "allowed_operations": ["SELECT", "WITH"]
    }
  }
}
```

## 📁 Configuration Management

### Configuration File Location
```bash
# Default location
~/.ryoma/config.json

# Custom location via environment
export RYOMA_CONFIG_PATH="/path/to/custom/config.json"
```

### Environment Variable Substitution
```json
{
  "datasources": [
    {
      "type": "postgres",
      "host": "${DB_HOST:localhost}",
      "database": "${DB_NAME}",
      "user": "${DB_USER}",
      "password": "${DB_PASSWORD}"
    }
  ]
}
```

### Configuration Validation
```bash
# Validate configuration
ryoma-ai --validate-config

# Check specific section
ryoma-ai --validate-config meta_store
```

## 🚀 Configuration Examples

### Multi-Database Setup
```json
{
  "datasources": [
    {
      "name": "transactional",
      "type": "postgres",
      "host": "postgres-prod",
      "database": "transactions"
    },
    {
      "name": "analytics", 
      "type": "snowflake",
      "account": "analytics-account",
      "warehouse": "ANALYTICS_WH"
    },
    {
      "name": "local_cache",
      "type": "sqlite", 
      "database": "./cache/local.db"
    }
  ]
}
```

### High-Performance Setup
```json
{
  "model": "gpt-4o",
  "embedding_model": "text-embedding-3-large",
  
  "meta_store": {
    "type": "redis",
    "connection_string": "redis://redis-cluster:6379/0",
    "options": {
      "socket_timeout": 5,
      "retry_on_timeout": true
    }
  },
  
  "vector_store": {
    "type": "qdrant",
    "dimension": 3072,  # text-embedding-3-large
    "distance_metric": "cosine",
    "extra_configs": {
      "url": "http://qdrant-cluster:6333",
      "prefer_grpc": true,
      "timeout": 30
    }
  }
}
```

## 🔧 Troubleshooting Configuration

### Common Configuration Issues

#### Store Connection Errors
```bash
# Check store connectivity
ryoma-ai --test-stores

# Validate specific store type
ryoma-ai --test-stores meta_store
```

#### Vector Store Dimension Mismatch
```json
{
  "vector_store": {
    "dimension": 1536,  # Must match embedding model
    "extra_configs": {
      "auto_create_collection": true  # Auto-handle dimension
    }
  }
}
```

#### Data Source Authentication
```json
{
  "datasources": [
    {
      "type": "postgres",
      "connection_string": "postgresql://user:password@host:5432/db",
      "options": {
        "connect_timeout": 30,
        "command_timeout": 300
      }
    }
  ]
}
```

### Configuration Migration
```python
# Migrate from old format
from ryoma_ai.config.migrator import ConfigMigrator

migrator = ConfigMigrator()
new_config = migrator.migrate_legacy_config("/path/to/old/config.json")
migrator.save_config(new_config, "/path/to/new/config.json")
```

## 🔗 Related Documentation

- **[Store Architecture](../architecture/store-architecture.md)** - Unified storage system
- **[CLI Usage](cli-usage.md)** - Command-line interface
- **[Advanced Setup](advanced-setup.md)** - Production configuration
- **[Data Sources](../reference/data-sources/index.md)** - Database connectors