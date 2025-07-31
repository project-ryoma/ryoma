# 🔧 Advanced Setup

This guide covers advanced configuration options and production deployment strategies for Ryoma.

## 🎯 Agent Modes

Ryoma offers different agent modes optimized for various use cases:

### Enhanced Mode (Recommended)
```python
from ryoma_ai.agent.sql import SqlAgent

agent = SqlAgent(
    model="gpt-4",
    mode="enhanced",  # Multi-step reasoning with safety validation
    safety_config={
        "enable_validation": True,
        "max_retries": 3,
        "allowed_operations": ["SELECT", "WITH", "CTE"]
    }
)
```

**Features:**
- ✅ Advanced schema linking
- ✅ Query planning and optimization
- ✅ Safety validation
- ✅ Error handling with retry logic
- ✅ Comprehensive logging

### ReFoRCE Mode (State-of-the-Art)
```python
agent = SqlAgent(
    model="gpt-4",
    mode="reforce",  # Research-based optimizations
    reforce_config={
        "enable_self_refinement": True,
        "parallel_generation": True,
        "consensus_voting": True,
        "exploration_depth": 3
    }
)
```

**Features:**
- 🚀 Self-refinement workflow
- 🚀 Format restriction generation
- 🚀 Column exploration with feedback
- 🚀 Parallel SQL generation
- 🚀 Majority-vote consensus

## 🗄️ Database Configuration

### PostgreSQL with Profiling
```python
from ryoma_ai.datasource.postgres import PostgresDataSource

datasource = PostgresDataSource(
    connection_string="postgresql://user:pass@host:5432/db",
    enable_profiling=True,
    profiler_config={
        "sample_size": 10000,      # Rows to analyze
        "top_k": 10,               # Top frequent values
        "enable_lsh": True,        # Column similarity
        "lsh_threshold": 0.8       # Similarity threshold
    }
)
```

### Snowflake with Connection Pooling
```python
from ryoma_ai.datasource.snowflake import SnowflakeDataSource

datasource = SnowflakeDataSource(
    account="your-account",
    user="your-user",
    password="your-password",
    database="your-database",
    warehouse="your-warehouse",
    enable_profiling=True,
    connection_config={
        "pool_size": 5,
        "max_overflow": 10,
        "pool_timeout": 30
    }
)
```

### BigQuery with Service Account
```python
from ryoma_ai.datasource.bigquery import BigQueryDataSource

datasource = BigQueryDataSource(
    project_id="your-project",
    credentials_path="/path/to/service-account.json",
    enable_profiling=True,
    query_config={
        "use_query_cache": True,
        "maximum_bytes_billed": 1000000000  # 1GB limit
    }
)
```

## 🛡️ Security Configuration

### Safety Validation
```python
from ryoma_ai.agent.sql import SqlAgent

agent = SqlAgent(
    model="gpt-4",
    mode="enhanced",
    safety_config={
        "enable_validation": True,
        "allowed_operations": [
            "SELECT", "WITH", "CTE", "UNION", "JOIN"
        ],
        "blocked_operations": [
            "DROP", "DELETE", "UPDATE", "INSERT", "TRUNCATE"
        ],
        "max_rows": 50000,
        "max_execution_time": 300,  # 5 minutes
        "require_where_clause": True,
        "block_cross_database": True
    }
)
```

### Custom Validation Rules
```python
from ryoma_ai.agent.internals.sql_safety_validator import (
    SqlSafetyValidator, ValidationRule
)

# Define custom validation rules
custom_rules = [
    ValidationRule(
        name="no_production_tables",
        pattern=r"FROM\s+prod\.",
        message="Production tables are not allowed",
        severity="error"
    ),
    ValidationRule(
        name="require_limit",
        pattern=r"SELECT.*(?!.*LIMIT)",
        message="All queries must include LIMIT clause",
        severity="warning"
    )
]

# Apply to agent
validator = SqlSafetyValidator(custom_rules=custom_rules)
agent.set_safety_validator(validator)
```

## 🔧 Model Configuration

