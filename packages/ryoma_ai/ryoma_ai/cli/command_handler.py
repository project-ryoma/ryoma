"""
Command Handler for Ryoma AI CLI

Handles all CLI commands and orchestrates different managers.
"""

import sys
from typing import TYPE_CHECKING

from rich.console import Console

if TYPE_CHECKING:
    from ryoma_ai.cli.config_manager import ConfigManager
    from ryoma_ai.cli.datasource_manager import DataSourceManager
    from ryoma_ai.cli.agent_manager import AgentManager
    from ryoma_ai.cli.display_manager import DisplayManager

from ryoma_ai.cli.catalog_manager import CatalogManager


class CommandHandler:
    """Handles CLI command processing and orchestration."""

    def __init__(
        self,
        console: Console,
        config_manager: "ConfigManager",
        datasource_manager: "DataSourceManager",
        agent_manager: "AgentManager",
        display_manager: "DisplayManager",
    ):
        """
        Initialize the command handler.

        Args:
            console: Rich console for output
            config_manager: Configuration manager instance
            datasource_manager: Data source manager instance
            agent_manager: Agent manager interface instance
            display_manager: Display manager instance
        """
        self.console = console
        self.config_manager = config_manager
        self.datasource_manager = datasource_manager
        self.agent_interface = agent_manager
        self.display_manager = display_manager
        self.catalog_manager = CatalogManager(console)

    def handle_command(self, input_text: str) -> bool:
        """
        Handle CLI commands.

        Args:
            input_text: User input text

        Returns:
            bool: True if command was handled, False if not a command
        """
        if not input_text.startswith("/"):
            return False

        parts = input_text[1:].split(None, 1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        # Basic commands
        if command in ["help", "h"]:
            self.display_manager.show_help()

        elif command in ["quit", "exit", "q"]:
            self.console.print("[yellow]Goodbye! 👋[/yellow]")
            sys.exit(0)

        elif command == "config":
            self.display_manager.show_config(self.config_manager.config)

        elif command == "setup":
            self.interactive_setup()

        # Model and mode commands
        elif command == "mode":
            self._handle_mode_command(args)

        elif command == "model":
            self._handle_model_command(args)

        # Schema and agent commands
        elif command == "schema":
            self.display_manager.show_schema(self.datasource_manager.current_datasource)

        elif command == "agents":
            self.agent_interface.show_agents()

        elif command == "stats":
            self.agent_interface.show_stats()

        # Data source management commands
        elif command == "datasources":
            self.datasource_manager.show_datasources()

        elif command == "add-datasource":
            self.datasource_manager.add_datasource_interactive()

        elif command == "switch-datasource":
            self._handle_switch_datasource_command(args)

        # Catalog management commands
        elif command == "index-catalog":
            self._handle_index_catalog_command(args)

        elif command == "search-catalog":
            self._handle_search_catalog_command(args)

        # Agent configuration commands
        elif command == "agent-config":
            self._handle_agent_config_command(args)

        elif command == "auto-approve":
            self._handle_auto_approve_command(args)

        else:
            self.console.print(f"[red]Unknown command: {command}[/red]")
            self.console.print("Type [bold]/help[/bold] for available commands")

        return True

    def process_question(self, question: str) -> None:
        """
        Process a natural language question.

        Args:
            question: User's natural language question
        """
        self.agent_interface.process_question(question)

    def interactive_setup(self) -> None:
        """Run interactive database setup."""
        if self.datasource_manager.interactive_setup():
            # Update config with new database settings
            # Note: This is simplified - in a real implementation, you'd want to
            # update the config manager with the new database settings

            # Reinitialize agent manager with new data source
            if self.agent_interface.setup_agent_manager(
                config=self.config_manager.config,
                datasource=self.datasource_manager.current_datasource,
            ):
                self.display_manager.show_success("✅ Database setup successful!")
            else:
                self.display_manager.show_error("❌ Failed to setup agent")
        else:
            self.display_manager.show_error("❌ Database setup failed")

    def _handle_mode_command(self, args: str) -> None:
        """Handle mode change command."""
        if args:
            if self.agent_interface.change_mode(args):
                self.config_manager.update_config("mode", args)
                # Reinitialize agent manager
                self.agent_interface.setup_agent_manager(
                    config=self.config_manager.config,
                    datasource=self.datasource_manager.current_datasource,
                )
        else:
            current_mode = self.config_manager.get_config("mode", "enhanced")
            self.console.print(f"Current mode: {current_mode}")

    def _handle_model_command(self, args: str) -> None:
        """Handle model change command."""
        if args:
            if self.agent_interface.change_model(args):
                self.config_manager.update_config("model", args)
                # Reinitialize agent manager
                self.agent_interface.setup_agent_manager(
                    config=self.config_manager.config,
                    datasource=self.datasource_manager.current_datasource,
                )
        else:
            current_model = self.config_manager.get_config("model", "gpt-4o")
            self.console.print(f"Current model: {current_model}")

    def _handle_switch_datasource_command(self, args: str) -> None:
        """Handle switch datasource command."""
        if args:
            if self.datasource_manager.switch_datasource(args):
                # Reinitialize agent manager with new data source
                self.agent_interface.setup_agent_manager(
                    config=self.config_manager.config,
                    datasource=self.datasource_manager.current_datasource,
                )
        else:
            self.datasource_manager.show_datasource_selection()

    def _handle_index_catalog_command(self, args: str) -> None:
        """Handle index catalog command."""
        if args:
            parts = args.split()
            if len(parts) < 1:
                self.display_manager.show_error(
                    "Usage: /index-catalog <datasource_id> [level]"
                )
                return

            datasource_id = parts[0]
            level = parts[1] if len(parts) > 1 else "table"

            try:
                datasource = self.datasource_manager.datasource_store.get_data_source(
                    datasource_id
                )
                self.catalog_manager.index_catalog(datasource_id, datasource, level)
            except Exception as e:
                self.display_manager.show_error(f"Failed to index catalog: {e}")
        else:
            # Index current catalog
            if (
                not self.datasource_manager.current_datasource_id
                or not self.datasource_manager.current_datasource
            ):
                self.display_manager.show_error("No current data source selected")
                return

            self.catalog_manager.index_catalog(
                self.datasource_manager.current_datasource_id,
                self.datasource_manager.current_datasource,
                "table",
            )

    def _handle_search_catalog_command(self, args: str) -> None:
        """Handle search catalog command."""
        if not args:
            self.display_manager.show_error("Please provide a search query")
            return

        results = self.catalog_manager.search_catalogs(args, top_k=5)
        self.display_manager.show_search_results(args, results)

    def _handle_agent_config_command(self, args: str) -> None:
        """Handle agent configuration commands."""
        if not args:
            # Show current agent configuration
            agent_config = self.config_manager.get_config("agent", {})
            if agent_config:
                from rich.table import Table

                config_table = Table(title="🤖 Agent Configuration")
                config_table.add_column("Setting", style="cyan")
                config_table.add_column("Value", style="green")

                for key, value in agent_config.items():
                    config_table.add_row(key, str(value))

                self.console.print(config_table)
            else:
                self.console.print("[yellow]No agent configuration found[/yellow]")
            return

        # Parse config setting: /agent-config setting_name value
        parts = args.split(None, 1)
        if len(parts) < 2:
            self.display_manager.show_error("Usage: /agent-config <setting> <value>")
            self.console.print(
                "Available settings: auto_approve_all, retry_count, timeout_seconds"
            )
            return

        setting = parts[0]
        value_str = parts[1]

        # Convert value to appropriate type
        if setting == "auto_approve_all":
            value = value_str.lower() in ["true", "1", "yes", "on", "enable"]
        elif setting in ["retry_count", "timeout_seconds"]:
            try:
                value = int(value_str)
            except ValueError:
                self.display_manager.show_error(
                    f"'{setting}' requires an integer value"
                )
                return
        else:
            self.display_manager.show_error(f"Unknown agent setting: {setting}")
            self.console.print(
                "Available settings: auto_approve_all, retry_count, timeout_seconds"
            )
            return

        # Update the configuration
        self.config_manager.update_config(f"agent.{setting}", value)

        # Reinitialize agent manager with new config
        if self.datasource_manager.current_datasource:
            self.agent_interface.setup_agent_manager(
                config=self.config_manager.config,
                datasource=self.datasource_manager.current_datasource,
            )

        self.console.print(f"[green]✅ Updated agent.{setting} = {value}[/green]")

    def _handle_auto_approve_command(self, args: str) -> None:
        """Handle auto-approve toggle command."""
        current_value = self.config_manager.get_config("agent.auto_approve_all", False)

        if args:
            # Set specific value
            new_value = args.lower() in ["true", "1", "yes", "on", "enable"]
        else:
            # Toggle current value
            new_value = not current_value

        self.config_manager.update_config("agent.auto_approve_all", new_value)

        # Reinitialize agent manager with new config
        if self.datasource_manager.current_datasource:
            self.agent_interface.setup_agent_manager(
                config=self.config_manager.config,
                datasource=self.datasource_manager.current_datasource,
            )

        status = "enabled" if new_value else "disabled"
        self.console.print(f"[green]✅ Auto-approve {status}[/green]")
