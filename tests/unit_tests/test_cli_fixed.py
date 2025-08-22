#!/usr/bin/env python3
"""
Test the fixed CLI functionality
"""

import os
import sys
from pathlib import Path

# Add the ryoma_ai package to Python path
ryoma_ai_path = Path(__file__).parent / "packages" / "ryoma_ai"
sys.path.insert(0, str(ryoma_ai_path))

from ryoma_ai.cli.app import RyomaAI


def test_cli_with_sqlite():
    """Test CLI with SQLite database and basic mode."""
    print("🧪 Testing CLI with SQLite and basic mode...")

    cli = RyomaAI()

    # Configure for SQLite basic mode
    cli.config_manager.config["database"] = {"type": "sqlite", "database": ":memory:"}
    cli.config_manager.config["mode"] = "basic"

    # Setup datasource and agent
    if cli.datasource_manager.setup_from_config(cli.config_manager.config["database"]):
        print("✅ Datasource setup successful")

        if cli.agent_manager.setup_agent_manager(
            config=cli.config_manager.config,
            datasource=cli.datasource_manager.current_datasource,
        ):
            print("✅ Agent setup successful")

            # Create test table directly
            conn = cli.datasource_manager.current_datasource.connect()
            conn.raw_sql("CREATE TABLE users (id INTEGER, name TEXT, city TEXT)")
            conn.raw_sql(
                "INSERT INTO users VALUES (1, 'Alice', 'New York'), (2, 'Bob', 'London'), (3, 'Charlie', 'Tokyo')"
            )
            print("✅ Test data created")

            # Simulate a question (but don't actually process it interactively)
            print("CLI is ready to process questions!")
            print("Example questions you could ask:")
            print("- 'Show me all users'")
            print("- 'How many users are there?'")
            print("- 'Show me users from New York'")

            # Test the schema display (through display manager)
            print("\n🔍 Testing schema display:")
            try:
                schema = cli.datasource_manager.current_datasource.get_table_schema("")
                cli.display_manager.show_schema(schema)
            except Exception as e:
                print(f"Schema display error: {e}")

        else:
            print("❌ Agent setup failed")
    else:
        print("❌ Datasource setup failed")


if __name__ == "__main__":
    test_cli_with_sqlite()
