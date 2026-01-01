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

### Local Models (GPT4All)
```python
from ryoma_ai.llm.provider import load_model_provider

# CodeLlama or other GPT4All models
model = load_model_provider(
    model_id="gpt4all:orca-mini-3b.gguf",
    model_type="chat",
    model_parameters={"allow_download": True}
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

All model providers are loaded through the unified `load_model_provider` function from `ryoma_ai.llm.provider`.

#### OpenAI
```python
import os
from ryoma_ai.llm.provider import load_model_provider

# Set API key
os.environ["OPENAI_API_KEY"] = "your-api-key"

# Load OpenAI chat model
chat_model = load_model_provider(
    model_id="openai:gpt-4",  # or just "gpt-4"
    model_type="chat",
    model_parameters={
        "temperature": 0.1,
        "max_tokens": 2000
    }
)

# Load OpenAI embedding model
embedding_model = load_model_provider(
    model_id="openai:text-embedding-ada-002",
    model_type="embedding"
)
```

#### Anthropic
```python
import os
from ryoma_ai.llm.provider import load_model_provider

# Set API key
os.environ["ANTHROPIC_API_KEY"] = "your-api-key"

# Load Anthropic chat model
model = load_model_provider(
    model_id="anthropic:claude-3-sonnet-20240229",
    model_type="chat",
    model_parameters={
        "temperature": 0.1,
        "max_tokens": 4000
    }
)
```

#### Azure OpenAI
```python
from ryoma_ai.llm.provider import load_model_provider

# Set environment variables for Azure
import os
os.environ["AZURE_OPENAI_API_KEY"] = "your-azure-key"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://your-resource.openai.azure.com/"

# Load Azure OpenAI model
model = load_model_provider(
    model_id="azure-chat-openai:gpt-4",
    model_type="chat",
    model_parameters={
        "temperature": 0.1
    }
)
```

#### Google Gemini
```python
import os
from ryoma_ai.llm.provider import load_model_provider

# Set API key
os.environ["GOOGLE_API_KEY"] = "your-google-api-key"

# Load Google Gemini model
model = load_model_provider(
    model_id="google:gemini-pro",  # or "gemini:gemini-pro"
    model_type="chat",
    model_parameters={
        "temperature": 0.1,
        "max_tokens": 2000
    }
)
```

#### GPT4All (Local)
```python
from ryoma_ai.llm.provider import load_model_provider

# Load GPT4All local model
model = load_model_provider(
    model_id="gpt4all:orca-mini-3b.gguf",
    model_type="chat",
    model_parameters={
        "allow_download": True,  # Auto-download if not present
        "temperature": 0.1
    }
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
**Recommended**: Local models via GPT4All
```python
from ryoma_ai.llm.provider import load_model_provider

model = load_model_provider(
    model_id="gpt4all:orca-mini-3b.gguf",
    model_type="chat",
    model_parameters={"allow_download": True}
)
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
# Use environment variables (recommended)
import os
os.environ["OPENAI_API_KEY"] = "your-key"
os.environ["ANTHROPIC_API_KEY"] = "your-key"

# Models will automatically use environment variables
from ryoma_ai.llm.provider import load_model_provider

model = load_model_provider(
    model_id="openai:gpt-4",
    model_type="chat"
)
```

### Data Privacy
```python
# Use local models for sensitive data (no data leaves your infrastructure)
from ryoma_ai.llm.provider import load_model_provider

local_model = load_model_provider(
    model_id="gpt4all:orca-mini-3b.gguf",
    model_type="chat",
    model_parameters={"allow_download": True}
)

# Or use Azure OpenAI for enterprise privacy requirements
azure_model = load_model_provider(
    model_id="azure-chat-openai:gpt-4",
    model_type="chat"
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
