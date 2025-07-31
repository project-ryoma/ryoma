# 🧠 Models

Ryoma supports multiple LLM providers and model configurations for different use cases and requirements.

## 🎯 Supported Providers

| 🏢 Provider | 🤖 Models | 🔧 Features |
|-------------|-----------|-------------|
| **OpenAI** | GPT-4, GPT-3.5-turbo | Function calling, streaming |
| **Anthropic** | Claude-3 Sonnet/Haiku | Large context, safety |
| **Local (Ollama)** | CodeLlama, Mistral | Privacy, cost control |
| **Azure OpenAI** | GPT-4, GPT-3.5 | Enterprise features |

## 🚀 Quick Start

### OpenAI Models
```python
from ryoma_ai.agent.sql import SqlAgent

# GPT-4 (recommended for production)
agent = SqlAgent(
    model="gpt-4",
    model_parameters={
        "temperature": 0.1,
        "max_tokens": 2000
    }
)

# GPT-3.5-turbo (cost-effective)
agent = SqlAgent(
    model="gpt-3.5-turbo",
    model_parameters={
        "temperature": 0.1,
        "max_tokens": 1500
    }
)
```

### Anthropic Claude
```python
# Claude-3 Sonnet (balanced performance)
agent = SqlAgent(
    model="claude-3-sonnet-20240229",
    model_parameters={
        "temperature": 0.1,
        "max_tokens": 4000
    }
)

# Claude-3 Haiku (fast and efficient)
agent = SqlAgent(
    model="claude-3-haiku-20240307",
    model_parameters={
        "temperature": 0.1,
        "max_tokens": 2000
    }
)
```

### Local Models (Ollama)
```python
from ryoma_ai.models.ollama import OllamaModel

# CodeLlama for SQL generation
model = OllamaModel(
    model_name="codellama:13b",
    base_url="http://localhost:11434"
)

agent = SqlAgent(model=model, mode="enhanced")
```

## ⚙️ Configuration

### Model Parameters

#### Temperature
Controls randomness in model outputs:
```python
# Conservative (recommended for SQL)
model_parameters = {"temperature": 0.1}

# Balanced
model_parameters = {"temperature": 0.3}

# Creative (not recommended for SQL)
model_parameters = {"temperature": 0.7}
```

#### Max Tokens
Controls maximum response length:
```python
# Simple queries
model_parameters = {"max_tokens": 1000}

# Complex analysis
model_parameters = {"max_tokens": 2000}

# Detailed explanations
model_parameters = {"max_tokens": 4000}
```

#### Advanced Parameters
```python
model_parameters = {
    "temperature": 0.1,
    "max_tokens": 2000,
    "top_p": 0.9,              # Nucleus sampling
    "frequency_penalty": 0.1,   # Reduce repetition
    "presence_penalty": 0.0,    # Encourage new topics
    "stop": ["```", "END"]      # Stop sequences
}
```

### Provider-Specific Configuration

#### OpenAI
```python
import os
from ryoma_ai.models.openai import OpenAIModel

# Set API key
os.environ["OPENAI_API_KEY"] = "your-api-key"

# Custom configuration
model = OpenAIModel(
    model_name="gpt-4",
    api_key="your-api-key",
    organization="your-org-id",
    base_url="https://api.openai.com/v1",  # Custom endpoint
    timeout=60,
    max_retries=3
)
```

#### Anthropic
```python
import os
from ryoma_ai.models.anthropic import AnthropicModel

# Set API key
os.environ["ANTHROPIC_API_KEY"] = "your-api-key"

# Custom configuration
model = AnthropicModel(
    model_name="claude-3-sonnet-20240229",
    api_key="your-api-key",
    timeout=60,
    max_retries=3
)
```

#### Azure OpenAI
```python
from ryoma_ai.models.azure_openai import AzureOpenAIModel

model = AzureOpenAIModel(
    deployment_name="gpt-4-deployment",
    api_key="your-azure-key",
    api_base="https://your-resource.openai.azure.com/",
    api_version="2024-02-01"
)
```

#### Ollama (Local)
```python
from ryoma_ai.models.ollama import OllamaModel

# Local Ollama instance
model = OllamaModel(
    model_name="codellama:13b",
    base_url="http://localhost:11434",
    timeout=120,  # Longer timeout for local models
    keep_alive="5m"  # Keep model loaded
)

