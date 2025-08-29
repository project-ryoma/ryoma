# 🏭 Agent Factory

The Agent Factory provides a unified interface for creating and managing all Ryoma agents with consistent configuration patterns.

## 🎯 Overview

The Agent Factory simplifies agent creation by providing a single entry point with built-in defaults and validation.

```python
from ryoma_ai.agent.factory import AgentFactory

# Create any agent type with consistent API
agent = AgentFactory.create_agent(
    agent_type="sql",
    model="gpt-4o",
    datasource=your_datasource,
    store=meta_store,
    vector_store=vector_store
)
```

## 🤖 Built-in Agent Types

### Available Agents
```python
from ryoma_ai.agent.factory import get_builtin_agents

# List all available agent types
agents = get_builtin_agents()
for agent in agents:
    print(f"{agent.name}: {agent.value.__name__}")
```

Output:
```
base: ChatAgent
sql: SqlAgent  
pandas: PandasAgent
pyarrow: ArrowAgent
pyspark: SparkAgent
python: PythonAgent
embedding: EmbeddingAgent
```

## 🚀 Agent Creation Patterns

### SQL Agent Factory
```python
# Create SQL agent with factory
sql_agent = AgentFactory.create_agent(
    agent_type="sql",
    model="gpt-4o",
    mode="enhanced",
    datasource=postgres_datasource,
    store=meta_store,
    vector_store=vector_store,
    safety_config={
        "enable_validation": True,
        "max_retries": 3
    }
)
```

### Python Agent Factory
```python
# Create Python agent
python_agent = AgentFactory.create_agent(
    agent_type="python", 
    model="gpt-4o",
    model_parameters={
        "temperature": 0.1,
        "max_tokens": 2000
    },
    store=meta_store,
    vector_store=vector_store
)
```

### Data Analysis Agent Factory
```python
# Create pandas agent for data analysis
data_agent = AgentFactory.create_agent(
    agent_type="pandas",
    model="gpt-4o", 
    datasource=datasource,
    store=meta_store,
    vector_store=vector_store,
    enable_visualization=True
)
```

### Chat Agent Factory
```python
# Create conversational agent
chat_agent = AgentFactory.create_agent(
    agent_type="base",  # Maps to ChatAgent
    model="gpt-4o",
    model_parameters={
        "temperature": 0.7  # More creative for conversations
    },
    store=meta_store,
    vector_store=vector_store
)
```

## ⚙️ Configuration Management

### Default Configuration
```python
# Factory applies sensible defaults
agent = AgentFactory.create_agent(
    agent_type="sql",
    model="gpt-4o"
    # Defaults applied:
    # - mode: "enhanced" 
    # - temperature: 0.1
    # - max_tokens: 2000
    # - safety_config: basic validation enabled
)
```

### Configuration Override
```python
# Override defaults as needed
agent = AgentFactory.create_agent(
    agent_type="sql",
    model="gpt-4o",
    mode="reforce",  # Override default mode
    model_parameters={
        "temperature": 0.0,  # Override default temperature
        "max_tokens": 4000   # Override default max_tokens
    }
)
```

## 🏗️ Advanced Factory Patterns

### Batch Agent Creation
```python
# Create multiple agents with shared configuration
def create_agent_suite(base_config):
    agents = {}
    
    for agent_type in ["sql", "python", "pandas", "chat"]:
        agents[agent_type] = AgentFactory.create_agent(
            agent_type=agent_type,
            **base_config
        )
    
    return agents

# Create full agent suite
agents = create_agent_suite({
    "model": "gpt-4o",
    "datasource": datasource,
    "store": meta_store,
    "vector_store": vector_store
})
```

### Configuration Builder Pattern
```python
class AgentConfigBuilder:
    def __init__(self):
        self.config = {}
    
    def model(self, model_name):
        self.config["model"] = model_name
        return self
    
    def datasource(self, ds):
        self.config["datasource"] = ds
        return self
        
    def stores(self, meta_store, vector_store):
        self.config["store"] = meta_store
        self.config["vector_store"] = vector_store
        return self
    
    def safety(self, **safety_config):
        self.config["safety_config"] = safety_config
        return self
    
    def build(self, agent_type):
        return AgentFactory.create_agent(agent_type, **self.config)

# Usage
builder = AgentConfigBuilder()
agent = (builder
    .model("gpt-4o")
    .datasource(datasource)
    .stores(meta_store, vector_store)
    .safety(enable_validation=True, max_retries=3)
    .build("sql")
)
```

