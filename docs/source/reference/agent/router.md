# 🧠 Multi-Agent Router

The Multi-Agent Router intelligently routes user questions to the most appropriate specialized agent using LLM-based intent classification.

## 🎯 Overview

Instead of manually choosing which agent to use, the router automatically analyzes your question and selects the optimal agent for the task.

```python
from ryoma_ai.agent.multi_agent_router import MultiAgentRouter

# Create router with unified stores
router = MultiAgentRouter(
    model="gpt-4o",
    datasource=your_datasource,
    meta_store=meta_store,
    vector_store=vector_store
)

# Just ask naturally - routing is automatic
agent, classification, context = router.route_and_execute(
    "Show me the top 10 customers by revenue this quarter"
)
# → Automatically routes to SQL Agent
```

## 🤖 Agent Types

### 1. **SQL Agent** (`sql_query`)
Handles database queries and data retrieval.

**Triggers:**
- Questions about data in databases
- Database exploration requests
- Data filtering and aggregation

**Examples:**
```bash
"Show me all customers from California"
"What are the top selling products?"
"Find orders placed last month"
"Describe the users table structure"
```

### 2. **Python Agent** (`python_code`)
Executes Python code and scripts.

**Triggers:**
- Python code requests
- Algorithm implementation
- Script creation needs

**Examples:**
```bash
"Write a function to calculate fibonacci numbers"
"Create a script to process CSV files"
"Python code to send HTTP requests"
"Implement a binary search algorithm"
```

### 3. **Data Analysis Agent** (`data_analysis`) 
Performs statistical analysis and visualization.

**Triggers:**
- Statistical analysis requests
- Data visualization needs
- Trend analysis questions

**Examples:**
```bash
"Analyze sales trends over the last year"
"Create a correlation matrix of these variables"
"Plot the distribution of customer ages"
"Calculate statistical significance of A/B test"
```

### 4. **Chat Agent** (`general_chat`)
Handles conversations and general questions.

**Triggers:**
- General knowledge questions
- Help and explanations
- Conceptual discussions

**Examples:**
```bash
"What are database best practices?"
"Explain how machine learning works"
"What can you help me with?"
"How do I improve query performance?"
```

## ⚙️ Configuration

### Basic Setup
```python
from ryoma_ai.agent.multi_agent_router import MultiAgentRouter

router = MultiAgentRouter(
    model="gpt-4o",                    # Model for routing decisions
    datasource=postgres_datasource,    # Primary data source
    meta_store=unified_meta_store,     # Metadata storage
    vector_store=unified_vector_store, # Vector storage
    model_parameters={
        "temperature": 0.3  # Balanced for routing decisions
    }
)
```

### Custom Agent Configuration
```python
# Route with agent-specific overrides
agent, classification, context = router.route_and_execute(
    "Analyze customer churn patterns",
    sql_mode="reforce",  # Override SQL agent mode
    enable_visualization=True  # Override analysis options
)
```

## 🔍 Classification System

### LLM-Based Intent Recognition
The router uses advanced LLM inference to understand user intent:

```python
from ryoma_ai.agent.multi_agent_router import LLMTaskRouter

# Create classifier
classifier = LLMTaskRouter(model="gpt-4o")

# Get classification details
classification = classifier.classify_task(
    "Show me sales trends for Q4 and create a visualization"
)

print(f"Task Type: {classification.task_type}")
print(f"Confidence: {classification.confidence:.2f}")
print(f"Reasoning: {classification.reasoning}")
print(f"Agent: {classification.suggested_agent}")
```

### Classification Output
```python
TaskClassification(
    task_type=TaskType.DATA_ANALYSIS,
    confidence=0.95,
    reasoning="Request involves both data retrieval and visualization creation",
    suggested_agent="pandas"
)
```

## 📊 Agent Management

### Lazy Agent Initialization
Agents are created on-demand for optimal performance:

```python
# Agents created only when needed
sql_agent = router.get_agent("sql")           # Creates SqlAgent
python_agent = router.get_agent("python")     # Creates PythonAgent
data_agent = router.get_agent("pandas")       # Creates PandasAgent
chat_agent = router.get_agent("chat")         # Creates ChatAgent
```

### Agent Caching
```python
# Agents are cached for reuse
agent1 = router.get_agent("sql")  # Creates new SqlAgent
agent2 = router.get_agent("sql")  # Returns cached SqlAgent
assert agent1 is agent2  # Same instance
```

