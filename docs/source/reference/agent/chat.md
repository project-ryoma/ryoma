# 💬 ChatAgent

The ChatAgent is Ryoma's conversational AI agent for general questions, explanations, and knowledge sharing. It provides intelligent responses using advanced language models.

## 🎯 Core Capabilities

### 🗣️ **Conversational AI**
- Natural language understanding and generation
- Context-aware responses
- Multi-turn conversations with memory
- Intelligent question routing

### 📚 **Knowledge Sharing**
- Technical explanations and tutorials
- Best practices and recommendations
- Conceptual discussions
- Help and guidance

### 🔗 **Context Integration**
- Vector store integration for knowledge retrieval
- Conversation history management
- Shared context across agent interactions

## 🚀 Quick Start

```python
from ryoma_ai.agent.chat_agent import ChatAgent

# Basic chat agent
agent = ChatAgent(
    model="gpt-4o",
    model_parameters={
        "temperature": 0.7,  # More creative for conversations
        "max_tokens": 2000
    }
)

# Ask general questions
response = agent.stream("What are the best practices for database design?")
print(response)
```

## 🔧 Advanced Configuration

### Custom Prompts
```python
from langchain_core.prompts import ChatPromptTemplate

# Custom base prompt
custom_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful data engineering expert."),
    ("human", "{question}")
])

agent = ChatAgent(
    model="gpt-4o",
    base_prompt_template=custom_prompt
)
```

### Vector Store Integration
```python
# Chat agent with knowledge retrieval
agent = ChatAgent(
    model="gpt-4o",
    vector_store=vector_store_config,
    embedding=embedding_config
)

# Questions can now leverage indexed knowledge
response = agent.stream("How do I optimize SQL queries for large datasets?")
```

## 📊 Methods

### Core Methods

#### `stream(question: str, display: bool = True)`
Stream conversational responses in real-time.

```python
# Stream response
agent.stream("Explain the difference between OLTP and OLAP systems")

# Stream without display
response = agent.stream("What is data normalization?", display=False)
```

#### `invoke(question: str, display: bool = True)`
Get complete response at once.

```python
# Get full response
response = agent.invoke("How do database indexes work?")
print(response.content)
```

#### `chat(question: str, display: bool = True, stream: bool = False)`
Unified interface for both streaming and invoke modes.

```python
# Use chat interface
agent.chat("What are the benefits of using vector databases?", stream=True)
```

### Advanced Methods

#### `add_prompt(prompt)`
Add context to the conversation.

```python
# Add domain-specific context
agent.add_prompt("""
You are an expert in financial data analysis.
Focus on accounting principles and regulatory compliance.
""")

response = agent.stream("How should I structure my customer revenue tables?")
```

#### `set_base_prompt(prompt)`
Replace the base prompt template.

```python
from langchain_core.prompts import ChatPromptTemplate

# Technical documentation assistant
tech_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a technical documentation expert. Provide clear, actionable answers."),
    ("human", "{question}")
])

agent.set_base_prompt(tech_prompt)
```

#### `set_output_parser(parser)`
Structure responses using Pydantic models.

```python
from pydantic import BaseModel

class TechnicalAnswer(BaseModel):
    concept: str
    explanation: str
    examples: list[str]
    best_practices: list[str]

agent.set_output_parser(TechnicalAnswer)
response = agent.invoke("Explain database indexing")
print(f"Concept: {response.concept}")
```

## 🎨 Use Cases

### 1. **Technical Help and Guidance**
```python
# Get technical explanations
agent.stream("What's the difference between clustered and non-clustered indexes?")
agent.stream("When should I use a data warehouse vs data lake?")
```

### 2. **Best Practices Consultation**
```python
# Ask for recommendations
agent.stream("What are the security best practices for database connections?")
agent.stream("How should I structure my data pipeline architecture?")
```

### 3. **Learning and Education**
```python
# Educational content
agent.stream("Explain how database transactions work")
agent.stream("What are the ACID properties and why are they important?")
```

### 4. **Troubleshooting Support**
```python
# Get help with issues
agent.stream("My PostgreSQL queries are running slowly, what could be wrong?")
agent.stream("How do I debug connection timeout errors?")
```

## 🔍 Integration with Other Agents

### Multi-Agent Workflows
The ChatAgent works seamlessly with other agents through the router:

```python
from ryoma_ai.agent.multi_agent_router import MultiAgentRouter

router = MultiAgentRouter(
    model="gpt-4o",
    datasource=your_datasource,
    meta_store=meta_store,
    vector_store=vector_store
)

# Natural routing between agents
agent, classification, context = router.route_and_execute(
    "First explain how joins work, then show me all orders with customer names"
)
# → Routes to ChatAgent for explanation, then SqlAgent for query
```

### Context Sharing
```python
# Share context between agent types
router.switch_agent_context(
    from_agent="chat",
    to_agent="sql",
    context_data={
        "previous_explanation": "User learned about joins",
        "complexity_level": "beginner"
    }
)
```

## 🛡️ Safety and Validation

### Content Filtering
```python
# Configure content policies
agent = ChatAgent(
    model="gpt-4o",
    safety_config={
        "enable_content_filter": True,
        "block_sensitive_info": True,
        "require_data_context": False
    }
)
```

### Response Validation
```python
# Validate responses for technical accuracy
agent = ChatAgent(
    model="gpt-4o",
    validation_config={
        "enable_fact_checking": True,
        "cross_reference_sources": True,
        "confidence_threshold": 0.8
    }
)
```

## 📈 Performance Optimization

### Caching Responses
```python
# Enable response caching for common questions
agent = ChatAgent(
    model="gpt-4o",
    enable_caching=True,
    cache_config={
        "ttl": 3600,  # 1 hour
        "cache_key_fields": ["question", "base_prompt"]
    }
)
```

### Model Optimization
```python
# Optimize for conversation flow
agent = ChatAgent(
    model="gpt-4o",
    model_parameters={
        "temperature": 0.7,        # Creative but consistent
        "max_tokens": 1500,        # Reasonable response length
        "presence_penalty": 0.1,   # Encourage topic variation
        "frequency_penalty": 0.1   # Reduce repetition
    }
)
```

## 🔗 Related Documentation

- **[Multi-Agent Router](router.md)** - Intelligent agent routing
- **[SQL Agent](sql.md)** - Database query agent
- **[Python Agent](python.md)** - Code execution agent
- **[Models](../models/index.md)** - Model configuration