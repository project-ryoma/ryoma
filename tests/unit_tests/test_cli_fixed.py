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

from ryoma_ai.cli.main import RyomaSQL


def test_cli_with_sqlite():
    """Test CLI with SQLite database and basic mode."""
    print("🧪 Testing CLI with SQLite and basic mode...")

    cli = RyomaSQL()

    # Configure for SQLite basic mode
    cli.config["database"] = {"type": "sqlite", "database": ":memory:"}
    cli.config["mode"] = "basic"

    # Setup datasource and agent
    if cli._setup_datasource(cli.config["database"]):
        print("✅ Datasource setup successful")

        if cli._setup_agent():
            print("✅ Agent setup successful")

            # Create test table directly
            conn = cli.datasource.connect()
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

            # Test the schema display
            print("\n🔍 Testing schema display:")
            cli._show_schema()

        else:
            print("❌ Agent setup failed")
    else:
        print("❌ Datasource setup failed")


if __name__ == "__main__":
    test_cli_with_sqlite()
