"""
Apache Iceberg Data Source Example

This example demonstrates how to use the Ryoma AI framework with Apache Iceberg
tables, leveraging rich catalog metadata for enhanced text-to-SQL capabilities.
"""

import os

from ryoma_ai.agent.sql import SqlAgent
from ryoma_ai.datasource.iceberg import IcebergDataSource


def example_iceberg_rest_catalog():
    """Example using Iceberg REST catalog."""
    print("=== Iceberg REST Catalog Example ===")

    # Create Iceberg data source with REST catalog
    iceberg_ds = IcebergDataSource(
        catalog_name="production",
        catalog_type="rest",
        catalog_uri="http://localhost:8181",  # Iceberg REST catalog URI
        warehouse="s3a://warehouse/path",
        properties={
            "s3.endpoint": "http://localhost:9000",  # MinIO/S3 endpoint
            "s3.access-key-id": os.getenv("AWS_ACCESS_KEY_ID", "admin"),
            "s3.secret-access-key": os.getenv("AWS_SECRET_ACCESS_KEY", "password"),
        },
    )

    # Get catalog information with rich metadata
    print("Getting catalog information...")
    catalog = iceberg_ds.get_catalog()
    print(f"Catalog: {catalog.catalog_name}")

    for schema in catalog.schemas or []:
        print(f"  Schema: {schema.schema_name}")
        for table in schema.tables or []:
            print(f"    Table: {table.table_name}")
            if table.profile:
                print(
                    f"      Rows: {table.profile.row_count:,}"
                    if table.profile.row_count
                    else "      Rows: Unknown"
                )
                print(f"      Columns: {table.profile.column_count}")
                print(
                    f"      Quality: {table.profile.completeness_score:.1%}"
                    if table.profile.completeness_score
                    else ""
                )

            # Show column details with enhanced metadata
            for col in table.columns[:3]:  # Show first 3 columns
                print(f"        Column: {col.name} ({col.type})")
                if col.profile:
                    if col.profile.null_percentage is not None:
                        print(f"          NULL: {col.profile.null_percentage:.1f}%")
                    if col.profile.distinct_ratio is not None:
                        print(
                            f"          Distinct ratio: {col.profile.distinct_ratio:.2f}"
                        )


def example_iceberg_sql_agent():
    """Example using Iceberg with SQL Agent for text-to-SQL."""
    print("\n=== Iceberg SQL Agent Example ===")

    # Create Iceberg data source
    iceberg_ds = IcebergDataSource(
        catalog_name="analytics",
        catalog_type="rest",
        catalog_uri="http://localhost:8181",
        warehouse="s3a://warehouse/analytics",
        properties={"io-impl": "org.apache.iceberg.aws.s3.S3FileIO"},
    )

    # Create enhanced SQL agent with Iceberg
    sql_agent = SqlAgent(
        model="gpt-4",
        datasource=iceberg_ds,
        use_enhanced_mode=True,
        safety_config={
            "max_result_rows": 1000,
            "blocked_functions": ["DROP", "DELETE"],
        },
    )

    # Example questions leveraging Iceberg's rich metadata
    questions = [
        "Show me the top 10 products by sales volume from the sales table",
        "What's the average order value by customer segment?",
        "Find customers who haven't purchased anything in the last 6 months",
        "Show the monthly revenue trend for the past year",
    ]

    for question in questions:
        print(f"\nQuestion: {question}")
        try:
            # The SQL agent will use Iceberg's metadata for better schema understanding
            response = sql_agent.invoke({"messages": [("human", question)]})
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")


