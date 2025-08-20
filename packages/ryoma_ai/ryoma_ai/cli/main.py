#!/usr/bin/env python3
"""
Ryoma AI SQL Agent CLI

A command-line interface for natural language to SQL conversion with human-in-the-loop approval.
Similar to Claude Code but specialized for database interactions.
"""

import os
import sys
import json
import argparse
import readline
from typing import Optional, Dict, Any
from pathlib import Path
import signal

import click
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.markdown import Markdown
from rich.text import Text
from langgraph.types import Command

from ryoma_ai.agent.sql import SqlAgent
from ryoma_ai.datasource.factory import DataSourceFactory, get_supported_datasources
from ryoma_ai.models.agent import SqlAgentMode


class RyomaSQL:
    """Main CLI application class."""

    def __init__(self):
        self.console = Console()
        self.agent: Optional[SqlAgent] = None
        self.datasource = None
        self.config = self._load_config()
        self.session_active = False

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or environment."""
        config_file = Path.home() / '.ryoma' / 'config.json'

        if config_file.exists():
            try:
                with open(config_file) as f:
                    return json.load(f)
            except Exception as e:
                self.console.print(f"[yellow]Warning: Could not load config file: {e}[/yellow]")

        # Default configuration
        return {
            "model": "gpt-4o",
            "mode": "enhanced",
            "database": {
                "type": "postgres",
                "host": "localhost",
                "port": 5432,
                "database": "postgres",
                "user": os.environ.get("POSTGRES_USER", ""),
                "password": os.environ.get("POSTGRES_PASSWORD", "")
            }
        }

    def _save_config(self):
        """Save current configuration to file."""
        config_dir = Path.home() / '.ryoma'
        config_dir.mkdir(exist_ok=True)

        config_file = config_dir / 'config.json'
        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def _setup_datasource(self, db_config: Dict[str, Any]):
        """Setup database connection using the factory with dynamic config validation."""
        if "type" not in db_config:
            raise ValueError("Database configuration must specify 'type' field")
        
        db_type = db_config["type"].lower()

        try:
            # Get the expected config fields for this datasource type
            expected_fields = DataSourceFactory.get_datasource_config(db_type)

            # Validate and prepare config parameters
            config_kwargs = self._prepare_datasource_config(db_config, expected_fields, db_type)

            # Use the factory to create the datasource
            self.datasource = DataSourceFactory.create_datasource(db_type, **config_kwargs)

            # Test connection
            self.datasource.query("SELECT 1")
            return True

        except ValueError as e:
            self.console.print(f"[red]Unsupported database type or configuration error: {e}[/red]")
            return False
        except Exception as e:
            self.console.print(f"[red]Database connection failed: {e}[/red]")
            return False

    def _prepare_datasource_config(self, db_config: Dict[str, Any], expected_fields: Dict[str, Any], db_type: str) -> Dict[str, Any]:
        """Prepare configuration parameters based on datasource field requirements."""
        # Remove 'type' from config
        config = {k: v for k, v in db_config.items() if k != "type"}

        # Validate that all required fields are present
        for field_name, field_info in expected_fields.items():
            is_required = field_info.is_required()  # Call the method
            if is_required and field_name not in config:
                raise ValueError(f"Missing required field '{field_name}' for {db_type} datasource")

        # Filter config to only include expected fields (remove any extra fields)
        filtered_config = {k: v for k, v in config.items() if k in expected_fields}

        return filtered_config

    def _setup_agent(self):
        """Setup SQL agent."""
        if not self.datasource:
            self.console.print("[red]No database connection available[/red]")
            return False

        try:
            mode = SqlAgentMode(self.config.get("mode", "enhanced"))
            self.agent = SqlAgent(
                model=self.config.get("model", "gpt-4o"),
                mode=mode,
                datasource=self.datasource
            )
            return True

        except Exception as e:
            self.console.print(f"[red]Failed to setup agent: {e}[/red]")
            return False

    def _display_banner(self):
        """Display CLI banner."""
        banner = """
🤖 Ryoma AI SQL Agent
Natural Language ➜ SQL with Human-in-the-Loop Approval
        """

        info_table = Table(show_header=False, box=None)
        info_table.add_row("Model:", self.config.get("model", "gpt-4o"))
        info_table.add_row("Mode:", self.config.get("mode", "enhanced"))
        info_table.add_row("Database:", f"{self.config['database']['type']}://{self.config['database']['host']}:{self.config['database']['port']}/{self.config['database']['database']}")

        self.console.print(Panel(banner, style="bold blue"))
        self.console.print(info_table)
        self.console.print()

    def _display_help(self):
        """Display help information."""
        help_text = """
