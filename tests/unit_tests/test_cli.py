#!/usr/bin/env python3
"""
Quick test script for the Ryoma SQL CLI in development mode.
"""

import os
import sys
from pathlib import Path

# Add the ryoma_ai package to Python path
ryoma_ai_path = Path(__file__).parent / "packages" / "ryoma_ai"
sys.path.insert(0, str(ryoma_ai_path))

# Import and run the CLI
from ryoma_ai.cli.main import main

if __name__ == "__main__":
    # You can modify sys.argv to test different arguments
    # sys.argv = ["test_cli.py", "--setup"]  # Test setup mode
    # sys.argv = ["test_cli.py", "--help"]   # Test help

    main()