### Custom Agent Config
```python
# Override default configuration per agent
sql_agent = router.get_agent("sql", mode="reforce")
python_agent = router.get_agent("python", enable_plotting=True)
```

## 🔄 Context Management

### Execution Context
The router maintains shared context across all agents:

```python
# Access shared execution context
context = router.execution_context

# View conversation history
print("Recent queries:")
for entry in context["conversation_history"][-5:]:
    print(f"  {entry['input']} → {entry['agent_type']}")

# Access shared variables
shared_data = context["shared_variables"]
current_ds = context["current_datasource"]
```

### Context Switching
```python
# Switch between agents with context preservation
router.switch_agent_context(
    from_agent="sql",
    to_agent="pandas", 
    context_data={
        "query_results": sql_results,
        "table_schema": table_info,
        "user_preference": "detailed_analysis"
    }
)
```

## 📈 Usage Statistics

### Agent Usage Tracking
```python
# Get router statistics
stats = router.get_current_stats()

print(f"Total queries: {stats['total_queries']}")
print(f"Agent usage: {stats['agent_usage']}")
print(f"Active agents: {stats['active_agents']}")
```

### Example Output
```python
{
    'total_queries': 25,
    'agent_usage': {
        'sql': 15,      # 60% SQL queries  
        'pandas': 6,    # 24% Data analysis
        'chat': 3,      # 12% General questions
        'python': 1     # 4% Code requests
    },
    'active_agents': ['sql_enhanced', 'pandas_default', 'chat_default']
}
```

## 🎯 Routing Examples

### Automatic Classification
```python
# Database query → SQL Agent
router.route_and_execute("Show me customers who haven't ordered in 30 days")

# Algorithm request → Python Agent  
router.route_and_execute("Write a function to validate email addresses")

# Analysis request → Data Analysis Agent
router.route_and_execute("Calculate correlation between price and sales volume")

# General question → Chat Agent
router.route_and_execute("What are the benefits of using database indexes?")
```

### Complex Multi-Agent Workflows
```python
# Router handles complex requests intelligently
user_input = """
First explain what customer lifetime value means,
then calculate it for our top 10 customers,
and create a visualization of the results
"""

# Router automatically breaks this down:
# 1. Chat Agent: Explains CLV concept
# 2. SQL Agent: Retrieves customer data
# 3. Data Analysis Agent: Calculates CLV and creates visualization
agent, classification, context = router.route_and_execute(user_input)
```

## 🛡️ Routing Accuracy

### Confidence Scoring
```python
# Monitor routing confidence
agent, classification, context = router.route_and_execute(user_input)

if classification.confidence < 0.7:
    print(f"Low confidence routing: {classification.reasoning}")
    print("Consider rephrasing your question for better routing")
```

### Fallback Handling
```python
# Configure fallback behavior
router = MultiAgentRouter(
    model="gpt-4o",
    fallback_agent="chat",  # Default to chat for ambiguous queries
    min_confidence=0.6      # Require minimum confidence
)
```

## 🔧 Capabilities Overview

### Get Router Capabilities
```python
# View all agent capabilities
capabilities = router.get_capabilities()

for agent_name, info in capabilities.items():
    print(f"\n{agent_name}:")
    print(f"  Capabilities: {info['capabilities']}")
    print(f"  Examples: {info['examples']}")
```

### Dynamic Agent Selection
```python
# Smart routing based on context
def smart_route(question, context=None):
    if context and "database" in context:
        return router.get_agent("sql")
    elif context and "visualization" in context:
        return router.get_agent("pandas")
    else:
        # Use automatic classification
        agent, _, _ = router.route_and_execute(question)
        return agent
```

## 🎯 Best Practices

### 1. **Question Clarity**
- Be specific about your intent
- Include relevant context
- Use keywords that indicate the type of task

### 2. **Context Management**
- Leverage conversation history
- Provide domain-specific context when needed
- Use context switching for complex workflows

### 3. **Performance Optimization**
- Cache frequently used agents
- Monitor routing accuracy
- Use appropriate confidence thresholds

### 4. **Error Handling**
- Handle low-confidence classifications
- Implement fallback strategies
- Monitor agent performance

## 🔗 Related Documentation

- **[SQL Agent](sql.md)** - Database query agent
- **[Python Agent](python.md)** - Code execution agent  
- **[Pandas Agent](pandas.md)** - Data analysis agent
- **[Store Architecture](../../architecture/store-architecture.md)** - Unified storage system