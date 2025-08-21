"""
Agent Interface for Ryoma AI CLI

Handles agent management, routing, and execution.
"""

import traceback
from typing import Dict, Any, Optional

from openai import APIConnectionError
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.syntax import Syntax
from langgraph.types import Command

from ryoma_ai.agent.multi_agent_router import MultiAgentRouter, TaskClassification
from ryoma_ai.datasource.base import DataSource
from ryoma_ai.models.agent import SqlAgentMode


class AgentManager:
    """Manages agent interactions and execution."""

    def __init__(self, console: Console):
        """
        Initialize the agent interface.

        Args:
            console: Rich console for output
        """
        self.console = console
        self.agent_router: Optional[MultiAgentRouter] = None
        self.current_agent = None
        self.current_classification: Optional[TaskClassification] = None
        self.agent_config: Dict[str, Any] = {}

    def setup_agent_manager(self, config: Dict[str, Any], datasource: DataSource) -> bool:
        """
        Setup the multi-agent routing manager.

        Args:
            config: Configuration dictionary
            datasource: Current data source

        Returns:
            bool: True if setup successful
        """
        if not datasource:
            self.console.print("[red]No database connection available[/red]")
            return False

        try:
            # Store agent configuration
            self.agent_config = config.get("agent", {})
            
            self.agent_router = MultiAgentRouter(
                model=config.get("model"),
                datasource=datasource,
                model_parameters=config.get("model_parameters", {})
            )
            return True

        except Exception as e:
            self.console.print(f"[red]Failed to setup agent manager: {e}[/red]")
            return False

    def process_question(self, question: str) -> None:
        """
        Process a natural language question using multi-agent routing.

        Args:
            question: User's natural language question
        """
        if not self.agent_router:
            self.console.print("[red]Agent manager not initialized. Run /setup first.[/red]")
            return

        try:
            # Step 1: Route the question to the appropriate agent
            with self.console.status("[bold green]🧠 Analyzing question and routing to best agent..."):
                try:
                    agent, classification, context = self.agent_router.route_and_execute(question)
                    self.current_agent = agent
                    self.current_classification = classification
                except APIConnectionError:
                    self.console.print(f"[red]OpenAI Connection Error, Did you forget to setup OpenAI token?[/red]")
                    return
                except Exception:
                    self.console.print_exception()
                    return

            # Step 2: Display routing information
            self.console.print(f"[cyan]🎯 Routed to: {classification.suggested_agent.title()} Agent[/cyan]")
            self.console.print(f"[dim]Confidence: {classification.confidence:.2f} | Reasoning: {classification.reasoning}[/dim]")

            # Step 3: Execute with the selected agent
            if classification.suggested_agent == "sql":
                # SQL agent requires special handling for approval workflow
                self._handle_sql_agent_execution(agent, question)
            else:
                # Other agents can execute directly
                self._handle_general_agent_execution(agent, question, classification.suggested_agent)

        except Exception as e:
            self.console.print(f"[red]Error processing question: {e}[/red]")
            self.console.print(f"[red]Traceback: {traceback.format_exc()}[/red]")

    def _handle_sql_agent_execution(self, agent, question: str) -> None:
        """Handle SQL agent execution with approval workflow."""
        try:
            # Start the SQL workflow
            with self.console.status("[bold green]🔍 Generating SQL query..."):
                result_generator = agent.stream(question, display=False)
                # Consume the generator to execute the workflow
                for event in result_generator:
                    pass

            # Handle approval workflow
            interrupt_count = 0
            while True:
                current_state = agent.get_current_state()
                interrupt_count += 1

                if not current_state or not hasattr(current_state, 'next') or not current_state.next:
                    # Workflow completed
                    break

                # Handle interrupt - get approval
                approval = self._handle_interrupt_approval(agent)

                # Resume with approval
                with self.console.status("[bold green]⚡ Executing query..."):
                    resume_generator = agent.stream(Command(resume=approval), display=False)
                    for event in resume_generator:
                        pass

                # Safety break
                if interrupt_count > 10:
                    self.console.print("[red]Too many approval requests, breaking[/red]")
                    break

            # Display results
            self._display_agent_results(agent, "SQL")

        except Exception as e:
            self.console.print(f"[red]SQL Agent Error: {e}[/red]")

    def _handle_general_agent_execution(self, agent, question: str, agent_type: str) -> None:
        """Handle execution for non-SQL agents."""
        try:
            with self.console.status(f"[bold green]🤖 {agent_type.title()} Agent processing..."):
                # For non-SQL agents, we might need different execution patterns
                if hasattr(agent, 'stream'):
                    result_generator = agent.stream(question, display=True)
                    for event in result_generator:
                        pass
                elif hasattr(agent, 'run'):
                    result = agent.run(question)
                    self.console.print(Panel(str(result), title=f"🤖 {agent_type.title()} Agent Response", style="blue"))
                else:
                    self.console.print(f"[yellow]Agent type {agent_type} execution not yet implemented[/yellow]")

        except Exception as e:
            self.console.print(f"[red]{agent_type.title()} Agent Error: {e}[/red]")

    def _handle_interrupt_approval(self, agent) -> str:
        """Handle interrupt-based approval in CLI."""
        try:
            # Check if auto-approve is enabled
            if self.agent_config.get("auto_approve_all", False):
                self.console.print("[green]🔄 Auto-approve enabled - automatically approving query[/green]")
                return 'approve'

            # Get the current workflow state
            current_state = agent.get_current_state()

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

    def _display_agent_results(self, agent, agent_type: str) -> None:
        """Display results from agent execution."""
        try:
            final_state = agent.get_current_state()

            if final_state and final_state.values:
                execution_result = final_state.values.get("execution_result")
                error_info = final_state.values.get("error_info")
                final_answer = final_state.values.get("final_answer")

                # Check for query execution results
                if execution_result and not error_info:
                    result_display = self._format_execution_result(execution_result)
                    self.console.print(Panel(result_display, title="📊 Query Results", style="green"))

                # Check for enhanced mode final answer
                elif final_answer:
                    self.console.print(Panel(final_answer, title=f"🤖 {agent_type} Agent Response", style="blue"))

                # Check for errors
                elif error_info:
                    error_message = error_info.get('error_message', 'Unknown error') if isinstance(error_info, dict) else str(error_info)
                    self.console.print(Panel(f"❌ Error: {error_message}", title="Error", style="red"))

                else:
                    self.console.print("[yellow]No results found in workflow[/yellow]")
            else:
                self.console.print("[yellow]No results available[/yellow]")

        except Exception as e:
            self.console.print(f"[red]Error displaying results: {e}[/red]")

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

    def show_agents(self) -> None:
        """Show available agents and their capabilities."""
        if not self.agent_router:
            self.console.print("[red]Agent manager not initialized[/red]")
            return

        try:
            from rich.table import Table

            capabilities = self.agent_router.get_capabilities()

            for agent_name, agent_info in capabilities.items():
                # Create table for each agent
                agent_table = Table(title=f"🤖 {agent_name}")
                agent_table.add_column("Capabilities", style="green")
                agent_table.add_column("Examples", style="cyan")

                # Add capabilities and examples
                max_rows = max(len(agent_info["capabilities"]), len(agent_info["examples"]))
                for i in range(max_rows):
                    capability = agent_info["capabilities"][i] if i < len(agent_info["capabilities"]) else ""
                    example = agent_info["examples"][i] if i < len(agent_info["examples"]) else ""
                    agent_table.add_row(capability, example)

                self.console.print(agent_table)
                self.console.print()

        except Exception as e:
            self.console.print(f"[red]Failed to retrieve agent capabilities: {e}[/red]")

    def show_stats(self) -> None:
        """Show agent usage statistics."""
        if not self.agent_router:
            self.console.print("[red]Agent manager not initialized[/red]")
            return

        try:
            from rich.table import Table

            stats = self.agent_router.get_current_stats()

            stats_table = Table(title="📊 Agent Usage Statistics")
            stats_table.add_column("Metric", style="cyan")
            stats_table.add_column("Value", style="green")

            stats_table.add_row("Total Queries", str(stats["total_queries"]))
            stats_table.add_row("Active Agents", str(len(stats["active_agents"])))

            # Add agent usage breakdown
            for agent_type, count in stats["agent_usage"].items():
                stats_table.add_row(f"{agent_type.title()} Agent", str(count))

            self.console.print(stats_table)

            # Show current classification if available
            if self.current_classification:
                self.console.print(f"\n[bold]Last Classification:[/bold]")
                self.console.print(f"  Agent: {self.current_classification.suggested_agent}")
                self.console.print(f"  Confidence: {self.current_classification.confidence:.2f}")
                self.console.print(f"  Reasoning: {self.current_classification.reasoning}")

        except Exception as e:
            self.console.print(f"[red]Failed to retrieve statistics: {e}[/red]")

    def change_mode(self, mode: str) -> bool:
        """
        Change agent mode.

        Args:
            mode: New mode to set

        Returns:
            bool: True if mode change successful
        """
        try:
            SqlAgentMode(mode)
            self.console.print(f"[green]✅ Agent mode changed to: {mode}[/green]")
            return True

        except ValueError:
            self.console.print(f"[red]Invalid mode: {mode}. Valid modes: basic, enhanced, reforce[/red]")
            return False

    def change_model(self, model: str) -> bool:
        """
        Change language model.

        Args:
            model: New model to set

        Returns:
            bool: True if model change successful
        """
        try:
            self.console.print(f"[green]✅ Language model changed to: {model}[/green]")
            return True

        except Exception as e:
            self.console.print(f"[red]Failed to change model: {e}[/red]")
            return False
