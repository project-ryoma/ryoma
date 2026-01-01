# 💡 Examples

Real-world examples demonstrating Ryoma's capabilities across different use cases and industries.

## 🏪 E-commerce Analytics

### Customer Segmentation Analysis
```python
from ryoma_ai.agent.sql import SqlAgent
from ryoma_data import DataSource

# Connect to e-commerce database
datasource = DataSource(
    "postgres",
    host="localhost",
    database="ecommerce",
    user="user",
    password="pass"
)

agent = SqlAgent(model="gpt-4", mode="enhanced")
agent.add_datasource(datasource)

# Complex customer analysis
response = agent.stream("""
Segment customers based on their purchase behavior:
1. High-value customers (>$1000 total purchases)
2. Frequent buyers (>10 orders)
3. Recent customers (first purchase in last 30 days)
4. At-risk customers (no purchase in 90+ days)

Show the count and average order value for each segment.
""")

print(response)
```

### Product Performance Dashboard
```python
# Multi-dimensional product analysis
response = agent.stream("""
Create a product performance report showing:
- Top 10 products by revenue this quarter
- Products with declining sales (comparing this month vs last month)
- Inventory turnover rate by category
- Seasonal trends for each product category

Include percentage changes and rank products by profitability.
""")
```

## 📊 Financial Analysis

### Revenue Forecasting
```python
from ryoma_data import DataSource

# Connect to financial data warehouse
datasource = DataSource(
    "snowflake",
    account="your-account",
    database="FINANCE_DW",
    user="user",
    password="pass"
)

agent = SqlAgent(model="gpt-4", mode="reforce")
agent.add_datasource(datasource)

# Complex financial analysis
response = agent.stream("""
Analyze monthly recurring revenue (MRR) trends:
1. Calculate MRR growth rate for the last 12 months
2. Identify churn impact on revenue
3. Segment MRR by customer size (SMB, Mid-market, Enterprise)
4. Forecast next quarter MRR based on current trends
5. Show the contribution of new vs expansion revenue

Include confidence intervals for the forecast.
""")
```

### Risk Assessment
```python
# Credit risk analysis
response = agent.stream("""
Generate a credit risk report:
- Customers with overdue payments >30 days
- Payment pattern analysis by customer segment
- Default probability scoring based on historical data
- Recommended credit limits for new customers
- Geographic risk distribution

Rank customers by risk score and suggest actions.
""")
```

## 🏥 Healthcare Analytics

### Patient Outcome Analysis
```python
from ryoma_data import DataSource

# Connect to healthcare data
datasource = DataSource(
    "bigquery",
    project_id="healthcare-analytics",
    dataset_id="patient_data"
)

agent = SqlAgent(
    model="gpt-4",
    mode="enhanced",
    safety_config={
        "enable_validation": True,
        "max_rows": 100000,
        "require_where_clause": True
    }
)
agent.add_datasource(datasource)

# HIPAA-compliant analysis
response = agent.stream("""
Analyze patient readmission patterns (anonymized data):
1. 30-day readmission rates by department
2. Common diagnoses leading to readmissions
3. Seasonal patterns in emergency visits
4. Average length of stay by condition type
5. Resource utilization efficiency metrics

Exclude any personally identifiable information.
""")
```

## 🏭 Manufacturing Operations

### Supply Chain Optimization
```python
# Manufacturing database with IoT sensor data
datasource = DataSource(
    "postgres",
    host="localhost",
    database="manufacturing",
    user="user",
    password="pass"
)

agent = SqlAgent(model="gpt-4", mode="enhanced")
agent.add_datasource(datasource)

# Complex supply chain analysis
response = agent.stream("""
Optimize our supply chain operations:
1. Identify bottlenecks in production lines
2. Calculate optimal inventory levels by component
3. Predict maintenance needs based on sensor data
4. Analyze supplier performance and delivery times
5. Recommend production schedule adjustments

Focus on reducing costs while maintaining quality standards.
""")
```

## 📱 SaaS Product Analytics

### User Engagement Analysis
```python
from ryoma_ai.agent.pandas import PandasAgent
import pandas as pd

# Load user activity data
df = pd.read_csv('user_activity.csv')

agent = PandasAgent("gpt-4")
agent.add_dataframe(df, name="user_activity")

# Comprehensive user analysis
response = agent.stream("""
Analyze user engagement patterns:
1. Daily/weekly/monthly active users trends
2. Feature adoption rates and user journey analysis
3. Cohort retention analysis by signup month
4. Identify power users vs casual users
5. Churn prediction based on activity patterns

Create actionable insights for product team.
""")
```

