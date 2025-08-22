"""
Database Profiling Demo

This example demonstrates the comprehensive database profiling capabilities
based on the "Automatic Metadata Extraction for Text-to-SQL" paper.

Features demonstrated:
- Row counts & NULL statistics
- Distinct-value ratio per column
- Numeric/date min, max, mean
- String length & character-type stats
- Top-k frequent values
- Locality-sensitive hashing / MinHash sketches for approximate similarity
"""

from ryoma_ai.datasource.sqlite import SqliteDataSource


def demo_comprehensive_profiling():
    """Demonstrate comprehensive database profiling."""

    print("🔍 Database Profiling Demo")
    print("=" * 50)

    # Initialize datasource with automatic profiling
    # You can use any SQL datasource (PostgreSQL, MySQL, SQLite, etc.)
    datasource = SqliteDataSource(
        connection_url="sqlite:///example.db",
        profiler_config={
            "sample_size": 10000,
            "top_k": 10,
            "lsh_threshold": 0.8,
            "num_hashes": 128,
            "enable_lsh": True,
        },
    )

    # Example table name - replace with your actual table
    table_name = "customers"

    print(f"\n📊 Profiling table: {table_name}")
    print("-" * 30)

    # 1. Comprehensive Table Profiling
    print("\n1. Table-Level Profiling:")
    table_profile = datasource.profile_table(table_name)

    if "error" not in table_profile:
        print("   ✅ Table profiled successfully")
        print(
            f"   📈 Row count: {table_profile.get('profiling_summary', {}).get('row_count', 'N/A')}"
        )
        print(
            f"   📊 Total columns: {table_profile.get('profiling_summary', {}).get('total_columns', 'N/A')}"
        )
        print(
            f"   🎯 Completeness score: {table_profile.get('profiling_summary', {}).get('completeness_score', 'N/A')}"
        )

        # Display column profiles
        column_profiles = table_profile.get("column_profiles", {})
        print(f"\n2. Column-Level Profiling ({len(column_profiles)} columns):")

        for col_name, profile in column_profiles.items():
            print(f"\n   📋 Column: {col_name}")
            print(f"      Type: {profile.get('semantic_type', 'general')}")
            print(f"      NULL %: {profile.get('null_percentage', 0):.1f}%")
            print(f"      Distinct ratio: {profile.get('distinct_ratio', 0):.3f}")
            print(f"      Quality score: {profile.get('data_quality_score', 0):.3f}")

            # Show top values
            top_values = profile.get("top_k_values", [])
            if top_values:
                print(
                    f"      Top values: {', '.join([str(v['value']) for v in top_values[:3]])}"
                )

            # Show numeric stats if available
            numeric_stats = profile.get("numeric_stats")
            if numeric_stats:
                print(
                    f"      Range: {numeric_stats.get('min_value', 'N/A')} - {numeric_stats.get('max_value', 'N/A')}"
                )
                print(
                    f"      Mean: {numeric_stats.get('mean', 'N/A'):.2f}"
                    if numeric_stats.get("mean")
                    else ""
                )

            # Show string stats if available
            string_stats = profile.get("string_stats")
            if string_stats:
                print(
                    f"      Length: {string_stats.get('min_length', 'N/A')} - {string_stats.get('max_length', 'N/A')} chars"
                )
                print(
                    f"      Avg length: {string_stats.get('avg_length', 'N/A'):.1f}"
                    if string_stats.get("avg_length")
                    else ""
                )

            # Show date stats if available
            date_stats = profile.get("date_stats")
            if date_stats:
                print(
                    f"      Date range: {date_stats.get('date_range_days', 'N/A')} days"
                )
    else:
        print(f"   ❌ Error profiling table: {table_profile['error']}")

    print("\n3. Enhanced Catalog with Profiling:")
    enhanced_catalog = datasource.get_enhanced_catalog(include_profiles=True)
    print(f"   📚 Catalog: {enhanced_catalog.catalog_name}")

    for schema in enhanced_catalog.schemas or []:
        print(f"   📁 Schema: {schema.schema_name}")
        for table in schema.tables or []:
            print(f"      📊 Table: {table.table_name}")
            if table.profile:
                print(f"         Rows: {table.profile.row_count}")
                print(
                    f"         Completeness: {table.profile.completeness_score:.3f}"
                    if table.profile.completeness_score
                    else ""
                )

            # Show enhanced column information
            profiled_columns = table.get_profiled_columns()
            high_quality_columns = table.get_high_quality_columns()

            print(f"         Profiled columns: {len(profiled_columns)}")
            print(f"         High quality columns: {len(high_quality_columns)}")

    print("\n4. Column Similarity Analysis:")
    # Find similar columns using LSH
    similar_columns = datasource.find_similar_columns("customer_id", threshold=0.7)
    if similar_columns:
        print(f"   🔗 Columns similar to 'customer_id': {', '.join(similar_columns)}")
    else:
        print("   ℹ️  No similar columns found (or LSH not available)")


