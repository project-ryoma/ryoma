"""
Display Manager for Ryoma AI CLI

Handles all display and UI formatting logic.
"""

import json
from typing import Dict, Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.markdown import Markdown


class DisplayManager:
    """Manages display and UI formatting for the CLI."""

    def __init__(self, console: Console):
        """
        Initialize the display manager.

        Args:
            console: Rich console for output
        """
        self.console = console

    def show_banner(self, config: Dict[str, Any]) -> None:
        """
        Display the CLI banner with system information.

        Args:
            config: Configuration dictionary
        """
        banner = """
🤖 Ryoma AI Multi-Agent System
Natural Language ➜ Intelligent Agent Routing ➜ Results
        """

        info_table = Table(show_header=False, box=None)
        info_table.add_row("Model:", config.get("model", "gpt-4o"))
        info_table.add_row("Mode:", config.get("mode", "enhanced"))

        db_config = config.get("database", {})
        if db_config:
            if "password" in db_config:
                db_config["password"] = "***"
            info_table.add_row("Database:", str(db_config))

        self.console.print(Panel(banner, style="bold blue"))
        self.console.print(info_table)
        self.console.print()

    def show_help(self) -> None:
        """Display help information."""
        help_text = """
## Commands:
- **Ask questions**: Type natural language questions - the system will route to the best agent
- **/help**: Show this help message
- **/config**: Show current configuration
- **/setup**: Setup database connection
- **/agents**: Show available agents and their capabilities
- **/stats**: Show agent usage statistics
- **/model <model>**: Change language model
- **/schema**: Show database schema
- **/quit** or **/exit**: Exit the CLI

## Data Source Management:
- **/datasources**: Show all registered data sources
- **/add-datasource**: Add a new data source interactively
- **/switch-datasource [id]**: Switch to a different data source
- **/index-catalog [datasource_id] [level]**: Index catalog for search
- **/search-catalog <query>**: Search indexed catalogs

## Available Agents:
- **SQL Agent**: Database queries and data retrieval
- **Python Agent**: Python code execution and scripts
- **Data Analysis Agent**: Advanced data analysis with pandas
- **Chat Agent**: General questions and explanations

## Examples:
- "Show me the top 5 customers by sales" → SQL Agent
- "Write a function to calculate fibonacci" → Python Agent
- "Analyze the sales trends in this data" → Data Analysis Agent
- "Explain machine learning concepts" → Chat Agent

## Approval Workflow:
- System routes to appropriate agent automatically
- SQL operations require approval for safety
- Type **approve** to execute, **deny** to reject
        """

        self.console.print(Panel(Markdown(help_text), title="Ryoma Multi-Agent Help", style="green"))

    def show_config(self, config: Dict[str, Any]) -> None:
        """
        Show current configuration.

        Args:
            config: Configuration dictionary to display
        """
        config_text = json.dumps(config, indent=2)
        syntax = Syntax(config_text, "json", theme="monokai", line_numbers=True)
        self.console.print(Panel(syntax, title="Current Configuration"))

    def show_schema(self, datasource) -> None:
        """
        Show database schema.

        Args:
            datasource: Current data source instance
        """
        if not datasource:
            self.console.print("[red]No database connection[/red]")
            return

        try:
            catalog = datasource.get_catalog()

            for schema in catalog.schemas:
                schema_table = Table(title=f"Schema: {schema.schema_name}")
                schema_table.add_column("Table", style="cyan")
                schema_table.add_column("Columns", style="green")

                for table in schema.tables:
                    columns = ", ".join([f"{col.name}({col.type})" for col in table.columns[:5]])
                    if len(table.columns) > 5:
                        columns += f" ... (+{len(table.columns) - 5} more)"
                    schema_table.add_row(table.table_name, columns)

                self.console.print(schema_table)

        except Exception as e:
            self.console.print(f"[red]Failed to retrieve schema: {e}[/red]")

    def show_search_results(self, query: str, results: list) -> None:
        """
        Display catalog search results.

        Args:
            query: Search query
            results: List of search results
        """
        if not results:
            self.console.print("[yellow]No search results found[/yellow]")
            return

        search_table = Table(title=f"🔍 Search Results for: '{query}'")
        search_table.add_column("Score", style="cyan")
        search_table.add_column("Type", style="green")
        search_table.add_column("Content", style="white")

        for result in results:
            metadata = result['metadata']
            content = result['content'][:100] + "..." if len(result['content']) > 100 else result['content']
            score = f"{result['score']:.3f}"

            search_table.add_row(score, metadata.get('type', 'unknown'), content)

        self.console.print(search_table)

    def show_error(self, message: str, details: str = None) -> None:
        """
        Display error message.

        Args:
            message: Error message
            details: Optional error details
        """
        if details:
            self.console.print(f"[red]{message}[/red]")
            self.console.print(f"[red]Details: {details}[/red]")
        else:
            self.console.print(f"[red]{message}[/red]")

    def show_success(self, message: str) -> None:
        """
        Display success message.

        Args:
            message: Success message
        """
        self.console.print(f"[green]{message}[/green]")

    def show_warning(self, message: str) -> None:
        """
        Display warning message.

        Args:
            message: Warning message
        """
        self.console.print(f"[yellow]{message}[/yellow]")

    def show_info(self, message: str) -> None:
        """
        Display info message.

        Args:
            message: Info message
        """
        self.console.print(f"[cyan]{message}[/cyan]")