### A/B Test Analysis
```python
# A/B test results analysis
test_data = pd.read_csv('ab_test_results.csv')
agent.add_dataframe(test_data, name="ab_test")

response = agent.stream("""
Analyze A/B test results for new checkout flow:
1. Statistical significance of conversion rate difference
2. Segment analysis (mobile vs desktop, new vs returning users)
3. Revenue impact calculation
4. Confidence intervals and p-values
5. Recommendation on whether to ship the new feature

Include both statistical and business impact analysis.
""")
```

## 🎓 Educational Data Analysis

### Student Performance Insights
```python
# Educational database
datasource = DataSource(
    "postgres",
    host="localhost",
    database="education",
    user="user",
    password="pass"
)

agent = SqlAgent(model="gpt-4", mode="enhanced")
agent.add_datasource(datasource)

response = agent.stream("""
Analyze student performance and learning outcomes:
1. Grade distribution by subject and semester
2. Correlation between attendance and performance
3. Identify at-risk students early warning indicators
4. Course completion rates and dropout patterns
5. Teacher effectiveness metrics

Provide recommendations for improving student success.
""")
```

## 🌐 Multi-Database Analysis

### Cross-Platform Integration
```python
# Connect multiple data sources
postgres_ds = DataSource("postgres", host="localhost", database="sales")
snowflake_ds = DataSource("snowflake", account="account", database="MARKETING")

agent = SqlAgent(model="gpt-4", mode="enhanced")
agent.add_datasource(postgres_ds, name="sales_db")
agent.add_datasource(snowflake_ds, name="marketing_db")

# Cross-database analysis
response = agent.stream("""
Analyze the complete customer journey:
1. Marketing campaign effectiveness (from marketing_db)
2. Sales conversion rates (from sales_db)
3. Customer lifetime value calculation
4. Attribution modeling across channels
5. ROI by marketing channel and campaign

Combine data from both databases for comprehensive insights.
""")
```

## 🔍 Advanced Profiling Examples

### Database Health Check
```python
from ryoma_data import DataSource, DatabaseProfiler

# Connect to database
datasource = DataSource(
    "postgres",
    host="localhost",
    database="production",
    user="user",
    password="pass"
)

# Configure profiler
profiler = DatabaseProfiler(
    sample_size=20000,
    top_k=15,
    enable_lsh=True
)

# Get detailed profiling information
profile = datasource.profile_table("customers")

print("📊 Table Profile:")
print(f"Rows: {profile['table_profile']['row_count']:,}")
print(f"Completeness: {profile['table_profile']['completeness_score']:.2%}")

print("\n📋 Column Quality:")
for col, prof in profile['column_profiles'].items():
    quality = prof['data_quality_score']
    null_pct = prof['null_percentage']
    print(f"{col}: Quality {quality:.2f}, NULL {null_pct:.1f}%")
```

### Schema Similarity Analysis
```python
# Find similar columns across tables
similar_columns = datasource.find_similar_columns("customer_id", threshold=0.8)
print(f"🔗 Similar columns: {similar_columns}")

# Enhanced catalog with profiling
catalog = datasource.get_enhanced_catalog(include_profiles=True)
for schema in catalog.schemas:
    for table in schema.tables:
        high_quality_cols = table.get_high_quality_columns(min_quality_score=0.8)
        print(f"📊 {table.table_name}: {len(high_quality_cols)} high-quality columns")
```

## 🎯 Best Practices from Examples

### 1. **Use Appropriate Agent Modes**
- **Enhanced mode** for production analytics
- **ReFoRCE mode** for complex, multi-step analysis
- **Basic mode** for simple queries and development

### 2. **Configure Safety for Your Use Case**
- Healthcare: Strict PII protection
- Finance: Audit logging and access controls
- E-commerce: Row limits for large datasets

### 3. **Optimize Profiling Settings**
- Large datasets: Higher sample sizes
- Real-time systems: Cached profiles
- Development: Smaller samples for speed

### 4. **Structure Complex Queries**
- Break down multi-part questions
- Specify desired output format
- Include business context and constraints

### 5. **Monitor and Iterate**
- Track query performance
- Refine prompts based on results
- Use profiling data to improve accuracy

## 🚀 Next Steps

Ready to implement these patterns in your own projects?

- **[Advanced Setup](advanced-setup.md)** - Production configuration
- **[API Reference](../reference/index.md)** - Complete method documentation
- **[Architecture Guide](../architecture/index.md)** - Deep dive into internals