def demo_individual_column_profiling():
    """Demonstrate individual column profiling."""

    print("\n\n🎯 Individual Column Profiling Demo")
    print("=" * 50)

    datasource = SqliteDataSource(
        connection_url="sqlite:///example.db", enable_profiling=True
    )

    # Profile specific columns
    columns_to_profile = ["customer_id", "email", "created_at", "total_spent"]
    table_name = "customers"

    for column_name in columns_to_profile:
        print(f"\n📊 Profiling column: {table_name}.{column_name}")
        print("-" * 40)

        column_profile = datasource.profile_column(table_name, column_name)

        if "error" not in column_profile:
            print("   ✅ Column profiled successfully")
            print(
                f"   🏷️  Semantic type: {column_profile.get('semantic_type', 'general')}"
            )
            print(
                f"   📊 Data quality: {column_profile.get('data_quality_score', 0):.3f}"
            )
            print(
                f"   🔢 Distinct count: {column_profile.get('distinct_count', 'N/A')}"
            )
            print(
                f"   ❌ NULL percentage: {column_profile.get('null_percentage', 0):.1f}%"
            )

            # Show type-specific statistics
            if column_profile.get("numeric_stats"):
                stats = column_profile["numeric_stats"]
                print("   📈 Numeric stats:")
                print(f"      Min: {stats.get('min_value', 'N/A')}")
                print(f"      Max: {stats.get('max_value', 'N/A')}")
                print(
                    f"      Mean: {stats.get('mean', 'N/A'):.2f}"
                    if stats.get("mean")
                    else ""
                )
                print(
                    f"      Std Dev: {stats.get('std_dev', 'N/A'):.2f}"
                    if stats.get("std_dev")
                    else ""
                )

            if column_profile.get("string_stats"):
                stats = column_profile["string_stats"]
                print("   📝 String stats:")
                print(
                    f"      Length range: {stats.get('min_length', 'N/A')} - {stats.get('max_length', 'N/A')}"
                )
                print(
                    f"      Avg length: {stats.get('avg_length', 'N/A'):.1f}"
                    if stats.get("avg_length")
                    else ""
                )
                char_types = stats.get("character_types", {})
                if char_types:
                    print(f"      Character types: {dict(char_types)}")

            if column_profile.get("date_stats"):
                stats = column_profile["date_stats"]
                print("   📅 Date stats:")
                print(f"      Range: {stats.get('date_range_days', 'N/A')} days")
                formats = stats.get("common_date_formats", [])
                if formats:
                    print(f"      Common formats: {', '.join(formats)}")

            # Show top frequent values
            top_values = column_profile.get("top_k_values", [])
            if top_values:
                print("   🔝 Top values:")
                for i, value_info in enumerate(top_values[:5], 1):
                    print(
                        f"      {i}. {value_info['value']} ({value_info['count']} times, {value_info['percentage']:.1f}%)"
                    )

            # Show LSH information
            lsh_sketch = column_profile.get("lsh_sketch")
            if lsh_sketch:
                print(
                    f"   🔗 LSH sketch: {lsh_sketch['num_hashes']} hashes, threshold {lsh_sketch['jaccard_threshold']}"
                )
        else:
            print(f"   ❌ Error profiling column: {column_profile['error']}")