### Environment-Based Factory
```python
import os

class EnvironmentAgentFactory:
    @staticmethod
    def create_production_agent(agent_type, **overrides):
        """Create agent optimized for production."""
        config = {
            "model": "gpt-4o",
            "model_parameters": {
                "temperature": 0.1,
                "max_tokens": 2000
            },
            "safety_config": {
                "enable_validation": True,
                "max_retries": 3,
                "allowed_operations": ["SELECT", "WITH"]
            }
        }
        config.update(overrides)
        return AgentFactory.create_agent(agent_type, **config)
    
    @staticmethod  
    def create_development_agent(agent_type, **overrides):
        """Create agent optimized for development."""
        config = {
            "model": "gpt-3.5-turbo",
            "model_parameters": {
                "temperature": 0.2,
                "max_tokens": 1500
            },
            "safety_config": {
                "enable_validation": False  # More permissive
            }
        }
        config.update(overrides)
        return AgentFactory.create_agent(agent_type, **config)

# Usage
if os.getenv("ENVIRONMENT") == "production":
    agent = EnvironmentAgentFactory.create_production_agent("sql")
else:
    agent = EnvironmentAgentFactory.create_development_agent("sql")
```

## 🔄 Factory Integration

### With Multi-Agent Router
```python
from ryoma_ai.agent.multi_agent_router import MultiAgentRouter

class AdvancedRouter(MultiAgentRouter):
    def _create_agent(self, agent_type, **config_overrides):
        """Override to use factory pattern."""
        base_config = {
            "model": self.model,
            "datasource": self.datasource,
            "store": self.meta_store,
            "vector_store": self.vector_store
        }
        base_config.update(config_overrides)
        
        return AgentFactory.create_agent(agent_type, **base_config)
```

### With CLI Integration
```python
# CLI can use factory for consistent agent creation
class CLIAgentManager:
    def __init__(self, config):
        self.config = config
        
    def create_agent_for_command(self, command_type):
        # Map CLI commands to agent types
        command_to_agent = {
            "query": "sql",
            "analyze": "pandas", 
            "code": "python",
            "chat": "base"
        }
        
        agent_type = command_to_agent.get(command_type, "base")
        return AgentFactory.create_agent(
            agent_type=agent_type,
            **self.config
        )
```

## 🎯 Error Handling

### Invalid Agent Types
```python
# Factory handles invalid types gracefully
agent = AgentFactory.create_agent(
    agent_type="invalid_type",  # Fallback to ChatAgent
    model="gpt-4o"
)
print(type(agent).__name__)  # "ChatAgent"
```

### Configuration Validation
```python
try:
    agent = AgentFactory.create_agent(
        agent_type="sql",
        model="invalid-model"
    )
except ValueError as e:
    print(f"Configuration error: {e}")
```

## 🛡️ Best Practices

### 1. **Use Factory for Consistency**
- Always use factory for agent creation
- Avoid directly instantiating agent classes
- Leverage built-in defaults and validation

### 2. **Configure Appropriately**
- Use production-ready configurations
- Set appropriate safety limits
- Configure stores correctly

### 3. **Handle Errors Gracefully**
- Implement fallback strategies
- Validate configuration before creation
- Monitor agent creation success rates

### 4. **Optimize Performance**
- Cache agent instances when possible
- Use lazy initialization for expensive resources
- Monitor resource usage

## 🔗 Related Documentation

- **[Multi-Agent Router](router.md)** - Intelligent routing system
- **[Store Architecture](../../architecture/store-architecture.md)** - Unified storage
- **[Models](../models/index.md)** - Model configuration
- **[CLI Usage](../../getting-started/cli-usage.md)** - Command-line interface