# Ryoma SQL CLI

A command-line interface for natural language to SQL conversion with human-in-the-loop approval, similar to Claude Code but specialized for database interactions.

## Installation

```bash
pip install ryoma_ai
```

## Quick Start

```bash
# Start interactive mode
ryoma-sql

# Run interactive setup
ryoma-sql --setup

# Use specific model and mode
ryoma-sql --model gpt-4o --mode enhanced
```

## Features

- 🤖 **Natural Language to SQL** - Ask questions in plain English
- 👤 **Human-in-the-Loop Approval** - Review and approve queries before execution
- 🔍 **Schema Analysis** - Automatic database schema discovery
- 🛠️ **Error Recovery** - Intelligent SQL error correction
- 🎯 **Multiple Modes** - Basic, Enhanced, and ReFoRCE agent modes
- 🗄️ **Multi-Database Support** - PostgreSQL, MySQL, and more

## Usage

### Interactive Mode

Start the CLI and enter natural language questions:

```
ryoma-sql> What are the top 5 customers by total sales?
ryoma-sql> Show me all orders from last month
ryoma-sql> Find customers who haven't placed orders recently
```

### Commands

- `/help` - Show help information
- `/setup` - Interactive database setup
- `/config` - Show current configuration
- `/schema` - Display database schema
- `/mode <mode>` - Change agent mode (basic, enhanced, reforce)
- `/model <model>` - Change language model
- `/quit` or `/exit` - Exit the CLI

### Approval Workflow

When the agent generates SQL:

1. **Review**: SQL query is displayed for approval
2. **Choose**:
   - Type `approve` to execute
   - Type `deny` to reject
   - Or provide modified SQL to use instead

Example:
```
🔍 SQL Query for Approval
┌─────────────────────────────────────────────┐
│ SELECT customer_name, SUM(total_amount)     │
│ FROM customers c                            │
│ JOIN orders o ON c.id = o.customer_id       │
│ GROUP BY customer_name                      │
│ ORDER BY SUM(total_amount) DESC             │
│ LIMIT 5;                                    │
└─────────────────────────────────────────────┘

Options:
• Type approve to execute
• Type deny to reject
• Or provide modified SQL to use instead

Your decision: approve
```

## Configuration

Configuration is stored in `~/.ryoma/config.json`:

```json
{
  "model": "gpt-4o",
  "mode": "enhanced",
  "database": {
    "type": "postgres",
    "host": "localhost",
    "port": 5432,
    "database": "mydatabase",
    "user": "myuser",
    "password": "mypassword"
  }
}
```

### Environment Variables

You can use environment variables for database credentials:

- `POSTGRES_USER` - PostgreSQL username
- `POSTGRES_PASSWORD` - PostgreSQL password
- `MYSQL_USER` - MySQL username  
- `MYSQL_PASSWORD` - MySQL password

## Agent Modes

### Basic Mode
- Core SQL functionality
- Basic query generation
- No advanced features

### Enhanced Mode (Default)
- Multi-step reasoning
- Schema analysis and linking
- Safety validation
- Error recovery
- Human-in-the-loop approval

### ReFoRCE Mode
- State-of-the-art Text-to-SQL techniques
- Database information compression
- Format restriction
- Column exploration
- Parallel generation with consensus voting

## Examples

### Customer Analysis
```
ryoma-sql> Who are our top 10 customers by revenue this year?
```

### Sales Reporting  
```
ryoma-sql> Show me monthly sales trends for the last 6 months
```

### Inventory Management
```
ryoma-sql> Which products are running low in stock?
```

### Order Analysis
```
ryoma-sql> Find all orders that were shipped late last quarter
```

## Troubleshooting

### Database Connection Issues
1. Verify connection parameters with `/config`
2. Test connection manually
3. Run `/setup` for interactive configuration
4. Check firewall and network connectivity

### SQL Generation Issues
1. Try different agent modes (`/mode enhanced`)
2. Use `/schema` to verify table/column names
3. Provide more specific questions
4. Check database permissions

### Performance Issues
1. Use `basic` mode for simpler queries
2. Limit result sets in your questions
3. Consider database indexing
4. Use `reforce` mode for complex analytical queries

## Support

For issues and questions:
- GitHub Issues: [github.com/project-ryoma/ryoma](https://github.com/project-ryoma/ryoma)
- Documentation: [docs.ryoma-ai.com](https://docs.ryoma-ai.com)