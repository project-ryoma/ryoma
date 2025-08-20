#!/usr/bin/env python3
"""
Demonstration of Ryoma SQL CLI usage.

This script shows how to use the Ryoma SQL CLI programmatically,
which can be useful for automation or integration into other tools.
"""

import os
import subprocess
import sys
from pathlib import Path

def run_cli_command(command: str) -> str:
    """Run a CLI command and return the output."""
    try:
        result = subprocess.run(
            ['ryoma-sql', '--help'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"
    except FileNotFoundError:
        return "Error: ryoma-sql command not found. Please install ryoma_ai package."

def demo_cli_help():
    """Demonstrate CLI help."""
    print("🔧 Ryoma SQL CLI Help:")
    print("=" * 50)
    
    help_output = run_cli_command("--help")
    print(help_output)

def demo_configuration():
    """Demonstrate configuration setup."""
    print("\n🔧 Configuration Example:")
    print("=" * 50)
    
    config_example = {
        "model": "gpt-4o",
        "mode": "enhanced", 
        "database": {
            "type": "postgres",
            "host": "localhost",
            "port": 5432,
            "database": "ecommerce",
            "user": "analytics_user",
            "password": "secure_password"
        }
    }
    
    import json
    print("Sample ~/.ryoma/config.json:")
    print(json.dumps(config_example, indent=2))

def demo_example_questions():
    """Show example questions that work well with the CLI."""
    print("\n💬 Example Natural Language Questions:")
    print("=" * 50)
    
    examples = [
        # Customer Analysis
        ("Customer Analysis", [
            "Who are our top 10 customers by total revenue?",
            "Which customers haven't placed orders in the last 30 days?",
            "Show me customer acquisition trends by month this year",
            "Find customers who have made more than 5 orders"
        ]),
        
        # Sales & Revenue
        ("Sales & Revenue", [
            "What are our best-selling products this quarter?",
            "Show me daily sales for the last 30 days", 
            "Which product categories generate the most revenue?",
            "Find all orders over $1000 from last month"
        ]),
        
        # Inventory & Products  
        ("Inventory & Products", [
            "Which products are running low in stock?",
            "Show me products that haven't sold in 60 days",
            "What's the average product rating by category?",
            "Find products with the highest return rates"
        ]),
        
        # Order Analysis
        ("Order Operations", [
            "Show me all pending orders from today",
            "Which orders were shipped late this week?", 
            "What's the average order processing time?",
            "Find orders with multiple items from the same product"
        ])
    ]
    
    for category, questions in examples:
        print(f"\n📊 {category}:")
        for i, question in enumerate(questions, 1):
            print(f"  {i}. {question}")

def demo_workflow():
    """Demonstrate the CLI workflow."""
    print("\n🔄 CLI Workflow Example:")
    print("=" * 50)
    
    workflow_steps = [
        "1. Start CLI: ryoma-sql",
        "2. Setup database (first time): /setup", 
        "3. Ask natural language question:",
        "   > Who are the top 5 customers by sales?",
        "",
        "4. Agent analyzes and generates SQL:",
        "   📊 Database Analysis: Finding relevant tables...",
        "   🔍 SQL Generation: Creating optimized query...",
        "",
        "5. Human approval workflow:",
        "   ┌─────────────────────────────────────────┐",
        "   │ SELECT c.name, SUM(o.total_amount)     │", 
        "   │ FROM customers c                        │",
        "   │ JOIN orders o ON c.id = o.customer_id   │",
        "   │ GROUP BY c.name                         │",
        "   │ ORDER BY SUM(o.total_amount) DESC       │",
        "   │ LIMIT 5;                                │",
        "   └─────────────────────────────────────────┘",
        "   Your decision: approve",
        "",
        "6. Query execution and results:",
        "   📊 Query Results",
        "   ┌─────────────────┬─────────────┐",
        "   │ Customer Name   │ Total Sales │", 
        "   ├─────────────────┼─────────────┤",
        "   │ Acme Corp       │ $125,000    │",
        "   │ Tech Solutions  │ $98,500     │",
        "   │ Global Systems  │ $87,200     │",
        "   └─────────────────┴─────────────┘"
    ]
    
    for step in workflow_steps:
        print(step)

def demo_advanced_features():
    """Show advanced CLI features."""
    print("\n⚡ Advanced Features:")
    print("=" * 50)
    
    features = [
        ("Error Recovery", "Automatic PostgreSQL case sensitivity fixes"),
        ("Schema Analysis", "Intelligent table and column discovery"),  
        ("Safety Validation", "Prevents dangerous queries (DROP, DELETE without WHERE)"),
        ("Multi-Database", "PostgreSQL, MySQL support with easy switching"),
        ("Agent Modes", "Basic (fast) → Enhanced (smart) → ReFoRCE (research-grade)"),
        ("Configuration", "Persistent settings in ~/.ryoma/config.json"),
        ("Interactive Commands", "/help, /schema, /config, /setup, /mode, /model")
    ]
    
    for feature, description in features:
        print(f"• {feature:20} - {description}")

def main():
    """Run the CLI demonstration."""
    print("🤖 Ryoma SQL CLI Demonstration")
    print("===============================")
    print()
    print("This demo shows the capabilities of the Ryoma SQL CLI,")
    print("a natural language to SQL interface with human-in-the-loop approval.")
    print()
    
    # Run demonstrations
    demo_cli_help()
    demo_configuration() 
    demo_example_questions()
    demo_workflow()
    demo_advanced_features()
    
    print("\n🚀 Getting Started:")
    print("=" * 50)
    print("1. Install: pip install ryoma_ai")
    print("2. Run: ryoma-sql --setup")
    print("3. Start asking questions in natural language!")
    print()
    print("For more help: ryoma-sql --help")

if __name__ == "__main__":
    main()