# Remote Ollama instance
model = OllamaModel(
    model_name="mistral:7b",
    base_url="http://your-server:11434",
    headers={"Authorization": "Bearer your-token"}
)
```

## 🎯 Model Selection Guide

### By Use Case

#### Production SQL Generation
**Recommended**: GPT-4 or Claude-3 Sonnet
```python
agent = SqlAgent(
    model="gpt-4",
    mode="enhanced",
    model_parameters={"temperature": 0.1}
)
```

#### Development and Testing
**Recommended**: GPT-3.5-turbo or Claude-3 Haiku
```python
agent = SqlAgent(
    model="gpt-3.5-turbo",
    mode="basic",
    model_parameters={"temperature": 0.2}
)
```

#### Privacy-Sensitive Environments
**Recommended**: Local models via Ollama
```python
model = OllamaModel("codellama:13b")
agent = SqlAgent(model=model, mode="enhanced")
```

#### Cost-Optimized Deployment
**Recommended**: GPT-3.5-turbo with caching
```python
agent = SqlAgent(
    model="gpt-3.5-turbo",
    mode="enhanced",
    model_parameters={"temperature": 0.1},
    enable_caching=True
)
```

### By Performance Requirements

| 🎯 Requirement | 🥇 Best Choice | 🥈 Alternative |
|----------------|----------------|----------------|
| **Accuracy** | GPT-4 | Claude-3 Sonnet |
| **Speed** | GPT-3.5-turbo | Claude-3 Haiku |
| **Cost** | Local models | GPT-3.5-turbo |
| **Privacy** | Ollama | Azure OpenAI |
| **Context** | Claude-3 | GPT-4 |

## 🔧 Advanced Features

### Model Switching
```python
# Switch models based on query complexity
def get_model_for_complexity(complexity):
    if complexity == "high":
        return "gpt-4"
    elif complexity == "medium":
        return "gpt-3.5-turbo"
    else:
        return "claude-3-haiku-20240307"

# Dynamic model selection
query_plan = agent.get_query_plan(question)
model = get_model_for_complexity(query_plan["complexity"])
agent.set_model(model)
```

### Model Ensembling
```python
# Use multiple models for consensus
from ryoma_ai.models.ensemble import EnsembleModel

ensemble = EnsembleModel([
    "gpt-4",
    "claude-3-sonnet-20240229",
    "gpt-3.5-turbo"
])

agent = SqlAgent(
    model=ensemble,
    mode="reforce",  # Consensus voting
    ensemble_config={
        "voting_strategy": "majority",
        "confidence_threshold": 0.8
    }
)
```

### Caching and Optimization
```python
# Enable response caching
agent = SqlAgent(
    model="gpt-4",
    enable_caching=True,
    cache_config={
        "ttl": 3600,  # 1 hour
        "max_size": 1000,
        "cache_key_fields": ["question", "schema_hash"]
    }
)
```

## 📊 Performance Monitoring

### Track Model Usage
```python
from ryoma_ai.monitoring import ModelMonitor

monitor = ModelMonitor()

agent = SqlAgent(
    model="gpt-4",
    monitor=monitor
)

# Get usage statistics
stats = monitor.get_stats()
print(f"Total tokens: {stats['total_tokens']}")
print(f"Average latency: {stats['avg_latency']:.2f}s")
print(f"Cost estimate: ${stats['estimated_cost']:.2f}")
```

### A/B Testing Models
```python
from ryoma_ai.testing import ModelABTest

# Compare model performance
ab_test = ModelABTest(
    model_a="gpt-4",
    model_b="claude-3-sonnet-20240229",
    traffic_split=0.5
)

agent = SqlAgent(model=ab_test)

# Analyze results
results = ab_test.get_results()
print(f"Model A accuracy: {results['model_a']['accuracy']:.2%}")
print(f"Model B accuracy: {results['model_b']['accuracy']:.2%}")
```

## 🛡️ Security and Privacy

### API Key Management
```python
# Use environment variables
import os
os.environ["OPENAI_API_KEY"] = "your-key"

# Use key management service
from ryoma_ai.security import KeyManager

key_manager = KeyManager("aws-secrets-manager")
api_key = key_manager.get_key("openai-api-key")

model = OpenAIModel(api_key=api_key)
```

### Data Privacy
```python
# Local model for sensitive data
model = OllamaModel("codellama:13b")  # No data leaves your infrastructure

# Or use privacy-focused providers
model = AnthropicModel(
    model_name="claude-3-sonnet-20240229",
    privacy_mode=True  # Enhanced privacy settings
)
```

## 🎯 Best Practices

### 1. **Choose Models Appropriately**
- Use GPT-4 for complex analysis
- Use GPT-3.5-turbo for simple queries
- Use local models for sensitive data

### 2. **Optimize Parameters**
- Low temperature (0.1) for SQL generation
- Appropriate max_tokens for your use case
- Enable caching for repeated queries

### 3. **Monitor Performance**
- Track token usage and costs
- Monitor response latency
- A/B test different models

### 4. **Handle Failures Gracefully**
- Implement retry logic
- Have fallback models
- Log errors for debugging

### 5. **Security Considerations**
- Rotate API keys regularly
- Use environment variables
- Consider local models for sensitive data

```{toctree}
:maxdepth: 2

openai
anthropic
ollama
azure-openai
ensemble
```
