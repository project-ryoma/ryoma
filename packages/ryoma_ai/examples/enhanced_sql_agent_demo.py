"""
Enhanced SQL Agent Demo

This demo showcases the new capabilities of the enhanced SQL Agent including:
- Multi-step reasoning and query planning
- Intelligent schema linking and table selection
- Advanced error handling and recovery
- SQL safety validation and security checks
- Query optimization and explanation
"""

import os

from ryoma_ai.agent.query_planner import QueryPlannerAgent
from ryoma_ai.agent.schema_linking_agent import SchemaLinkingAgent
from ryoma_ai.agent.sql import SqlAgent
from ryoma_ai.agent.sql_error_handler import SqlErrorHandler
from ryoma_ai.agent.sql_safety_validator import SqlSafetyValidator
from ryoma_data.postgres import PostgresDataSource
from ryoma_ai.tool.sql_tool import (
    QueryExplanationTool,
    QueryOptimizationTool,
    QueryValidationTool,
    SchemaAnalysisTool,
    TableSelectionTool,
)


def setup_demo_datasource():
    """Setup a demo PostgreSQL datasource."""
    return PostgresDataSource(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", 5432)),
        database=os.getenv("POSTGRES_DB", "demo_db"),
        user=os.getenv("POSTGRES_USER", "demo_user"),
        password=os.getenv("POSTGRES_PASSWORD", "demo_password"),
        db_schema=os.getenv("POSTGRES_SCHEMA", "public"),
    )


def demo_basic_enhanced_agent():
    """Demonstrate basic enhanced SQL agent usage."""
    print("=== Basic Enhanced SQL Agent Demo ===")

    datasource = setup_demo_datasource()

    # Create enhanced SQL agent with safety features
    sql_agent = SqlAgent(
        model="gpt-3.5-turbo",
        datasource=datasource,
        use_enhanced_mode=True,
        safety_config={
            "max_result_rows": 1000,
            "max_nested_queries": 2,
            "blocked_functions": ["LOAD_FILE", "INTO OUTFILE"],
        },
    )

    # Example questions that showcase different capabilities
    questions = [
        "Show me the top 10 customers by total purchase amount",
        "What are the most popular products sold last month?",
        "Find customers who haven't made any purchases in the last 6 months",
        "Calculate the average order value by customer segment",
    ]

    for question in questions:
        print(f"\nQuestion: {question}")
        try:
            response = sql_agent.invoke(question)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")


def demo_schema_linking():
    """Demonstrate intelligent schema linking capabilities."""
    print("\n=== Schema Linking Demo ===")

    datasource = setup_demo_datasource()
    schema_agent = SchemaLinkingAgent(model="gpt-3.5-turbo", datasource=datasource)

    questions = [
        "Show me customer purchase history",
        "What products are running low in inventory?",
        "Which employees have the highest sales performance?",
    ]

    for question in questions:
        print(f"\nAnalyzing: {question}")
        try:
            analysis = schema_agent.analyze_schema_relationships(question)
            print(
                f"Relevant tables: {[t['table'] for t in analysis['relevant_tables'][:3]]}"
            )
            print(f"Confidence: {analysis['confidence_score']}")

            # Show table selection
            table_suggestions = schema_agent.suggest_table_selection(
                question, max_tables=3
            )
            for suggestion in table_suggestions:
                print(f"  - {suggestion['table']} (score: {suggestion['score']:.2f})")
        except Exception as e:
            print(f"Error: {e}")


def demo_query_planning():
    """Demonstrate query planning and optimization."""
    print("\n=== Query Planning Demo ===")

    datasource = setup_demo_datasource()
    planner = QueryPlannerAgent(model="gpt-3.5-turbo", datasource=datasource)

    complex_questions = [
        "Show me the monthly sales trend for the top 5 product categories, including year-over-year growth",
        "Find customers who bought products from at least 3 different categories and spent more than $1000 total",
        "Calculate the customer lifetime value and segment customers into high, medium, and low value groups",
    ]

    for question in complex_questions:
        print(f"\nPlanning for: {question}")
        try:
            plan = planner.create_query_plan(question)
            print(f"Complexity: {plan.complexity.value}")
            print(f"Steps: {len(plan.steps)}")
            print(f"Estimated time: {plan.total_estimated_time:.1f}s")

            # Show plan explanation
            explanation = planner.explain_plan(plan)
            print(f"Plan details:\n{explanation[:200]}...")

        except Exception as e:
            print(f"Error: {e}")


def demo_safety_validation():
    """Demonstrate SQL safety validation."""
    print("\n=== Safety Validation Demo ===")

    datasource = setup_demo_datasource()
    validator = SqlSafetyValidator(datasource=datasource)

    # Test queries with different safety levels
    test_queries = [
        ("SELECT * FROM customers LIMIT 10", "Safe query"),
        ("SELECT * FROM customers", "Query without limit"),
        ("DELETE FROM customers WHERE id = 1", "Safe delete with WHERE"),
        ("DELETE FROM customers", "Dangerous delete without WHERE"),
        ("DROP TABLE customers", "Blocked operation"),
        ("UPDATE customers SET status = 'inactive'", "Update without WHERE"),
        ("SELECT LOAD_FILE('/etc/passwd')", "Dangerous function usage"),
    ]

    for query, description in test_queries:
        print(f"\nTesting: {description}")
        print(f"Query: {query}")

        try:
            result = validator.validate_query(query)
            print(f"Safety Level: {result.safety_level.value}")
            print(f"Execution Allowed: {result.execution_allowed}")

            if result.violations:
                print("Violations:")
                for violation in result.violations:
                    print(f"  - {violation.message}")

            if result.sanitized_query:
                print(f"Sanitized: {result.sanitized_query}")

        except Exception as e:
            print(f"Error: {e}")


