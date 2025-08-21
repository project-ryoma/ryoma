"""
Autocomplete Manager for Ryoma AI CLI

Provides command suggestion and autocomplete functionality.
"""

from typing import List, Optional, Tuple
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document


class RyomaAutoCompleter(Completer):
    """Autocomplete handler for Ryoma AI CLI commands."""

    def __init__(self):
        """Initialize the autocompleter with available commands."""
        self.commands = {
            # Basic commands
            "help": {"aliases": ["h"], "args": [], "description": "Show help message"},
            "quit": {"aliases": ["exit", "q"], "args": [], "description": "Exit the CLI"},
            "config": {"aliases": [], "args": [], "description": "Show current configuration"},
            "setup": {"aliases": [], "args": [], "description": "Setup database connection"},
            
            # Model and mode commands
            "mode": {"aliases": [], "args": ["basic", "enhanced", "reforce"], "description": "Change agent mode"},
            "model": {"aliases": [], "args": ["gpt-4o", "gpt-4", "gpt-3.5-turbo", "claude-3"], "description": "Change language model"},
            
            # Schema and agent commands
            "schema": {"aliases": [], "args": [], "description": "Show database schema"},
            "agents": {"aliases": [], "args": [], "description": "Show available agents"},
            "stats": {"aliases": [], "args": [], "description": "Show agent usage statistics"},
            
            # Data source management
            "datasources": {"aliases": [], "args": [], "description": "Show all registered data sources"},
            "add-datasource": {"aliases": [], "args": [], "description": "Add a new data source interactively"},
            "switch-datasource": {"aliases": [], "args": [], "description": "Switch to a different data source"},
            
            # Catalog management
            "index-catalog": {"aliases": [], "args": ["catalog", "schema", "table", "column"], "description": "Index catalog for search"},
            "search-catalog": {"aliases": [], "args": [], "description": "Search indexed catalogs"},
            
            # Agent configuration
            "agent-config": {"aliases": [], "args": ["auto_approve_all", "retry_count", "timeout_seconds"], "description": "Configure agent settings"},
            "auto-approve": {"aliases": [], "args": ["true", "false", "on", "off", "enable", "disable"], "description": "Toggle auto-approve for SQL queries"}
        }

        # Create flat list of all commands including aliases
        self.all_commands = []
        for cmd, info in self.commands.items():
            self.all_commands.append(cmd)
            self.all_commands.extend(info["aliases"])

    def get_completions(self, document: Document, complete_event) -> List[Completion]:
        """
        Get completion suggestions for the current input.

        Args:
            document: Current document state
            complete_event: Completion event

        Returns:
            List of completion suggestions
        """
        text = document.text
        
        # Handle empty input - suggest common commands
        if not text or text == "/":
            return [
                Completion("/help", start_position=-len(text), display_meta="Show help"),
                Completion("/config", start_position=-len(text), display_meta="Show config"),
                Completion("/agents", start_position=-len(text), display_meta="Show agents"),
                Completion("/stats", start_position=-len(text), display_meta="Show stats"),
                Completion("/setup", start_position=-len(text), display_meta="Setup database"),
            ]

        # Only complete if text starts with /
        if not text.startswith("/"):
            return []

        # Remove the leading slash for processing
        command_text = text[1:]
        words = command_text.split()
        
        if len(words) == 0:
            # Just typed "/", show all commands
            return self._get_command_completions("", 1)
        elif len(words) == 1:
            # Completing the command name
            partial_command = words[0]
            return self._get_command_completions(partial_command, len(partial_command) + 1)
        else:
            # Completing command arguments
            command = words[0]
            current_arg = words[-1] if words else ""
            return self._get_argument_completions(command, current_arg, len(current_arg))

    def _get_command_completions(self, partial: str, start_offset: int) -> List[Completion]:
        """Get completions for command names."""
        completions = []
        
        for cmd in self.all_commands:
            if cmd.startswith(partial.lower()):
                # Find the canonical command name for description
                canonical_cmd = self._get_canonical_command(cmd)
                description = self.commands.get(canonical_cmd, {}).get("description", "")
                
                completion_text = f"/{cmd}"
                completions.append(Completion(
                    completion_text,
                    start_position=-start_offset,
                    display_meta=description
                ))
        
        return completions

    def _get_argument_completions(self, command: str, current_arg: str, start_offset: int) -> List[Completion]:
        """Get completions for command arguments."""
        canonical_cmd = self._get_canonical_command(command)
        
        if canonical_cmd not in self.commands:
            return []
        
        args = self.commands[canonical_cmd]["args"]
        completions = []
        
        for arg in args:
            if arg.startswith(current_arg.lower()):
                completions.append(Completion(
                    arg,
                    start_position=-start_offset,
                    display_meta=f"Option for {canonical_cmd}"
                ))
        
        return completions

    def _get_canonical_command(self, cmd: str) -> str:
        """Get the canonical command name from a command or alias."""
        for canonical, info in self.commands.items():
            if cmd == canonical or cmd in info["aliases"]:
                return canonical
        return cmd

    def get_command_suggestions(self, partial_input: str) -> List[Tuple[str, str]]:
        """
        Get command suggestions for display.

        Args:
            partial_input: Partial command input

        Returns:
            List of (command, description) tuples
        """
        if not partial_input.startswith("/"):
            return []

        command_text = partial_input[1:]
        suggestions = []

        for cmd in self.all_commands:
            if cmd.startswith(command_text.lower()):
                canonical_cmd = self._get_canonical_command(cmd)
                description = self.commands.get(canonical_cmd, {}).get("description", "")
                suggestions.append((f"/{cmd}", description))

        return suggestions[:5]  # Limit to 5 suggestions


class AutocompleteManager:
    """Manages autocomplete functionality for the CLI."""

    def __init__(self):
        """Initialize the autocomplete manager."""
        self.completer = RyomaAutoCompleter()

    def get_completer(self) -> RyomaAutoCompleter:
        """
        Get the autocompleter instance.

        Returns:
            The autocompleter instance
        """
        return self.completer

    def get_suggestions(self, partial_input: str) -> List[Tuple[str, str]]:
        """
        Get command suggestions for the given partial input.

        Args:
            partial_input: Partial command input

        Returns:
            List of (command, description) tuples
        """
        return self.completer.get_command_suggestions(partial_input)

    def update_dynamic_completions(self, 
                                   datasource_ids: Optional[List[str]] = None,
                                   model_names: Optional[List[str]] = None) -> None:
        """
        Update dynamic completions based on current system state.

        Args:
            datasource_ids: List of available datasource IDs
            model_names: List of available model names
        """
        if datasource_ids:
            # Update switch-datasource command with actual datasource IDs
            self.completer.commands["switch-datasource"]["args"] = datasource_ids

        if model_names:
            # Update model command with actual model names
            self.completer.commands["model"]["args"] = model_names