# CLI Usage Guide

Ryoma AI provides a powerful command-line interface for interactive data analysis with intelligent agent routing.

## 🚀 Starting the CLI

```bash
# Basic usage
ryoma_ai

# With custom model and mode
ryoma_ai --model gpt-4o --mode enhanced

# Override store configurations
ryoma_ai --vector-store-type chroma --meta-store-type memory

# Run interactive setup
ryoma_ai --setup
```

## 📋 Available Commands

### Core Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/help` | Show available commands | `/help` |
| `/quit` | Exit the CLI | `/quit` |
| `/config` | Display current configuration | `/config` |
| `/setup` | Run interactive setup | `/setup` |

### Data Source Management

| Command | Description | Example |
|---------|-------------|---------|
| `/datasources` | List all configured data sources | `/datasources` |
| `/switch-datasource <name>` | Switch to different data source | `/switch-datasource production` |
| `/add-datasource` | Add new data source interactively | `/add-datasource` |
| `/schema` | Show current database schema | `/schema` |

### Catalog Management

| Command | Description | Example |
|---------|-------------|---------|
| `/index-catalog [level]` | Index current data source for search | `/index-catalog table` |
| `/search-catalog <query>` | Search indexed catalogs | `/search-catalog customer data` |

### Agent Management

| Command | Description | Example |
|---------|-------------|---------|
| `/agents` | Show active agents and their stats | `/agents` |
| `/mode <mode>` | Change SQL agent mode | `/mode reforce` |
| `/model <model>` | Change language model | `/model gpt-4o` |
| `/stats` | Show agent usage statistics | `/stats` |

### Configuration

| Command | Description | Example |
|---------|-------------|---------|
| `/agent-config` | Show/modify agent settings | `/agent-config` |
| `/agent-config <setting> <value>` | Update agent setting | `/agent-config retry_count 5` |
| `/auto-approve [on/off]` | Toggle auto-approval | `/auto-approve on` |

## 🎯 Interactive Usage

The CLI features intelligent agent routing - just ask questions naturally:

```bash
ryoma_ai> show me all customers from California
# Routes to SQL Agent automatically

ryoma_ai> create a function to calculate fibonacci numbers  
# Routes to Python Agent automatically

ryoma_ai> analyze sales trends over the last 6 months
# Routes to Data Analysis Agent automatically

ryoma_ai> what's the difference between INNER and LEFT JOIN?
# Routes to Chat Agent automatically
```

## 🔧 Configuration Management

### View Current Configuration
```bash
ryoma_ai> /config
```

### Update Agent Settings
```bash
ryoma_ai> /agent-config auto_approve_all true
ryoma_ai> /agent-config retry_count 3
ryoma_ai> /agent-config timeout_seconds 300
```

### Switch Models and Modes
```bash
ryoma_ai> /model gpt-4o-mini
ryoma_ai> /mode basic
```

## 📊 Catalog Indexing and Search

### Index Your Data Source
```bash
# Index at table level (recommended)
ryoma_ai> /index-catalog table

# Index at column level for detailed search
ryoma_ai> /index-catalog column

# Index at schema level for high-level overview
ryoma_ai> /index-catalog schema
```

### Search Indexed Catalogs
```bash
ryoma_ai> /search-catalog customer information
ryoma_ai> /search-catalog sales revenue data
ryoma_ai> /search-catalog user authentication tables
```

## 🚀 Advanced Features

### Auto-completion
The CLI provides intelligent auto-completion for:
- Command names and parameters
- Data source names
- Agent types and modes
- Configuration keys

### Session Management
- Command history with search (`Ctrl+R`)
- Persistent configuration across sessions
- Agent state preservation
- Context sharing between agents

### Error Handling
- Graceful error recovery
- Helpful error messages
- Automatic retry mechanisms
- Fallback strategies

## ⚙️ Configuration File

The CLI uses `~/.ryoma/config.json` for persistence:

```json
{
  "model": "gpt-4o",
  "mode": "enhanced", 
  "embedding_model": "text-embedding-ada-002",
  "meta_store": {
    "type": "memory"
  },
  "vector_store": {
    "type": "chroma",
    "collection_name": "ryoma_vectors"
  },
  "datasources": [
    {
      "name": "default",
      "type": "postgres",
      "host": "localhost",
      "database": "mydb"
    }
  ],
  "agent": {
    "auto_approve_all": false,
    "retry_count": 3,
    "timeout_seconds": 300
  }
}
```

## 🔍 Troubleshooting

### Vector Store Issues
```bash
# Check if vector store is properly configured
ryoma_ai> /config

# Re-index if search fails
ryoma_ai> /index-catalog
```

### Connection Problems
```bash
# Run setup to reconfigure
ryoma_ai> /setup

# Check data source status
ryoma_ai> /datasources
```

### Agent Errors
```bash
# Check agent configuration
ryoma_ai> /agent-config

# View agent statistics
ryoma_ai> /stats
```