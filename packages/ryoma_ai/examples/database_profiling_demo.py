"""
Database Profiling Demo

This example demonstrates comprehensive database profiling capabilities.

Features demonstrated:
- Row counts & NULL statistics
- Distinct-value ratio per column
- Numeric/date min, max, mean
- String length & character-type stats
- Top-k frequent values
- Locality-sensitive hashing / MinHash sketches for approximate similarity
"""

from ryoma_data import DatabaseProfiler, DataSource


def demo_comprehensive_profiling():
    """Demonstrate comprehensive database profiling."""

    print("🔍 Database Profiling Demo")
    print("=" * 50)

    # Create datasource
    datasource = DataSource("sqlite", database="example.db")

    # Create profiler with configuration
    profiler = DatabaseProfiler(
        sample_size=10000,
        top_k=10,
        lsh_threshold=0.8,
        num_hashes=128,
        enable_lsh=True,
    )

    # Example table name
    table_name = "customers"

    print(f"\n📊 Profiling table: {table_name}")
    print("-" * 30)

    # Profile the table
    print("\n1. Table-Level Profiling:")
    table_profile = profiler.profile_table(datasource, table_name)

    if table_profile:
        print("   ✅ Table profiled successfully")
        print(f"   📈 Row count: {table_profile.row_count}")
        print(f"   📊 Total columns: {table_profile.column_count}")
        print(f"   🎯 Completeness score: {table_profile.completeness_score:.3f}")
    else:
        print("   ❌ Error profiling table")

    # Profile individual columns
    print("\n2. Column-Level Profiling:")
    catalog = datasource.get_catalog(table=table_name)

    for schema in catalog.schemas:
        for table in schema.tables:
            for column in table.columns[:3]:  # Show first 3 columns as example
                column_profile = profiler.profile_column(
                    datasource, table_name, column.name
                )

                print(f"\n   📋 Column: {column.name}")
                print(f"      Type: {column_profile.semantic_type}")
                print(f"      NULL %: {column_profile.null_percentage:.1f}%")
                print(f"      Distinct ratio: {column_profile.distinct_ratio:.3f}")
                print(f"      Quality score: {column_profile.data_quality_score:.3f}")

                # Show top values if available
                if column_profile.top_k_values:
                    top_3 = column_profile.top_k_values[:3]
                    values_str = ", ".join([str(v["value"]) for v in top_3])
                    print(f"      Top values: {values_str}")


def demo_profiling_configurations():
    """Demonstrate different profiling configurations."""

    print("\n\n⚙️  Profiling Configuration Demo")
    print("=" * 50)

    # Configuration for large databases
    print("\n📊 Large Database Configuration:")
    _ = DatabaseProfiler(
        sample_size=50000,  # Larger sample for better accuracy
        top_k=20,  # More frequent values
        lsh_threshold=0.9,  # Higher similarity threshold
        num_hashes=256,  # More hash functions for precision
        enable_lsh=True,
    )
    print("   Sample size: 50,000")
    print("   Top-k values: 20")
    print("   LSH enabled: True (256 hashes)")

    # Configuration for fast profiling
    print("\n⚡ Fast Profiling Configuration:")
    _ = DatabaseProfiler(
        sample_size=1000,  # Smaller sample for speed
        top_k=5,  # Fewer frequent values
        enable_lsh=False,  # Disable LSH for speed
    )
    print("   Sample size: 1,000")
    print("   Top-k values: 5")
    print("   LSH enabled: False")

    print("\n💡 Usage:")
    print("   datasource = DataSource('postgres', host='localhost', database='db')")
    print("   profiler = DatabaseProfiler(sample_size=10000, enable_lsh=True)")
    print("   profile = profiler.profile_table(datasource, 'table_name')")


def demo_profiler_flexibility():
    """Demonstrate profiler flexibility with different configurations."""

    print("\n\n🏗️  Profiler Flexibility")
    print("=" * 50)

    _ = DataSource("sqlite", database="example.db")

    # Quick profiling
    _ = DatabaseProfiler(sample_size=1000, enable_lsh=False)
    print("\n1️⃣  Quick profiling with small sample:")
    # quick_profile = quick_profiler.profile_table(datasource, "table")

    # Detailed profiling
    _ = DatabaseProfiler(sample_size=50000, enable_lsh=True)
    print("2️⃣  Detailed profiling with large sample and LSH:")
    # detailed_profile = detailed_profiler.profile_table(datasource, "table")

    # Use same profiler with multiple datasources
    _ = DatabaseProfiler()
    print("\n3️⃣  Use same profiler with multiple datasources:")

    _ = DataSource("postgres", host="localhost", database="db1")
    # pg_profile = profiler.profile_table(pg_datasource, "users")

    _ = DataSource("mysql", host="localhost", database="db2")
    # mysql_profile = profiler.profile_table(mysql_datasource, "customers")


def demo_integration_patterns():
    """Show common integration patterns."""

    print("\n\n🔗 Integration Patterns")
    print("=" * 50)

    print("\n📋 Pattern 1: Profile During Data Exploration")
    print("```python")
    print("ds = DataSource('postgres', host='localhost', database='analytics')")
    print("profiler = DatabaseProfiler()")
    print("")
    print("# Explore catalog")
    print("catalog = ds.get_catalog()")
    print("for schema in catalog.schemas:")
    print("    for table in schema.tables:")
    print("        # Profile each table")
    print("        profile = profiler.profile_table(ds, table.table_name)")
    print("        print(f'{table.table_name}: {profile.row_count} rows')")
    print("```")

    print("\n📋 Pattern 2: Profile Specific Columns for Quality Checks")
    print("```python")
    print("profiler = DatabaseProfiler()")
    print("profile = profiler.profile_column(datasource, 'users', 'email')")
    print("")
    print("if profile.data_quality_score < 0.8:")
    print("    print(f'Warning: Low quality email column!')")
    print("    print(f'NULL %: {profile.null_percentage}%')")
    print("```")

    print("\n📋 Pattern 3: Use with AI Agents")
    print("```python")
    print("from ryoma_ai.agent.sql import SqlAgent")
    print("")
    print("# Create datasource and profiler")
    print("ds = DataSource('postgres', ...)")
    print("profiler = DatabaseProfiler()")
    print("")
    print("# Profile for metadata extraction")
    print("table_profile = profiler.profile_table(ds, 'customers')")
    print("")
    print("# Use with SQL agent")
    print("agent = SqlAgent('gpt-4')")
    print("agent.add_datasource(ds)")
    print("# Agent can leverage profiling metadata for better SQL generation")
    print("```")


if __name__ == "__main__":
    print("🚀 Database Profiling System Demo")
    print("=" * 70)

    try:
        # Run demos
        demo_comprehensive_profiling()
        demo_profiling_configurations()
        demo_profiler_flexibility()
        demo_integration_patterns()

        print("\n\n✅ Demo completed successfully!")
        print("\n📚 Next Steps:")
        print("   1. Try profiling your own database")
        print("   2. Experiment with different configurations")
        print("   3. Integrate profiling with SQL agents")
        print("   4. Use profiling data for data quality monitoring")

    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        print("\n💡 Make sure you have:")
        print("   1. A valid database with example data")
        print("   2. Required dependencies installed")
        print("   3. Appropriate database permissions")
