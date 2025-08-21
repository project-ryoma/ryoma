#!/usr/bin/env python3
"""
Ryoma AI CLI Application

Main CLI application class that orchestrates the multi-agent system.
"""

import signal
from typing import Optional
from pathlib import Path

import click
from rich.console import Console

from ryoma_ai.cli.config_manager import ConfigManager
from ryoma_ai.cli.command_handler import CommandHandler
from ryoma_ai.cli.datasource_manager import DataSourceManager
from ryoma_ai.cli.agent_manager import AgentManager
from ryoma_ai.cli.display_manager import DisplayManager


class RyomaAI:
    """Main CLI application class for Ryoma AI Multi-Agent System."""

    def __init__(self):
        """Initialize the CLI application with all managers."""
        self.console = Console()
        self.session_active = False

        # Initialize managers
        self.config_manager = ConfigManager()
        self.display_manager = DisplayManager(self.console)
        self.datasource_manager = DataSourceManager(self.console)
        self.agent_manager = AgentManager(self.console)
        self.command_handler = CommandHandler(
            console=self.console,
            config_manager=self.config_manager,
            datasource_manager=self.datasource_manager,
            agent_manager=self.agent_manager,
            display_manager=self.display_manager
        )

    def _signal_handler(self, signum, frame):
        """Handle interrupt signals."""
        self.console.print("\n[yellow]Interrupted. Type /quit to exit.[/yellow]")

    def start(self):
        """Start the interactive CLI."""
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)

        # Display banner
        self.display_manager.show_banner(self.config_manager.config)

        # Initialize system
        self._initialize_system()

        # Show help information
        self.console.print("\nType [bold]/help[/bold] for commands or just ask a question - I'll route it to the best agent!\n")

        # Main interaction loop
        self.session_active = True
        while self.session_active:
            try:
                from rich.prompt import Prompt
                user_input = Prompt.ask("[bold cyan]ryoma-ai>[/bold cyan]").strip()

                if not user_input:
                    continue

                # Handle commands or process questions
                if not self.command_handler.handle_command(user_input):
                    self.command_handler.process_question(user_input)

            except KeyboardInterrupt:
                self.console.print("\n[yellow]Use /quit to exit.[/yellow]")
                continue
            except EOFError:
                self.console.print("\n[yellow]Goodbye! 👋[/yellow]")
                break

    def _initialize_system(self):
        """Initialize the system components."""
        # Setup data source connection
        if not self.datasource_manager.setup_from_config(self.config_manager.config["database"]):
            self.console.print("[yellow]Database connection failed. Use /setup to configure.[/yellow]")
        elif not self.agent_manager.setup_agent_router(
            config=self.config_manager.config,
            datasource=self.datasource_manager.current_datasource
        ):
            self.console.print("[yellow]Agent initialization failed.[/yellow]")
        else:
            self.console.print("[green]✅ Ready! Multi-agent system initialized.[/green]")
            self.console.print("[dim]Available: SQL Agent, Python Agent, Data Analysis Agent, Chat Agent[/dim]")

    def stop(self):
        """Stop the CLI application."""
        self.session_active = False


@click.command()
@click.option('--model', '-m', default='gpt-4o', help='Language model to use')
@click.option('--mode', default='enhanced', type=click.Choice(['basic', 'enhanced', 'reforce']), help='SQL agent mode')
@click.option('--config', '-c', help='Config file path')
@click.option('--setup', is_flag=True, help='Run interactive setup')
def main(model, mode, config, setup):
    """Ryoma AI Multi-Agent System - Intelligent routing to specialized agents."""

    cli = RyomaAI()

    # Override config if provided
    if model:
        cli.config_manager.config['model'] = model
    if mode:
        cli.config_manager.config['mode'] = mode

    if setup:
        cli.command_handler.interactive_setup()
    else:
        cli.start()


if __name__ == '__main__':
    main()
