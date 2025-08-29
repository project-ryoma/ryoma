#!/usr/bin/env python3
"""
Ryoma AI CLI Application

Main CLI application class that orchestrates the multi-agent system.
"""

import signal

import click
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import CompleteStyle
from rich.console import Console
from ryoma_ai.cli.agent_manager import AgentManager
from ryoma_ai.cli.autocomplete_manager import AutocompleteManager
from ryoma_ai.cli.command_handler import CommandHandler
from ryoma_ai.cli.config_manager import ConfigManager
from ryoma_ai.cli.datasource_manager import DataSourceManager
from ryoma_ai.cli.display_manager import DisplayManager
from ryoma_ai.store.store_factory import StoreFactory


class RyomaAI:
    """Main CLI application class for Ryoma AI Multi-Agent System."""

    def __init__(self):
        """Initialize the CLI application with all managers."""
        self.console = Console()
        self.session_active = False

        # Initialize managers
        self.config_manager = ConfigManager()
        self.display_manager = DisplayManager(self.console)

        # Create stores from configuration
        try:
            meta_store_config = self.config_manager.get_meta_store_config()
            self.meta_store = StoreFactory.create_store(
                **meta_store_config.to_factory_params()
            )
        except Exception as e:
            self.console.print(
                f"[yellow]Warning: Using default memory store for metadata: {e}[/yellow]"
            )
            from langchain_core.stores import InMemoryStore

            self.meta_store = InMemoryStore()

        try:
            vector_store_config = self.config_manager.get_vector_store_config()
            # Create actual vector store instance
            from ryoma_ai.embedding.client import get_embedding_client
            from ryoma_ai.vector_store.factory import create_vector_store

            # Create embedding function for vector store
            embedding_model = self.config_manager.get_config(
                "embedding_model", "text-embedding-ada-002"
            )
            embedding = get_embedding_client(embedding_model)
            self.vector_store = create_vector_store(
                config=vector_store_config, embedding_function=embedding
            )
            self.vector_store_config = vector_store_config
        except Exception as e:
            self.console.print(
                f"[yellow]Warning: Vector store creation failed, using None: {e}[/yellow]"
            )
            self.vector_store = None
            self.vector_store_config = None

        # Initialize managers with their respective configs
        self.datasource_manager = DataSourceManager(
            self.console, meta_store=self.meta_store
        )
        self.agent_manager = AgentManager(self.console)
        self.autocomplete_manager = AutocompleteManager()
        self.command_handler = CommandHandler(
            console=self.console,
            config_manager=self.config_manager,
            datasource_manager=self.datasource_manager,
            agent_manager=self.agent_manager,
            display_manager=self.display_manager,
            meta_store=self.meta_store,
            vector_store=self.vector_store,
        )

        # Setup prompt history and key bindings
        self.history = InMemoryHistory()
        self.key_bindings = self._setup_key_bindings()

    def _setup_key_bindings(self) -> KeyBindings:
        """Setup key bindings for the prompt."""
        kb = KeyBindings()

        @kb.add("escape")
        def _(event):
            """Handle ESC key to cancel current input."""
            event.app.exit(result="")

        return kb

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
        self.console.print(
            "\nType [bold]/help[/bold] for commands or just ask a question - I'll route it to the best agent!\n"
        )

        # Main interaction loop
        self.session_active = True
        while self.session_active:
            try:
                # Update dynamic completions based on current state
                self._update_autocomplete_context()

                # Get user input with autocomplete support
                user_input = prompt(
                    "ryoma-ai> ",
                    completer=self.autocomplete_manager.get_completer(),
                    complete_style=CompleteStyle.MULTI_COLUMN,
                    history=self.history,
                    key_bindings=self.key_bindings,
                    enable_history_search=True,
                ).strip()

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
            except Exception as e:
                # Handle ESC key or other prompt cancellation
                if str(e) == "" or "cancelled" in str(e).lower():
                    self.console.print("\n[yellow]Input cancelled.[/yellow]")
                    continue
                else:
                    self.console.print(f"\n[red]Error: {e}[/red]")
                    continue

    def _update_autocomplete_context(self) -> None:
        """Update autocomplete context with current system state."""
        try:
            # Get available datasource IDs
            datasource_ids = []
            if hasattr(self.datasource_manager, "datasource_store"):
                registrations = (
                    self.datasource_manager.datasource_store.list_data_sources()
                )
                datasource_ids = [
                    reg.id[:8] for reg in registrations
                ]  # Use short IDs for completion

            # Update dynamic completions
            self.autocomplete_manager.update_dynamic_completions(
                datasource_ids=datasource_ids
            )
        except Exception:
            # If context update fails, continue with static completions
            pass

    def _initialize_system(self):
        """Initialize the system components with separate store configurations."""
        # Initialize components using new three-part config structure

        # 1. Initialize metadata store
        try:
            meta_store_config = self.config_manager.get_meta_store_config()
            self.console.print(f"[dim]Metadata store: {meta_store_config.type}[/dim]")
        except Exception as e:
            self.console.print(
                f"[yellow]Warning: Metadata store config issue: {e}[/yellow]"
            )

        # 2. Initialize vector store
        try:
            vector_store_config = self.config_manager.get_vector_store_config()
            self.console.print(f"[dim]Vector store: {vector_store_config.type}[/dim]")
        except Exception as e:
            self.console.print(
                f"[yellow]Warning: Vector store config issue: {e}[/yellow]"
            )

        # 3. Setup datasource connection
        datasource_config = self.config_manager.get_default_datasource_config()

        if datasource_config and not self.datasource_manager.setup_from_config(
            datasource_config
        ):
            self.console.print(
                "[yellow]Datasource connection failed. Use /setup to configure.[/yellow]"
            )
        elif not self.agent_manager.setup_agent_manager(
            config=self.config_manager.config,
            datasource=self.datasource_manager.current_datasource,
            vector_store=getattr(self, "vector_store", None),
            meta_store=self.meta_store,
        ):
            self.console.print("[yellow]Agent initialization failed.[/yellow]")
        else:
            self.console.print(
                "[green]✅ Ready! Multi-agent system initialized.[/green]"
            )
            self.console.print(
                "[dim]Available: SQL Agent, Python Agent, Data Analysis Agent, Chat Agent[/dim]"
            )

    def stop(self):
        """Stop the CLI application."""
        self.session_active = False


