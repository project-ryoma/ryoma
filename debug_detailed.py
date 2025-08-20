#!/usr/bin/env python3
"""
Detailed debug script to trace exactly what happens in the agent workflow.
"""

import sys
import os
import json
import traceback
from pathlib import Path

# Add the ryoma_ai package to Python path
ryoma_ai_path = Path(__file__).parent / "packages" / "ryoma_ai"
sys.path.insert(0, str(ryoma_ai_path))

from ryoma_ai.datasource.factory import DataSourceFactory
from ryoma_ai.agent.sql import SqlAgent
from ryoma_ai.models.agent import SqlAgentMode
from langchain_core.messages import HumanMessage

def test_agent_detailed():
    """Detailed test of agent functionality."""
    print("🔍 Detailed Agent Debug")
    print("=" * 50)
    
    # Create datasource
    datasource = DataSourceFactory.create_datasource("sqlite", connection_url=":memory:")
    print("✅ DataSource created")
    
    # Create tables for testing using the direct connection
    conn = datasource.connect()
    conn.raw_sql("CREATE TABLE users (id INTEGER, name TEXT)")
    conn.raw_sql("INSERT INTO users VALUES (1, 'Alice'), (2, 'Bob')")
    print("✅ Test table created with data")
    
    # Create agent
    agent = SqlAgent(
        model="gpt-4o",
        mode=SqlAgentMode.enhanced,
        datasource=datasource
    )
    print("✅ Agent created")
    
    # Check agent properties
    print(f"Agent type: {type(agent)}")
    print(f"Agent config: {agent.config}")
    print(f"Agent workflow: {agent.workflow}")
    
    # Test message formatting
    question = "What tables are in the database?"
    formatted = agent._format_messages(question)
    print(f"Formatted message: {formatted}")
    
    # Check initial state
    initial_state = agent.get_current_state()
    print(f"Initial state: {initial_state}")
    
    # Stream with debug
    print("\n🚀 Starting stream...")
    try:
        # Manually pass formatted messages
        result_generator = agent.workflow.stream(
            formatted, config=agent.config, stream_mode="values"
        )
        
        print("Stream generator created, iterating...")
        for i, event in enumerate(result_generator):
            print(f"Event {i}: {type(event)} - {event}")
            if i > 10:  # Safety break
                print("Breaking after 10 events")
                break
        
        # Check final state
        final_state = agent.get_current_state()
        print(f"Final state after manual stream: {final_state}")
        
        if final_state and final_state.values:
            print(f"Final state values keys: {final_state.values.keys()}")
            messages = final_state.values.get("messages", [])
            print(f"Messages count: {len(messages)}")
            for i, msg in enumerate(messages):
                print(f"Message {i}: {type(msg)} - {msg.content[:100] if hasattr(msg, 'content') else str(msg)[:100]}")
        
    except Exception as e:
        print(f"❌ Stream failed: {e}")
        traceback.print_exc()

def test_basic_mode():
    """Test with basic mode to see if it's a mode-specific issue."""
    print("\n🔧 Testing Basic Mode")
    print("=" * 30)
    
    # Create datasource  
    datasource = DataSourceFactory.create_datasource("sqlite", connection_url=":memory:")
    conn = datasource.connect()
    conn.raw_sql("CREATE TABLE users (id INTEGER, name TEXT)")
    
    # Create basic agent
    agent = SqlAgent(
        model="gpt-4o",
        mode=SqlAgentMode.basic,
        datasource=datasource
    )
    print("✅ Basic agent created")
    
    # Test workflow
    question = "Show me the users table"
    try:
        result_generator = agent.stream(question, display=False)
        print("Stream started...")
        
        # Just consume the generator
        for event in result_generator:
            pass
        
        final_state = agent.get_current_state()
        print(f"Basic mode final state: {final_state}")
        
    except Exception as e:
        print(f"❌ Basic mode failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_agent_detailed()
    test_basic_mode()