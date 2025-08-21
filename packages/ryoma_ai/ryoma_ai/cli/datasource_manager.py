"""
Data Source Manager for Ryoma AI CLI

Handles data source connections, registration, and management.
"""

from typing import Dict, Any, Optional

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table

from ryoma_ai.datasource.factory import DataSourceFactory, get_supported_datasources
from ryoma_ai.datasource.base import DataSource
from ryoma_ai.store import DataSourceStore


class DataSourceManager:
    """Manages data source connections and operations."""

    def __init__(self, console: Console):
        """
        Initialize the data source manager.

        Args:
            console: Rich console for output
        """
        self.console = console
        self.datasource_store = DataSourceStore()
        self.current_datasource: Optional[DataSource] = None
        self.current_datasource_id: Optional[str] = None

    def setup_from_config(self, db_config: Dict[str, Any]) -> bool:
        """
        Setup database connection from configuration.

        Args:
            db_config: Database configuration dictionary

        Returns:
            bool: True if setup successful
        """
        if "type" not in db_config:
            self.console.print("[red]Database configuration must specify 'type' field[/red]")
            return False

        db_type = db_config["type"].lower()
        name = db_config.get("name")
        description = db_config.get("description")

        try:
            # Get expected config fields for this datasource type
            expected_fields = DataSourceFactory.get_datasource_config(db_type)

            # Validate and prepare config parameters
            config_kwargs = self._prepare_datasource_config(db_config, expected_fields, db_type)

            # Create the datasource
            self.current_datasource = DataSourceFactory.create_datasource(db_type, **config_kwargs)

            # Test connection
            self.current_datasource.query("SELECT 1")

            # Register the data source
            with self.console.status("[yellow]Registering data source..."):
                ds_id = self.datasource_store.register_data_source(
                    name=name,
                    datasource_type=db_type,
                    config=config_kwargs,
                    description=description if description else None
                )

            self.console.print(f"[green]✅ Data source registered with ID: {ds_id}[/green]")
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
            is_required = field_info.is_required()
            if is_required and field_name not in config:
                raise ValueError(f"Missing required field '{field_name}' for {db_type} datasource")

        # Filter config to only include expected fields
        filtered_config = {k: v for k, v in config.items() if k in expected_fields}
        return filtered_config

    def interactive_setup(self) -> bool:
        """
        Interactive database setup.

        Returns:
            bool: True if setup successful
        """
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
                        if value:
                            value = int(value)
                    except ValueError:
                        self.console.print(f"[red]Invalid integer value for {field_name}[/red]")
                        return False

                # Add value if provided
                if value or is_required:
                    new_config[field_name] = value
                elif is_required and not value:
                    self.console.print(f"[red]Required field '{field_name}' cannot be empty[/red]")
                    return False

            self.console.print("[yellow]Testing connection...[/yellow]")

            if self.setup_from_config(new_config):
                self.console.print("[green]✅ Database setup successful![/green]")
                return True
            else:
                self.console.print("[red]❌ Database connection failed[/red]")
                return False

        except Exception as e:
            self.console.print(f"[red]Error during setup: {e}[/red]")
            return False

    def show_datasources(self) -> None:
        """Show all registered data sources."""
        try:
            registrations = self.datasource_store.list_data_sources()

            if not registrations:
                self.console.print("[yellow]No data sources registered[/yellow]")
                return

            ds_table = Table(title="📊 Registered Data Sources")
            ds_table.add_column("ID", style="cyan")
            ds_table.add_column("Name", style="green")
            ds_table.add_column("Type", style="blue")
            ds_table.add_column("Status", style="magenta")
            ds_table.add_column("Current", style="yellow")

            for reg in registrations:
                status = "✅ Active" if reg.is_active else "❌ Inactive"
                current = "👈" if reg.id == self.current_datasource_id else ""
                ds_table.add_row(reg.id[:8], reg.name, reg.type, status, current)

            self.console.print(ds_table)

        except Exception as e:
            self.console.print(f"[red]Failed to retrieve data sources: {e}[/red]")

    def add_datasource_interactive(self) -> None:
        """Add a new data source interactively."""
        self.console.print("[bold]Add Data Source[/bold]")

        # Get data source info
        name = Prompt.ask("Data source name")
        description = Prompt.ask("Description (optional)", default="")

        # Get supported datasources from factory
        supported_types = [ds.name for ds in get_supported_datasources()]
        db_type = Prompt.ask("Database type", choices=supported_types, default="postgres")

        try:
            # Get the expected config fields for this datasource type
            expected_fields = DataSourceFactory.get_datasource_config(db_type)

            # Build config interactively
            config = {}

            for field_name, field_info in expected_fields.items():
                is_required = field_info.is_required()
                description_text = getattr(field_info, 'description', field_name)

                # Handle password fields specially
                if 'password' in field_name.lower():
                    value = Prompt.ask(f"{description_text}", password=True)
                else:
                    prompt_text = f"{description_text}"
                    if is_required:
                        prompt_text += " (required)"

                    value = Prompt.ask(prompt_text)

                # Convert to appropriate type
                annotation = str(getattr(field_info, 'annotation', 'str'))
                if 'int' in annotation.lower() or 'port' in field_name.lower():
                    try:
                        if value:
                            value = int(value)
                    except ValueError:
                        self.console.print(f"[red]Invalid integer value for {field_name}[/red]")
                        return

                # Add value if provided
                if value or is_required:
                    config[field_name] = value
                elif is_required and not value:
                    self.console.print(f"[red]Required field '{field_name}' cannot be empty[/red]")
                    return

            # Register the data source
            with self.console.status("[yellow]Registering data source..."):
                ds_id = self.datasource_store.register_data_source(
                    name=name,
                    datasource_type=db_type,
                    config=config,
                    description=description if description else None
                )

            self.console.print(f"[green]✅ Data source registered with ID: {ds_id}[/green]")

            # Ask if they want to switch to this data source
            if Confirm.ask("Switch to this data source now?"):
                self.switch_datasource(ds_id)

        except Exception as e:
            self.console.print(f"[red]Failed to register data source: {e}[/red]")

    def switch_datasource(self, datasource_id: str) -> bool:
        """
        Switch to a different data source.

        Args:
            datasource_id: ID of the data source to switch to

        Returns:
            bool: True if switch successful
        """
        try:
            # Get the data source
            datasource = self.datasource_store.get_data_source(datasource_id)
            registration = self.datasource_store.get_registration(datasource_id)

            # Update current data source
            self.current_datasource = datasource
            self.current_datasource_id = datasource_id

            self.console.print(f"[green]✅ Switched to data source: {registration.name}[/green]")
            return True

        except Exception as e:
            self.console.print(f"[red]Failed to switch data source: {e}[/red]")
            return False

    def show_datasource_selection(self) -> None:
        """Show data source selection menu."""
        try:
            registrations = self.datasource_store.list_data_sources()

            if not registrations:
                self.console.print("[yellow]No data sources available. Use /add-datasource to register one.[/yellow]")
                return

            self.console.print("[bold]Available Data Sources:[/bold]")

            choices = []
            for i, reg in enumerate(registrations, 1):
                current = " (current)" if reg.id == self.current_datasource_id else ""
                self.console.print(f"{i}. {reg.name} ({reg.type}){current}")
                choices.append(str(i))

            choice = Prompt.ask("Select data source", choices=choices + ["q"])

            if choice != "q":
                selected_reg = registrations[int(choice) - 1]
                self.switch_datasource(selected_reg.id)

        except Exception as e:
            self.console.print(f"[red]Failed to show data source selection: {e}[/red]")

    def get_current_datasource_info(self) -> Dict[str, Any]:
        """
        Get information about the current data source.

        Returns:
            Dict containing current data source info
        """
        if not self.current_datasource_id:
            return {}

        try:
            registration = self.datasource_store.get_registration(self.current_datasource_id)
            return {
                "id": registration.id,
                "name": registration.name,
                "type": registration.type,
                "is_active": registration.is_active
            }
        except Exception:
            return {}
