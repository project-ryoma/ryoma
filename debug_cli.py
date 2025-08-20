#!/usr/bin/env python3
"""
Debug script to test CLI functionality step by step.
"""

import sys
import os
import json
import traceback
from pathlib import Path

# Add the ryoma_ai package to Python path
ryoma_ai_path = Path(__file__).parent / "packages" / "ryoma_ai"
sys.path.insert(0, str(ryoma_ai_path))

from ryoma_ai.cli.main import RyomaSQL
from ryoma_ai.datasource.factory import DataSourceFactory
from ryoma_ai.agent.sql import SqlAgent
from ryoma_ai.models.agent import SqlAgentMode

def test_datasource_factory():
    """Test if the datasource factory works."""
    print("🔧 Testing DataSource Factory...")
    
    try:
        # Test with SQLite (simpler than Postgres for testing)
        # Use proper parameter mapping as in the CLI
        datasource = DataSourceFactory.create_datasource("sqlite", connection_url=":memory:")
        
        # Test a simple query
        result = datasource.query("SELECT 1 as test")
        print(f"✅ DataSource factory works: {result}")
        return datasource
        
    except Exception as e:
        print(f"❌ DataSource factory failed: {e}")
        traceback.print_exc()
        return None

def test_agent_creation(datasource):
    """Test if the SqlAgent can be created."""
    print("🤖 Testing SqlAgent creation...")
    
    try:
        agent = SqlAgent(
            model="gpt-4o",
            mode=SqlAgentMode.enhanced,
            datasource=datasource
        )
        print(f"✅ SqlAgent created successfully: {type(agent)}")
        return agent
        
    except Exception as e:
        print(f"❌ SqlAgent creation failed: {e}")
        traceback.print_exc()
        return None

def test_agent_workflow(agent):
    """Test if the agent workflow works."""
    print("⚡ Testing Agent workflow...")
    
    try:
        # Test a simple question that shouldn't need database access
        print("Testing agent stream method...")
        result = agent.stream("What tables are in the database?", display=False)
        print(f"✅ Agent stream works: {type(result)}")
        
        # Check current state
        current_state = agent.get_current_state()
        print(f"Current state: {current_state}")
        
        if current_state:
            print(f"State values: {current_state.values.keys() if current_state.values else 'None'}")
            if hasattr(current_state, 'next'):
                print(f"Next steps: {current_state.next}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent workflow failed: {e}")
        traceback.print_exc()
        return False

def test_cli_components():
    """Test CLI components individually."""
    print("🖥️  Testing CLI components...")
    
    try:
        cli = RyomaSQL()
        print(f"✅ CLI created successfully")
        
        # Test configuration loading
        print(f"Config loaded: {bool(cli.config)}")
        print(f"Default config: {json.dumps(cli.config, indent=2)}")
        
        return cli
        
    except Exception as e:
        print(f"❌ CLI creation failed: {e}")
        traceback.print_exc()
        return None

def run_debug_tests():
    """Run all debug tests."""
    print("🔍 Ryoma CLI Debug Tests")
    print("=" * 50)
    
    # Test 1: DataSource Factory
    datasource = test_datasource_factory()
    if not datasource:
        return
    
    # Test 2: Agent Creation
    agent = test_agent_creation(datasource)
    if not agent:
        return
        
    # Test 3: Agent Workflow
    workflow_works = test_agent_workflow(agent)
    if not workflow_works:
        return
        
    # Test 4: CLI Components
    cli = test_cli_components()
    if not cli:
        return
    
    print("🎉 All basic tests passed!")
    print("\nNow testing CLI with simple database setup...")
    
    # Test 5: Full CLI with SQLite
    try:
        # Override the default config to use SQLite
        cli.config["database"] = {
            "type": "sqlite",
            "database": ":memory:"
        }
        
        if cli._setup_datasource(cli.config["database"]):
            print("✅ CLI datasource setup successful")
            
            if cli._setup_agent():
                print("✅ CLI agent setup successful")
                
                # Test a simple question processing
                print("Testing _process_question with debug output...")
                cli._process_question("What tables are in the database?")
            else:
                print("❌ CLI agent setup failed")
        else:
            print("❌ CLI datasource setup failed")
            
    except Exception as e:
        print(f"❌ Full CLI test failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    run_debug_tests()