@click.command()
@click.option("--model", "-m", default="gpt-4o", help="Language model to use")
@click.option(
    "--mode",
    default="enhanced",
    type=click.Choice(["basic", "enhanced", "reforce"]),
    help="SQL agent mode",
)
@click.option("--config", "-c", help="Config file path")
@click.option("--meta-store-type", help="Metadata store type (memory, postgres, redis)")
@click.option(
    "--vector-store-type", help="Vector store type (chroma, faiss, qdrant, pgvector)"
)
@click.option(
    "--datasource-type", help="Default datasource type (postgres, mysql, sqlite, etc.)"
)
@click.option("--setup", is_flag=True, help="Run interactive setup")
def main(
    model, mode, config, meta_store_type, vector_store_type, datasource_type, setup
):
    """Ryoma AI Multi-Agent System - Intelligent routing to specialized agents."""

    cli = RyomaAI()

    # Override config if provided
    if model:
        cli.config_manager.config["model"] = model
    if mode:
        cli.config_manager.config["mode"] = mode

    # Override store configurations from CLI options
    if meta_store_type:
        cli.config_manager.update_config("meta_store.type", meta_store_type)
    if vector_store_type:
        cli.config_manager.update_config("vector_store.type", vector_store_type)
    if datasource_type:
        # Update the default datasource type
        datasources = cli.config_manager.get_datasources_list()
        if datasources:
            datasources[0]["type"] = datasource_type
            cli.config_manager.update_config("datasources", datasources)

    if setup:
        cli.command_handler.interactive_setup()
    else:
        cli.start()


if __name__ == "__main__":
    main()
