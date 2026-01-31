#!/usr/bin/env python3
"""
Demonstration of the Ryoma SDK.
Shows how users can create SQL agents with different modes using the simple Ryoma API.
"""

from unittest.mock import Mock

from ryoma_ai import Ryoma
from ryoma_data.sql import DataSource


def create_mock_datasource():
    """Create a mock datasource for demonstration."""
    mock_datasource = Mock(spec=DataSource)
    mock_datasource.id = "mock_datasource"
    mock_datasource.query.return_value = "Mock query result"
    return mock_datasource


def demo_ryoma_simple():
    """Demonstrate the simple Ryoma API."""

    print("🔧 Ryoma Simple API Demo")
    print("=" * 50)

    # Create a mock datasource
    mock_datasource = create_mock_datasource()

    print("\n1. Creating Ryoma with single datasource:")
    print("   ryoma = Ryoma(datasource=datasource)")

    ryoma = Ryoma(datasource=mock_datasource)

    print(f"   ✅ Created: {ryoma}")
    print(f"   📊 Active datasource: {ryoma.active}")

    print("\n2. Creating Basic SQL Agent:")
    print("   agent = ryoma.sql_agent(model='gpt-4', mode='basic')")

    agent = ryoma.sql_agent(model="gpt-4", mode="basic")

    print(f"   ✅ Created: {type(agent).__name__}")
    print(f"   🔧 Tools: {len(agent.tools)} tools")

    print("\n3. Creating Enhanced SQL Agent:")
    print("   agent = ryoma.sql_agent(model='gpt-4', mode='enhanced')")

    agent = ryoma.sql_agent(model="gpt-4", mode="enhanced")

    print(f"   ✅ Created: {type(agent).__name__}")
    print(f"   🔧 Tools: {len(agent.tools)} tools")

    print("\n4. Creating ReFoRCE SQL Agent:")
    print("   agent = ryoma.sql_agent(model='gpt-4', mode='reforce')")

    agent = ryoma.sql_agent(model="gpt-4", mode="reforce")

    print(f"   ✅ Created: {type(agent).__name__}")
    print(f"   🔧 Tools: {len(agent.tools)} tools")


def demo_ryoma_multi_datasource():
    """Demonstrate multi-datasource support."""

    print("\n\n🔧 Ryoma Multi-Datasource Demo")
    print("=" * 50)

    # Create mock datasources
    sales_ds = create_mock_datasource()
    sales_ds.id = "sales_db"
    marketing_ds = create_mock_datasource()
    marketing_ds.id = "marketing_db"

    print("\n1. Creating Ryoma without datasource:")
    print("   ryoma = Ryoma()")

    ryoma = Ryoma()

    print(f"   ✅ Created: {ryoma}")

    print("\n2. Adding multiple datasources:")
    print("   ryoma.add_datasource(sales_ds, name='sales')")
    print("   ryoma.add_datasource(marketing_ds, name='marketing')")

    ryoma.add_datasource(sales_ds, name="sales")
    ryoma.add_datasource(marketing_ds, name="marketing")

    print(f"   ✅ Datasources: {ryoma.list_datasources()}")
    print(f"   📊 Active: {ryoma.active}")

    print("\n3. Switching active datasource:")
    print("   ryoma.set_active('marketing')")

    ryoma.set_active("marketing")

    print(f"   ✅ Active now: {ryoma.active}")

    print("\n4. Creating agent (uses active datasource):")
    print("   agent = ryoma.sql_agent(model='gpt-4', mode='enhanced')")

    agent = ryoma.sql_agent(model="gpt-4", mode="enhanced")

    print(f"   ✅ Created: {type(agent).__name__}")


def demo_usage_patterns():
    """Demonstrate common usage patterns."""

    print("\n\n💡 Common Usage Patterns")
    print("=" * 50)

    print("\n1. Simple - Single Datasource:")
    print("""
   from ryoma_ai import Ryoma
   from ryoma_data import DataSource

   datasource = DataSource("postgres", host="localhost", database="mydb", ...)
   ryoma = Ryoma(datasource=datasource)
   agent = ryoma.sql_agent(model="gpt-4", mode="enhanced")

   result = agent.stream("Show top customers by revenue")
""")

    print("\n2. Multiple Datasources:")
    print("""
   from ryoma_ai import Ryoma
   from ryoma_data import DataSource

   ryoma = Ryoma()
   ryoma.add_datasource(sales_db, name="sales")
   ryoma.add_datasource(marketing_db, name="marketing")

   agent = ryoma.sql_agent(model="gpt-4", mode="enhanced")

   # Query sales database
   agent.stream("Show top products")

   # Switch to marketing
   ryoma.set_active("marketing")
   agent.stream("Show campaign performance")
""")

    print("\n3. Mode-specific configurations:")
    configurations = {
        "basic": {
            "use_case": "Simple queries and testing",
            "tools": 3,
            "safety": "Basic validation only",
        },
        "enhanced": {
            "use_case": "Advanced analytics and optimization",
            "tools": 5,
            "safety": "Comprehensive validation",
        },
        "reforce": {
            "use_case": "Production workloads and complex reasoning",
            "tools": 5,
            "safety": "Enterprise-grade validation",
        },
    }

    for mode, config in configurations.items():
        print(f"\n   {mode.upper()} Mode:")
        print(f"   📋 Use case: {config['use_case']}")
        print(f"   🔧 Tools: {config['tools']}")
        print(f"   🛡️  Safety: {config['safety']}")


if __name__ == "__main__":
    demo_ryoma_simple()
    demo_ryoma_multi_datasource()
    demo_usage_patterns()

    print("\n\n✨ Summary:")
    print("Ryoma provides a simple, clean API for working with SQL databases.")
    print("Just create a Ryoma instance, add your datasources, and create agents!")
