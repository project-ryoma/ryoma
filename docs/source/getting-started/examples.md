# 💡 Examples

Real-world examples demonstrating Ryoma's capabilities across different use cases and industries.

## 🏪 E-commerce Analytics

### Customer Segmentation Analysis
```python
from ryoma_ai import Ryoma
from ryoma_data import DataSource

# Connect to e-commerce database
datasource = DataSource(
    "postgres",
    host="localhost",
    database="ecommerce",
    user="user",
    password="password"
)

ryoma = Ryoma(datasource=datasource)
agent = ryoma.sql_agent(model="gpt-4", mode="enhanced")

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
from ryoma_ai import Ryoma
from ryoma_data import DataSource

# Connect to financial data warehouse
datasource = DataSource(
    "snowflake",
    account="your-account",
    database="FINANCE_DW",
    user="user",
    password="password"
)

ryoma = Ryoma(datasource=datasource)
agent = ryoma.sql_agent(model="gpt-4", mode="reforce")

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
from ryoma_ai import Ryoma
from ryoma_data import DataSource

# Connect to healthcare data
datasource = DataSource(
    "bigquery",
    project_id="healthcare-analytics",
    dataset_id="patient_data"
)

ryoma = Ryoma(datasource=datasource)
agent = ryoma.sql_agent(model="gpt-4", mode="enhanced")

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
from ryoma_ai import Ryoma
from ryoma_data import DataSource

# Manufacturing database with IoT sensor data
datasource = DataSource(
    "postgres",
    host="localhost",
    database="manufacturing",
    user="user",
    password="password"
)

ryoma = Ryoma(datasource=datasource)
agent = ryoma.sql_agent(model="gpt-4", mode="enhanced")

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
from ryoma_ai import Ryoma
import pandas as pd

# Load user activity data
df = pd.read_csv('user_activity.csv')

# Create Ryoma and pandas agent
ryoma = Ryoma()
agent = ryoma.pandas_agent(model="gpt-4")
agent.add_dataframe(df, df_id="user_activity")

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
agent.add_dataframe(test_data, df_id="ab_test")

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
from ryoma_ai import Ryoma
from ryoma_data import DataSource

# Educational database
datasource = DataSource(
    "postgres",
    host="localhost",
    database="education",
    user="user",
    password="password"
)

ryoma = Ryoma(datasource=datasource)
agent = ryoma.sql_agent(model="gpt-4", mode="enhanced")

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
from ryoma_ai import Ryoma
from ryoma_data import DataSource

# Ryoma supports multiple datasources - switch between them easily
ryoma = Ryoma()

# Add multiple datasources
ryoma.add_datasource(
    DataSource("postgres", host="localhost", database="sales", user="user", password="password"),
    name="sales"
)
ryoma.add_datasource(
    DataSource("snowflake", account="account", database="MARKETING", user="user", password="password"),
    name="marketing"
)

# Create agent
agent = ryoma.sql_agent(model="gpt-4", mode="enhanced")

# Query sales database (default - first added)
sales_response = agent.stream("Get sales conversion rates by channel")

# Switch to marketing database
ryoma.set_active("marketing")
marketing_response = agent.stream("Get marketing campaign performance metrics")

# For cross-database analysis, use a consolidated data warehouse
ryoma.add_datasource(
    DataSource("snowflake", account="account", database="DATA_WAREHOUSE", user="user", password="password"),
    name="warehouse"
)
ryoma.set_active("warehouse")

response = agent.stream("""
Analyze the complete customer journey:
1. Marketing campaign effectiveness
2. Sales conversion rates
3. Customer lifetime value calculation
4. Attribution modeling across channels
5. ROI by marketing channel and campaign
""")
```

## 🔍 Database Exploration

### Metadata Exploration
```python
from ryoma_data import DataSource

# Connect to database
datasource = DataSource(
    "postgres",
    host="localhost",
    database="production",
    user="user",
    password="password"
)

# Get catalog metadata
catalog = datasource.get_catalog()

print("📊 Database Catalog:")
for schema in catalog.schemas:
    print(f"\nSchema: {schema.schema_name}")
    for table in schema.tables:
        print(f"  Table: {table.table_name}")
        for col in table.columns:
            print(f"    - {col.name}: {col.type}")
```

## 🎯 Best Practices

### 1. **Choose the Right Agent Mode**
```python
# Basic mode - fast, simple queries
agent = ryoma.sql_agent(model="gpt-4", mode="basic")

# Enhanced mode - multi-step reasoning, safety validation (recommended)
agent = ryoma.sql_agent(model="gpt-4", mode="enhanced")

# ReFoRCE mode - complex analysis, self-refinement
agent = ryoma.sql_agent(model="gpt-4", mode="reforce")
```

### 2. **Structure Complex Queries**
- Break down multi-part questions
- Specify desired output format
- Include business context and constraints

### 3. **Use Multiple Datasources Effectively**
```python
ryoma = Ryoma()
ryoma.add_datasource(prod_db, name="production")
ryoma.add_datasource(analytics_db, name="analytics")

# Switch as needed
ryoma.set_active("analytics")
```

## 🚀 Next Steps

Ready to implement these patterns in your own projects?

- **[Advanced Setup](advanced-setup.md)** - Production configuration
- **[API Reference](../reference/index.md)** - Complete method documentation
- **[Architecture Guide](../architecture/index.md)** - Deep dive into internals