def demo_error_handling():
    """Demonstrate advanced error handling."""
    print("\n=== Error Handling Demo ===")

    datasource = setup_demo_datasource()
    error_handler = SqlErrorHandler(datasource=datasource)

    # Simulate common SQL errors
    error_scenarios = [
        (
            "SELECT * FROM non_existent_table",
            "Table 'non_existent_table' doesn't exist",
        ),
        ("SELECT invalid_column FROM customers", "Unknown column 'invalid_column'"),
        ("SELECT name, email FROM customers WHERE", "Syntax error near 'WHERE'"),
        ("SELECT amount / 0 FROM orders", "Division by zero error"),
        (
            "SELECT * FROM customers ORDER BY",
            "Syntax error: missing column after ORDER BY",
        ),
    ]

    for query, error_msg in error_scenarios:
        print(f"\nHandling error for: {query}")
        print(f"Error: {error_msg}")

        try:
            sql_error = error_handler.analyze_error(error_msg, query)
            print(f"Error Type: {sql_error.error_type.value}")

            strategies = error_handler.suggest_recovery_strategies(sql_error)
            print(f"Recovery strategies ({len(strategies)}):")
            for strategy in strategies[:2]:  # Show top 2 strategies
                print(
                    f"  - {strategy.description} (confidence: {strategy.confidence:.2f})"
                )

            # Try auto-correction
            corrected = error_handler.auto_correct_query(query, error_msg)
            if corrected:
                print(f"Auto-corrected: {corrected}")
            else:
                print("No automatic correction available")

        except Exception as e:
            print(f"Error in error handling: {e}")


def demo_advanced_tools():
    """Demonstrate advanced SQL tools."""
    print("\n=== Advanced Tools Demo ===")

    datasource = setup_demo_datasource()

    # Test different tools
    tools = [
        (SchemaAnalysisTool(), {"datasource": datasource, "table_name": "customers"}),
        (
            QueryValidationTool(),
            {"query": "SELECT * FROM customers", "datasource": datasource},
        ),
        (
            TableSelectionTool(),
            {"question": "Show customer orders", "datasource": datasource},
        ),
        (
            QueryOptimizationTool(),
            {
                "query": "SELECT * FROM customers ORDER BY name",
                "datasource": datasource,
            },
        ),
        (
            QueryExplanationTool(),
            {
                "query": "SELECT COUNT(*) FROM orders WHERE date > '2023-01-01'",
                "datasource": datasource,
            },
        ),
    ]

    for tool, params in tools:
        print(f"\nTesting {tool.name}:")
        try:
            result = tool._run(**params)
            print(f"Result: {result[:200]}...")
        except Exception as e:
            print(f"Error: {e}")


def demo_configuration_options():
    """Demonstrate different configuration options."""
    print("\n=== Configuration Options Demo ===")

    datasource = setup_demo_datasource()

    # Different safety configurations
    configs = [
        {
            "name": "Strict Security",
            "config": {
                "max_result_rows": 100,
                "max_nested_queries": 1,
                "blocked_functions": ["LOAD_FILE", "INTO OUTFILE", "SYSTEM"],
                "protected_tables": ["users", "passwords", "admin"],
            },
        },
        {
            "name": "Development Mode",
            "config": {
                "max_result_rows": 10000,
                "max_nested_queries": 5,
                "blocked_functions": ["LOAD_FILE", "INTO OUTFILE"],
                "protected_tables": ["information_schema"],
            },
        },
        {
            "name": "Production Mode",
            "config": {
                "max_result_rows": 1000,
                "max_nested_queries": 3,
                "blocked_functions": ["LOAD_FILE", "INTO OUTFILE", "SYSTEM", "EXEC"],
                "protected_tables": [
                    "information_schema",
                    "mysql",
                    "performance_schema",
                ],
            },
        },
    ]

    test_query = "SELECT * FROM customers ORDER BY created_date"

    for config_info in configs:
        print(f"\nTesting {config_info['name']}:")

        validator = SqlSafetyValidator(
            datasource=datasource, safety_config=config_info["config"]
        )

        result = validator.validate_query(test_query)
        print(f"  Safety Level: {result.safety_level.value}")
        print(f"  Violations: {len(result.violations)}")

        # Show recommendations
        recommendations = validator.get_safety_recommendations(test_query)
        print(f"  Recommendations: {len(recommendations)} items")


def main():
    """Run all demos."""
    print("Enhanced SQL Agent Comprehensive Demo")
    print("=" * 50)

    try:
        demo_basic_enhanced_agent()
        demo_schema_linking()
        demo_query_planning()
        demo_safety_validation()
        demo_error_handling()
        demo_advanced_tools()
        demo_configuration_options()

        print("\n" + "=" * 50)
        print("Demo completed successfully!")
        print("\nKey Features Demonstrated:")
        print("✓ Multi-step reasoning and query planning")
        print("✓ Intelligent schema linking")
        print("✓ Advanced error handling and recovery")
        print("✓ SQL safety validation")
        print("✓ Query optimization suggestions")
        print("✓ Configurable security policies")

    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        print("Make sure you have:")
        print("1. PostgreSQL database running")
        print("2. Correct environment variables set")
        print("3. Required dependencies installed")


if __name__ == "__main__":
    main()
