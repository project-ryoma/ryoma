# 🔧 Advanced Setup

This guide covers advanced configuration options and production deployment strategies for Ryoma.

## 🎯 Agent Modes

Ryoma offers different agent modes optimized for various use cases:

### Basic Mode (Simple Queries)
```python
from ryoma_ai import Ryoma
from ryoma_data import DataSource

datasource = DataSource("postgres", host="localhost", database="mydb", user="user", password="password")
ryoma = Ryoma(datasource=datasource)

# Basic mode - fast, simple SQL generation
agent = ryoma.sql_agent(model="gpt-4", mode="basic")
```

### Enhanced Mode (Recommended)
```python
# Enhanced mode - multi-step reasoning with safety validation
agent = ryoma.sql_agent(model="gpt-4", mode="enhanced")
```

**Features:**
- ✅ Advanced schema linking
- ✅ Query planning and optimization
- ✅ Safety validation
- ✅ Error handling with retry logic
- ✅ Comprehensive logging

### ReFoRCE Mode (State-of-the-Art)
```python
# ReFoRCE mode - research-based optimizations for maximum accuracy
agent = ryoma.sql_agent(model="gpt-4", mode="reforce")
```

**Features:**
- 🚀 Self-refinement workflow
- 🚀 Format restriction generation
- 🚀 Column exploration with feedback
- 🚀 Parallel SQL generation
- 🚀 Majority-vote consensus

## 🗄️ Database Configuration

### PostgreSQL
```python
from ryoma_ai import Ryoma
from ryoma_data import DataSource

datasource = DataSource(
    "postgres",
    connection_string="postgresql://user:pass@host:5432/db"
)
ryoma = Ryoma(datasource=datasource)
```

### Snowflake
```python
from ryoma_ai import Ryoma
from ryoma_data import DataSource

datasource = DataSource(
    "snowflake",
    account="your-account",
    user="your-user",
    password="your-password",
    database="your-database",
    warehouse="your-warehouse"
)
ryoma = Ryoma(datasource=datasource)
```

### BigQuery
```python
from ryoma_ai import Ryoma
from ryoma_data import DataSource

datasource = DataSource(
    "bigquery",
    project_id="your-project",
    credentials_path="/path/to/service-account.json"
)
ryoma = Ryoma(datasource=datasource)
```

### Multiple Datasources
```python
from ryoma_ai import Ryoma
from ryoma_data import DataSource

ryoma = Ryoma()

# Add multiple databases
ryoma.add_datasource(
    DataSource("postgres", host="localhost", database="sales", user="user", password="pass"),
    name="sales"
)
ryoma.add_datasource(
    DataSource("snowflake", account="acc", database="ANALYTICS", user="user", password="pass"),
    name="analytics"
)

# Create agent and switch between datasources
agent = ryoma.sql_agent(model="gpt-4", mode="enhanced")
ryoma.set_active("analytics")
```

### Database Profiling
```python
from ryoma_data import DataSource, DatabaseProfiler

datasource = DataSource("postgres", connection_string="postgresql://...")

# Configure profiler
profiler = DatabaseProfiler(
    sample_size=10000,
    top_k=10,
    enable_lsh=True
)

# Profile tables
profile = profiler.profile_table(datasource, "customers")
```

## 🛡️ Security Configuration

### Safety Validation
```python
from ryoma_ai import Ryoma
from ryoma_data import DataSource

datasource = DataSource("postgres", host="localhost", database="mydb", user="user", password="pass")
ryoma = Ryoma(datasource=datasource)

# Enhanced mode includes safety validation by default
agent = ryoma.sql_agent(model="gpt-4", mode="enhanced")

# The agent's safety features include:
# - Query validation before execution
# - Blocked dangerous operations (DROP, DELETE, UPDATE, INSERT, TRUNCATE)
# - Resource limits and timeouts
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
from ryoma_ai import Ryoma
from ryoma_data import DataSource

datasource = DataSource("postgres", host="localhost", database="mydb", user="user", password="pass")
ryoma = Ryoma(datasource=datasource)

# Use GPT-4 with custom parameters
agent = ryoma.sql_agent(
    model="gpt-4",
    mode="enhanced"
)
```

### Anthropic Claude
```python
# Use Claude models
agent = ryoma.sql_agent(
    model="claude-3-sonnet-20240229",
    mode="enhanced"
)
```

### Local Models (GPT4All)
```python
from ryoma_ai import Ryoma
from ryoma_ai.llm.provider import load_model_provider
from ryoma_data import DataSource

# Load local model
model = load_model_provider(
    model_id="gpt4all:codellama-13b.gguf",
    model_type="chat",
    model_parameters={"allow_download": True}
)

datasource = DataSource("postgres", host="localhost", database="mydb", user="user", password="pass")
ryoma = Ryoma(datasource=datasource)

# Use local model with Ryoma
agent = ryoma.sql_agent(model=model, mode="enhanced")
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
