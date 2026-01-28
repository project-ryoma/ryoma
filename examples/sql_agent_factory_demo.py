#!/usr/bin/env python3
"""
Demonstration of the SqlAgent factory pattern and service-based API.
Shows how users can create SQL agents with different modes using both:
1. AgentBuilder (recommended)
2. SqlAgent factory with store injection
"""

from unittest.mock import Mock

from langchain_core.stores import InMemoryStore

from ryoma_ai.agent.sql import (
    BasicSqlAgent,
    EnhancedSqlAgentImpl,
    ReFoRCESqlAgentImpl,
    SqlAgent,
)
from ryoma_ai.domain.constants import StoreKeys
from ryoma_ai.models.agent import SqlAgentMode
from ryoma_ai.services import AgentBuilder, DataSourceService
from ryoma_ai.infrastructure.datasource_repository import StoreBasedDataSourceRepository
from ryoma_data.sql import DataSource


def create_mock_datasource():
    """Create a mock datasource for demonstration."""
    mock_datasource = Mock(spec=DataSource)
    mock_datasource.id = "mock_datasource"
    mock_datasource.query.return_value = "Mock query result"
    return mock_datasource


def demo_agent_builder():
    """Demonstrate the recommended AgentBuilder pattern."""

    print("🔧 AgentBuilder Pattern Demo (Recommended)")
    print("=" * 50)

    # Create a mock datasource
    mock_datasource = create_mock_datasource()

    # Set up services
    store = InMemoryStore()
    repo = StoreBasedDataSourceRepository(store)
    datasource_service = DataSourceService(repo)
    datasource_service.add_datasource(mock_datasource)

    # Create builder
    builder = AgentBuilder(datasource_service)

    print("\n1. Creating Basic SQL Agent:")
    print("   builder.build_sql_agent(model='gpt-4', mode='basic')")

    basic_agent = builder.build_sql_agent(model="gpt-4", mode="basic")

    print(f"   ✅ Created: {type(basic_agent).__name__}")
    print(f"   🔧 Tools: {len(basic_agent.tools)} tools")
    print(f"   📝 Tools: {[tool.name for tool in basic_agent.tools]}")

    print("\n2. Creating Enhanced SQL Agent:")
    print("   builder.build_sql_agent(model='gpt-4', mode='enhanced')")

    enhanced_agent = builder.build_sql_agent(model="gpt-4", mode="enhanced")

    print(f"   ✅ Created: {type(enhanced_agent).__name__}")
    print(f"   🔧 Tools: {len(enhanced_agent.tools)} tools")
    print(f"   📝 Tools: {[tool.name for tool in enhanced_agent.tools]}")

    print("\n3. Creating ReFoRCE SQL Agent:")
    print("   builder.build_sql_agent(model='gpt-4', mode='reforce')")

    reforce_agent = builder.build_sql_agent(model="gpt-4", mode="reforce")

    print(f"   ✅ Created: {type(reforce_agent).__name__}")
    print(f"   🔧 Tools: {len(reforce_agent.tools)} tools")
    print(f"   📝 Tools: {[tool.name for tool in reforce_agent.tools]}")