def example_iceberg_hive_catalog():
    """Example using Iceberg with Hive Metastore catalog."""
    print("\n=== Iceberg Hive Catalog Example ===")

    # Create Iceberg data source with Hive catalog
    iceberg_ds = IcebergDataSource(
        catalog_name="hive_catalog",
        catalog_type="hive",
        catalog_uri="thrift://localhost:9083",  # Hive Metastore URI
        warehouse="/user/hive/warehouse",
        properties={"hive.metastore.uris": "thrift://localhost:9083"},
    )

    # Profile a specific table
    print("Profiling table with Iceberg metadata...")
    table_profile = iceberg_ds.profile_table("orders", schema="sales")

    print("Table Profile:")
    print(
        f"  Method: {table_profile.get('profiling_summary', {}).get('profiling_method', 'unknown')}"
    )
    print(
        f"  Rows: {table_profile.get('table_profile', {}).get('row_count', 'unknown'):,}"
    )
    print(
        f"  Columns: {table_profile.get('profiling_summary', {}).get('total_columns', 'unknown')}"
    )

    # Show column profiles
    column_profiles = table_profile.get("column_profiles", {})
    print(f"  Column Details:")
    for col_name, profile in column_profiles.items():
        null_pct = profile.get("null_percentage", 0)
        distinct_ratio = profile.get("distinct_ratio", 0)
        print(
            f"    {col_name}: {null_pct:.1f}% NULL, {distinct_ratio:.2f} distinct ratio"
        )


def example_enhanced_prompt_generation():
    """Example showing enhanced prompt generation with Iceberg metadata."""
    print("\n=== Enhanced Prompt Generation ===")

    iceberg_ds = IcebergDataSource(
        catalog_name="data_lake",
        catalog_type="rest",
        catalog_uri="http://localhost:8181",
    )

    # Generate enhanced prompt for specific table
    prompt = iceberg_ds.prompt(schema="ecommerce", table="orders")
    print("Enhanced Prompt with Iceberg Metadata:")
    print(prompt)

    # The prompt includes:
    # - Table row counts from Iceberg snapshots
    # - Column statistics from Iceberg metadata
    # - Data freshness information
    # - Schema evolution history


def example_metadata_comparison():
    """Compare traditional profiling vs Iceberg metadata."""
    print("\n=== Metadata Comparison ===")

    # Traditional SQL datasource (requires runtime profiling)
    from ryoma_ai.datasource.postgres import PostgresDataSource

    postgres_ds = PostgresDataSource(
        host="localhost", database="ecommerce", user="user", password="password"
    )

    # Iceberg datasource (uses native metadata)
    iceberg_ds = IcebergDataSource(
        catalog_name="ecommerce",
        catalog_type="rest",
        catalog_uri="http://localhost:8181",
    )

    print("Traditional SQL profiling:")
    print("- Requires sampling data at runtime")
    print("- Limited by sample size")
    print("- Can be slow for large tables")
    print("- May miss historical patterns")

    print("\nIceberg metadata approach:")
    print("- Uses pre-computed statistics")
    print("- Full table statistics available")
    print("- Instant metadata access")
    print("- Includes historical evolution")
    print("- Schema evolution tracking")
    print("- Partition-level statistics")


if __name__ == "__main__":
    print("Ryoma AI - Apache Iceberg Integration Examples")
    print("=" * 50)

    try:
        # Run examples (comment out if you don't have Iceberg setup)
        # example_iceberg_rest_catalog()
        # example_iceberg_sql_agent()
        # example_iceberg_hive_catalog()
        # example_enhanced_prompt_generation()
        example_metadata_comparison()

        print("\n" + "=" * 50)
        print("Examples completed!")

        print("\nKey Benefits of Iceberg Integration:")
        print("✓ Rich metadata without runtime profiling")
        print("✓ Pre-computed statistics for better SQL generation")
        print("✓ Schema evolution tracking for robust queries")
        print("✓ Partition awareness for optimized query planning")
        print("✓ Time travel capabilities for historical analysis")
        print("✓ Transaction isolation for consistent results")

    except ImportError as e:
        print(f"Missing dependencies: {e}")
        print("Install with: pip install pyiceberg")
    except Exception as e:
        print(f"Example failed: {e}")
        print("Make sure you have:")
        print("1. Apache Iceberg catalog running")
        print("2. Correct connection parameters")
        print("3. PyIceberg installed")