def demo_profiling_configuration():
    """Demonstrate different profiling configurations."""

    print("\n\n⚙️  Profiling Configuration Demo")
    print("=" * 50)

    # Configuration for large databases
    large_db_config = {
        "sample_size": 50000,  # Larger sample for better accuracy
        "top_k": 20,  # More frequent values
        "lsh_threshold": 0.9,  # Higher similarity threshold
        "num_hashes": 256,  # More hash functions for better precision
        "enable_lsh": True,
    }

    # Configuration for fast profiling
    fast_config = {
        "sample_size": 1000,  # Smaller sample for speed
        "top_k": 5,  # Fewer frequent values
        "lsh_threshold": 0.7,  # Lower similarity threshold
        "num_hashes": 64,  # Fewer hash functions for speed
        "enable_lsh": False,  # Disable LSH for speed
    }

    print("📊 Large Database Configuration:")
    print(f"   Sample size: {large_db_config['sample_size']}")
    print(f"   Top-k values: {large_db_config['top_k']}")
    print(f"   LSH enabled: {large_db_config['enable_lsh']}")
    print(f"   Hash functions: {large_db_config['num_hashes']}")

    print("\n⚡ Fast Profiling Configuration:")
    print(f"   Sample size: {fast_config['sample_size']}")
    print(f"   Top-k values: {fast_config['top_k']}")
    print(f"   LSH enabled: {fast_config['enable_lsh']}")

    # Example of using different configurations
    print("\n🔧 Using custom configuration:")

    SqliteDataSource(
        connection_url="sqlite:///example.db",
        enable_profiling=True,
        profiler_config=fast_config,
    )

    print("   ✅ Fast profiling datasource initialized")
    print("   💡 Use this for quick analysis or large datasets")


def demo_profiling_integration_with_sql_agent():
    """Demonstrate how profiling integrates with SQL agents."""

    print("\n\n🤖 SQL Agent Integration Demo")
    print("=" * 50)

    # This would integrate with the enhanced SQL agent
    print("🔗 Integration points with Enhanced SQL Agent:")
    print("   1. Schema linking uses profiling data for better table selection")
    print("   2. Column exploration leverages statistical information")
    print("   3. Query optimization uses data distribution insights")
    print("   4. Error handling benefits from data quality scores")
    print("   5. Semantic type inference improves query generation")

    print("\n📋 Example profiling data usage in SQL generation:")
    print("   • High distinct ratio columns → Good for GROUP BY")
    print("   • Low null percentage columns → Safe for WHERE clauses")
    print("   • Semantic types (email, phone) → Appropriate formatting")
    print("   • Top-k values → Better literal matching")
    print("   • LSH similarity → Column name disambiguation")


if __name__ == "__main__":
    print("🚀 Database Profiling System Demo")
    print("Based on 'Automatic Metadata Extraction for Text-to-SQL' paper")
    print("=" * 70)

    try:
        # Run all demos
        demo_comprehensive_profiling()
        demo_individual_column_profiling()
        demo_profiling_configuration()
        demo_profiling_integration_with_sql_agent()

        print("\n\n✅ Demo completed successfully!")
        print("💡 Next steps:")
        print("   1. Configure profiling for your specific database")
        print("   2. Integrate with Enhanced SQL Agent")
        print("   3. Use profiling data for better query generation")
        print("   4. Monitor data quality over time")

    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        print("💡 Make sure you have:")
        print("   1. A valid database connection")
        print("   2. Required dependencies installed")
        print("   3. Appropriate table permissions")