## Commands:
- **Ask questions**: Type natural language questions about your database
- **/help**: Show this help message
- **/config**: Show current configuration
- **/setup**: Setup database connection
- **/mode <mode>**: Change agent mode (basic, enhanced, reforce)
- **/model <model>**: Change language model
- **/schema**: Show database schema
- **/quit** or **/exit**: Exit the CLI

## Examples:
- "Show me the top 5 customers by sales"
- "What are the most popular products last month?"
- "Find all orders from New York customers"

## Approval Workflow:
- Agent generates SQL and asks for approval
- Type **approve** to execute the query
- Type **deny** to reject the query
- Or provide modified SQL to use instead
        """

        self.console.print(Panel(Markdown(help_text), title="Ryoma SQL Help", style="green"))

    def _handle_command(self, input_text: str) -> bool:
        """Handle CLI commands. Returns True if command was handled."""
        if not input_text.startswith('/'):
            return False

        parts = input_text[1:].split(None, 1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        if command in ['help', 'h']:
            self._display_help()

        elif command in ['quit', 'exit', 'q']:
            self.console.print("[yellow]Goodbye! 👋[/yellow]")
            sys.exit(0)

        elif command == 'config':
            self._show_config()

        elif command == 'setup':
            self._interactive_setup()

        elif command == 'mode':
            if args:
                self._change_mode(args)
            else:
                self.console.print(f"Current mode: {self.config.get('mode', 'enhanced')}")

        elif command == 'model':
            if args:
                self._change_model(args)
            else:
                self.console.print(f"Current model: {self.config.get('model', 'gpt-4o')}")

        elif command == 'schema':
            self._show_schema()

        else:
            self.console.print(f"[red]Unknown command: {command}[/red]")
            self.console.print("Type [bold]/help[/bold] for available commands")

        return True

    def _show_config(self):
        """Show current configuration."""
        config_text = json.dumps(self.config, indent=2)
        syntax = Syntax(config_text, "json", theme="monokai", line_numbers=True)
        self.console.print(Panel(syntax, title="Current Configuration"))

    def _interactive_setup(self):
        """Interactive database setup using dynamic config introspection."""
        self.console.print("[bold]Database Setup[/bold]")

        # Get supported datasources from factory
        supported_types = [ds.name for ds in get_supported_datasources()]
        db_type = Prompt.ask("Database type", choices=supported_types, default="postgres")

        try:
            # Get the expected config fields for this datasource type
            expected_fields = DataSourceFactory.get_datasource_config(db_type)

            # Build config interactively based on field requirements
            new_config = {"type": db_type}

            for field_name, field_info in expected_fields.items():
                is_required = field_info.is_required()
                description = getattr(field_info, 'description', field_name)

                # Handle password fields specially
                if 'password' in field_name.lower():
                    value = Prompt.ask(f"{description}", password=True)
                else:
                    prompt_text = f"{description}"
                    if is_required:
                        prompt_text += " (required)"

                    value = Prompt.ask(prompt_text)

                # Convert to appropriate type based on annotation
                annotation = str(getattr(field_info, 'annotation', 'str'))
                if 'int' in annotation.lower() or 'port' in field_name.lower():
                    try:
                        if value:  # Only convert non-empty values
                            value = int(value)
                    except ValueError:
                        self.console.print(f"[red]Invalid integer value for {field_name}[/red]")
                        return

                # Add value if provided (required fields must have a value)
                if value or is_required:
                    new_config[field_name] = value
                elif is_required and not value:
                    self.console.print(f"[red]Required field '{field_name}' cannot be empty[/red]")
                    return

            self.console.print("[yellow]Testing connection...[/yellow]")

            if self._setup_datasource(new_config):
                self.config["database"] = new_config
                self._save_config()

                if self._setup_agent():
                    self.console.print("[green]✅ Database setup successful![/green]")
                else:
                    self.console.print("[red]❌ Failed to setup agent[/red]")
            else:
                self.console.print("[red]❌ Database connection failed[/red]")

        except Exception as e:
            self.console.print(f"[red]Error during setup: {e}[/red]")

    def _change_mode(self, mode: str):
        """Change agent mode."""
        try:
            SqlAgentMode(mode)
            self.config["mode"] = mode
            self._save_config()

            if self._setup_agent():
                self.console.print(f"[green]✅ Agent mode changed to: {mode}[/green]")
            else:
                self.console.print("[red]❌ Failed to reinitialize agent[/red]")

        except ValueError:
            self.console.print(f"[red]Invalid mode: {mode}. Valid modes: basic, enhanced, reforce[/red]")

    def _change_model(self, model: str):
        """Change language model."""
        self.config["model"] = model
        self._save_config()

        if self._setup_agent():
            self.console.print(f"[green]✅ Language model changed to: {model}[/green]")
        else:
            self.console.print("[red]❌ Failed to reinitialize agent[/red]")

    def _show_schema(self):
        """Show database schema."""
        if not self.datasource:
            self.console.print("[red]No database connection[/red]")
            return

        try:
            catalog = self.datasource.get_catalog()

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

    def _handle_interrupt_approval(self) -> str:
        """Handle interrupt-based approval in CLI."""
        try:
            # Get the current workflow state
            current_state = self.agent.get_current_state()

            if current_state and hasattr(current_state, 'next') and current_state.next:
                # We're in an interrupt state - extract SQL query for approval
                messages = current_state.values.get("messages", [])
                sql_query = None

                # For basic mode, the SQL query is in the latest AI message tool calls
                if messages and len(messages) > 0:
                    latest_message = messages[-1]
                    if hasattr(latest_message, 'tool_calls') and latest_message.tool_calls:
                        for tool_call in latest_message.tool_calls:
                            if tool_call.get('name') == 'sql_database_query':
                                sql_query = tool_call['args'].get('query', '')
                                break

                # For enhanced mode, also check the generated_sql field
                if not sql_query:
                    sql_query = current_state.values.get("generated_sql", "")

                if sql_query:
                    # Display the SQL query for approval
                    syntax = Syntax(sql_query, "sql", theme="monokai", line_numbers=True)
                    self.console.print(Panel(syntax, title="🔍 SQL Query for Approval", style="yellow"))

                    self.console.print("\n[bold]Options:[/bold]")
                    self.console.print("• Type [green]approve[/green] to execute")
                    self.console.print("• Type [red]deny[/red] to reject")
                    self.console.print("• Or provide modified SQL to use instead\n")

                    while True:
                        approval = Prompt.ask("Your decision")

                        if approval.lower() in ['approve', 'yes', 'y']:
                            return 'approve'
                        elif approval.lower() in ['deny', 'reject', 'no', 'n']:
                            return 'deny'
                        elif approval.strip():
                            # Treat as modified SQL
                            return approval.strip()
                        else:
                            self.console.print("[red]Please provide a valid response[/red]")
                else:
                    self.console.print("[yellow]No SQL query found for approval[/yellow]")
                    return 'deny'

        except Exception as e:
            self.console.print(f"[red]Error in approval workflow: {e}[/red]")
            return 'deny'

        return 'deny'

    def _format_execution_result(self, execution_result) -> str:
        """Format execution result for display, handling both artifacts and direct results."""
        if not execution_result:
            return "No results"

        # Check if it's a base64-encoded artifact (pickle)
        try:
            import base64
            import pickle

            # Try to decode as base64 and unpickle (artifact format)
            if isinstance(execution_result, str) and len(execution_result) > 100:
                # Likely an artifact string
                try:
                    decoded_data = base64.b64decode(execution_result.encode('utf-8'))
                    dataframe = pickle.loads(decoded_data)

                    # Format the DataFrame for display
                    if hasattr(dataframe, 'to_string'):
                        return dataframe.to_string(index=False)
                    else:
                        return str(dataframe)
                except:
                    # Not an artifact, treat as regular string
                    pass

            # Fallback to string representation
            if hasattr(execution_result, 'to_string'):
                return execution_result.to_string(index=False)
            else:
                return str(execution_result)

        except Exception as e:
            # If anything fails, just return string representation
            return str(execution_result)

    def _process_question(self, question: str):
        """Process a natural language question."""
        if not self.agent:
            self.console.print("[red]Agent not initialized. Run /setup first.[/red]")
            return

        self.console.print(f"[blue]Debug: Processing question: {question}[/blue]")

        try:
            # Check agent state before processing
            self.console.print("[blue]Debug: Starting workflow...[/blue]")
            with self.console.status("[bold green]Processing question..."):
                # Start the workflow and consume the generator
                result_generator = self.agent.stream(question, display=False)
                self.console.print(f"[blue]Debug: Stream result: {type(result_generator)}[/blue]")

                # IMPORTANT: Must consume the generator to actually execute the workflow
                for event in result_generator:
                    pass  # Just consume events to execute the workflow

            # Check current state after initial processing
            current_state = self.agent.get_current_state()
            self.console.print(f"[blue]Debug: Current state after stream: {current_state}[/blue]")

            if current_state:
                self.console.print(f"[blue]Debug: State values: {current_state.values.keys() if current_state.values else 'None'}[/blue]")
                if hasattr(current_state, 'next'):
                    self.console.print(f"[blue]Debug: Next steps: {current_state.next}[/blue]")

            # Handle any interrupts (approval requests)
            interrupt_count = 0
            while True:
                current_state = self.agent.get_current_state()
                interrupt_count += 1
                self.console.print(f"[blue]Debug: Interrupt check #{interrupt_count}[/blue]")

                if not current_state or not hasattr(current_state, 'next') or not current_state.next:
                    # Workflow completed
                    self.console.print("[blue]Debug: Workflow completed - no next steps[/blue]")
                    break

                self.console.print(f"[blue]Debug: Found interrupt state: {current_state.next}[/blue]")

                # Handle interrupt - get approval
                approval = self._handle_interrupt_approval()

                # Resume with approval
                with self.console.status("[bold green]Executing query..."):
                    resume_generator = self.agent.stream(Command(resume=approval), display=False)
                    # Consume the generator to execute the workflow
                    for event in resume_generator:
                        pass

                # Safety break to prevent infinite loops
                if interrupt_count > 10:
                    self.console.print("[red]Debug: Too many interrupts, breaking loop[/red]")
                    break

            # Get final results
            final_state = self.agent.get_current_state()
            self.console.print(f"[blue]Debug: Final state: {final_state}[/blue]")

            if final_state and final_state.values:
                execution_result = final_state.values.get("execution_result")
                error_info = final_state.values.get("error_info")
                final_answer = final_state.values.get("final_answer")

                self.console.print(f"[blue]Debug: Execution result: {bool(execution_result)}[/blue]")
                self.console.print(f"[blue]Debug: Error info: {bool(error_info)}[/blue]")
                self.console.print(f"[blue]Debug: Final answer: {bool(final_answer)}[/blue]")

                # Check for query execution results (basic mode)
                if execution_result and not error_info:
                    # Format execution result for display
                    result_display = self._format_execution_result(execution_result)
                    self.console.print(Panel(result_display, title="📊 Query Results", style="green"))

                # Check for enhanced mode final answer
                elif final_answer:
                    self.console.print(Panel(final_answer, title="🤖 Agent Response", style="blue"))

                # Check for errors
                elif error_info:
                    error_message = error_info.get('error_message', 'Unknown error') if isinstance(error_info, dict) else str(error_info)
                    self.console.print(Panel(f"❌ Error: {error_message}", title="Error", style="red"))

                # Check tool message results (basic mode after approval)
                else:
                    messages = final_state.values.get("messages", [])
                    if messages:
                        # Look for the latest tool message result
                        for message in reversed(messages):
                            if hasattr(message, 'content') and message.content and hasattr(message, 'type') and message.type == 'tool':
                                self.console.print(Panel(message.content, title="📊 Query Results", style="green"))
                                break
                        else:
                            self.console.print("[yellow]No results found in workflow[/yellow]")
                    else:
                        self.console.print("[yellow]No results or workflow incomplete[/yellow]")
            else:
                self.console.print("[yellow]Debug: No final state or values available[/yellow]")

        except Exception as e:
            import traceback
            self.console.print(f"[red]Error processing question: {e}[/red]")
            self.console.print(f"[red]Traceback: {traceback.format_exc()}[/red]")

    def _signal_handler(self, signum, frame):
        """Handle interrupt signals."""
        self.console.print("\n[yellow]Interrupted. Type /quit to exit.[/yellow]")

    def start(self):
        """Start the interactive CLI."""
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)

        self._display_banner()

        # Setup database connection
        if not self._setup_datasource(self.config["database"]):
            self.console.print("[yellow]Database connection failed. Use /setup to configure.[/yellow]")
        elif not self._setup_agent():
            self.console.print("[yellow]Agent initialization failed.[/yellow]")
        else:
            self.console.print("[green]✅ Ready! Ask me questions about your database.[/green]")

        self.console.print("\nType [bold]/help[/bold] for commands or just ask a question in natural language.\n")

        # Main interaction loop
        self.session_active = True
        while self.session_active:
            try:
                user_input = Prompt.ask("[bold cyan]ryoma-sql>[/bold cyan]").strip()

                if not user_input:
                    continue

                # Handle commands
                if self._handle_command(user_input):
                    continue

                # Process as natural language question
                self._process_question(user_input)

            except KeyboardInterrupt:
                self.console.print("\n[yellow]Use /quit to exit.[/yellow]")
                continue
            except EOFError:
                self.console.print("\n[yellow]Goodbye! 👋[/yellow]")
                break


@click.command()
@click.option('--model', '-m', default='gpt-4o', help='Language model to use')
@click.option('--mode', default='enhanced', type=click.Choice(['basic', 'enhanced', 'reforce']), help='SQL agent mode')
@click.option('--config', '-c', help='Config file path')
@click.option('--setup', is_flag=True, help='Run interactive setup')
def main(model, mode, config, setup):
    """Ryoma AI SQL Agent - Natural Language to SQL with Human-in-the-Loop Approval."""

    cli = RyomaSQL()

    # Override config if provided
    if model:
        cli.config['model'] = model
    if mode:
        cli.config['mode'] = mode

    if setup:
        cli._interactive_setup()
    else:
        cli.start()


if __name__ == '__main__':
    main()