def demo_sql_agent_factory():
    """Demonstrate the SqlAgent factory pattern with store injection."""

    print("\n\n🔧 SqlAgent Factory Pattern Demo")
    print("=" * 50)

    # Create a mock datasource
    mock_datasource = create_mock_datasource()

    # Create store and inject datasource
    store = InMemoryStore()
    store.mset([(StoreKeys.ACTIVE_DATASOURCE, mock_datasource)])

    print("\n1. Creating Basic SQL Agent:")
    print("   SqlAgent(model='gpt-4', mode='basic', store=store)")

    basic_agent = SqlAgent(model="gpt-4", mode="basic", store=store)

    print(f"   ✅ Created: {type(basic_agent).__name__}")
    print(f"   📊 Mode: {basic_agent.mode}")
    print(f"   🔧 Tools: {len(basic_agent.tools)} tools")
    print(f"   📝 Tools: {[tool.name for tool in basic_agent.tools]}")

    print("\n2. Creating Enhanced SQL Agent:")
    print("   SqlAgent(model='gpt-4', mode='enhanced', store=store)")

    enhanced_agent = SqlAgent(
        model="gpt-4",
        mode=SqlAgentMode.enhanced,
        safety_config={"enable_validation": True},
        store=store,
    )

    print(f"   ✅ Created: {type(enhanced_agent).__name__}")
    print(f"   📊 Mode: {enhanced_agent.mode}")
    print(f"   🔧 Tools: {len(enhanced_agent.tools)} tools")
    print(f"   📝 Tools: {[tool.name for tool in enhanced_agent.tools]}")

    print("\n3. Creating ReFoRCE SQL Agent:")
    print("   SqlAgent(model='gpt-4', mode='reforce', store=store)")

    reforce_agent = SqlAgent(
        model="gpt-4",
        mode="reforce",
        safety_config={"enable_advanced_validation": True},
        store=store,
    )

    print(f"   ✅ Created: {type(reforce_agent).__name__}")
    print(f"   📊 Mode: {reforce_agent.mode}")
    print(f"   🔧 Tools: {len(reforce_agent.tools)} tools")
    print(f"   📝 Tools: {[tool.name for tool in reforce_agent.tools]}")

    print("\n4. Default Mode (when no mode specified):")
    print("   SqlAgent(model='gpt-4', store=store)")

    default_agent = SqlAgent(model="gpt-4", store=store)

    print(f"   ✅ Created: {type(default_agent).__name__}")
    print(f"   📊 Mode: {default_agent.mode}")
    print(f"   🔧 Tools: {len(default_agent.tools)} tools")

    print("\n5. Testing Basic Agent Functionality:")
    try:
        basic_agent.analyze_schema("test query")
    except NotImplementedError as e:
        print(f"   ✅ Basic agent correctly raises: {e}")


def demo_direct_instantiation():
    """Demonstrate direct instantiation of specific agent types."""

    print("\n\n🎯 Direct Instantiation Demo")
    print("=" * 50)

    mock_datasource = create_mock_datasource()
    store = InMemoryStore()
    store.mset([(StoreKeys.ACTIVE_DATASOURCE, mock_datasource)])

    print("\n1. Direct BasicSqlAgent instantiation:")
    basic = BasicSqlAgent(model="gpt-4", store=store)
    print(f"   ✅ Created: {type(basic).__name__}")

    print("\n2. Direct EnhancedSqlAgentImpl instantiation:")
    enhanced = EnhancedSqlAgentImpl(model="gpt-4", store=store)
    print(f"   ✅ Created: {type(enhanced).__name__}")

    print("\n3. Direct ReFoRCESqlAgentImpl instantiation:")
    reforce = ReFoRCESqlAgentImpl(model="gpt-4", store=store)
    print(f"   ✅ Created: {type(reforce).__name__}")


def demo_usage_patterns():
    """Demonstrate common usage patterns."""

    print("\n\n💡 Common Usage Patterns")
    print("=" * 50)

    print("\n1. Recommended: Using AgentBuilder")
    print("""
   from ryoma_ai.services import AgentBuilder, DataSourceService
   from ryoma_ai.infrastructure.datasource_repository import StoreBasedDataSourceRepository
   from langchain_core.stores import InMemoryStore
   from ryoma_data.sql import DataSource

   # Setup
   datasource = DataSource("postgres", host="localhost", database="mydb", ...)
   store = InMemoryStore()
   repo = StoreBasedDataSourceRepository(store)
   datasource_service = DataSourceService(repo)
   datasource_service.add_datasource(datasource)

   # Build agent
   builder = AgentBuilder(datasource_service)
   agent = builder.build_sql_agent(model="gpt-4", mode="enhanced")

   # Use agent
   result = agent.stream("Show top customers by revenue")
""")

    print("\n2. Alternative: Direct SqlAgent with store")
    print("""
   from ryoma_ai.agent.sql import SqlAgent
   from ryoma_ai.domain.constants import StoreKeys
   from langchain_core.stores import InMemoryStore
   from ryoma_data.sql import DataSource

   # Setup datasource and store
   datasource = DataSource("postgres", host="localhost", database="mydb", ...)
   store = InMemoryStore()
   store.mset([(StoreKeys.ACTIVE_DATASOURCE, datasource)])

   # Create agent
   agent = SqlAgent(model="gpt-4", mode="enhanced", store=store)

   # Use agent
   result = agent.stream("Show top customers by revenue")
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
    demo_agent_builder()
    demo_sql_agent_factory()
    demo_direct_instantiation()
    demo_usage_patterns()

    print("\n\n✨ Summary:")
    print("The recommended approach is to use AgentBuilder for cleaner code.")
    print("The SqlAgent factory pattern still works but requires store injection.")
    print("Both patterns provide the same SQL agent capabilities!")