### OpenAI Models
```python
agent = SqlAgent(
    model="gpt-4",
    model_parameters={
        "temperature": 0.1,        # Low temperature for consistency
        "max_tokens": 2000,        # Sufficient for complex queries
        "top_p": 0.9,
        "frequency_penalty": 0.1
    }
)
```

### Anthropic Claude
```python
agent = SqlAgent(
    model="claude-3-sonnet-20240229",
    model_parameters={
        "temperature": 0.1,
        "max_tokens": 4000,
        "top_p": 0.9
    }
)
```

### Local Models (Ollama)
```python
from ryoma_ai.models.ollama import OllamaModel

model = OllamaModel(
    model_name="codellama:13b",
    base_url="http://localhost:11434"
)

agent = SqlAgent(
    model=model,
    mode="enhanced"
)
```

## 📊 Monitoring and Logging

### Enable Detailed Logging
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ryoma.log'),
        logging.StreamHandler()
    ]
)

# Enable Ryoma-specific logging
ryoma_logger = logging.getLogger('ryoma_ai')
ryoma_logger.setLevel(logging.DEBUG)
```

### Performance Monitoring
```python
from ryoma_ai.monitoring import PerformanceMonitor

# Enable performance tracking
monitor = PerformanceMonitor(
    track_query_time=True,
    track_profiling_time=True,
    track_model_calls=True,
    export_metrics=True
)

agent = SqlAgent(
    model="gpt-4",
    mode="enhanced",
    monitor=monitor
)
```

## 🚀 Production Deployment

### Docker Configuration
```dockerfile
FROM python:3.11-slim

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . /app
WORKDIR /app

# Set environment variables
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV DATABASE_URL=${DATABASE_URL}

# Run application
CMD ["python", "app.py"]
```

### Environment Variables
```bash
# API Keys
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Database Configuration
DATABASE_URL=postgresql://user:pass@host:5432/db
ENABLE_PROFILING=true
PROFILER_SAMPLE_SIZE=10000

# Security Settings
ENABLE_SAFETY_VALIDATION=true
MAX_QUERY_ROWS=50000
ALLOWED_OPERATIONS=SELECT,WITH,CTE

# Performance Settings
AGENT_MODE=enhanced
MODEL_TEMPERATURE=0.1
MAX_RETRIES=3
```

### Health Checks
```python
from ryoma_ai.health import HealthChecker

def health_check():
    checker = HealthChecker()
    
    # Check database connectivity
    db_status = checker.check_database(datasource)
    
    # Check model availability
    model_status = checker.check_model(agent.model)
    
    # Check profiling system
    profiler_status = checker.check_profiler(datasource)
    
    return {
        "database": db_status,
        "model": model_status,
        "profiler": profiler_status,
        "overall": all([db_status, model_status, profiler_status])
    }
```

## 🔄 Migration Guide

### From Basic to Enhanced Mode
```python
# Before (Basic mode)
agent = SqlAgent("gpt-3.5-turbo")

# After (Enhanced mode)
agent = SqlAgent(
    model="gpt-4",
    mode="enhanced",
    safety_config={"enable_validation": True}
)
```

### Enabling Database Profiling
```python
# Before (No profiling)
datasource = PostgresDataSource(connection_string)

# After (With profiling)
datasource = PostgresDataSource(
    connection_string,
    enable_profiling=True,
    profiler_config={"sample_size": 10000}
)
```

## 🎯 Best Practices

### 1. **Choose the Right Mode**
- **Basic**: Simple queries, development
- **Enhanced**: Production use, complex queries
- **ReFoRCE**: Maximum accuracy, research applications

### 2. **Configure Safety Appropriately**
- Always enable validation in production
- Set appropriate row limits
- Block dangerous operations

### 3. **Optimize Profiling**
- Use appropriate sample sizes
- Enable LSH for large schemas
- Cache profiles for frequently used tables

### 4. **Monitor Performance**
- Track query execution times
- Monitor model API usage
- Set up alerts for failures

### 5. **Security Considerations**
- Use environment variables for secrets
- Implement proper access controls
- Audit query logs regularly
