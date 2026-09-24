<div align="center">

<img src="docs/images/app_logo.png" width="120" alt="E-Commerce IQ Logo" style="border-radius: 12px; margin-bottom: 8px;" />

# E-COMMERCE IQ

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=34&duration=2500&pause=1000&color=1E3A8A&center=true&vCenter=true&width=650&height=60&lines=E-COMMERCE+IQ;AI-Powered+Decision+Intelligence;Deterministic+SQL+%2B+AI+Copilot;Executive+Business+Analytics)](https://github.com/AlankritaPaul/E-Commerce-IQ)

<img src="docs/images/animated_title.svg" width="650" alt="E-Commerce IQ Animated Title" />

<br/>

[![Python](https://img.shields.io/badge/Language-Python%203.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![SQL](https://img.shields.io/badge/Language-SQL%20(SQLite%20%2F%20PostgreSQL)-4479A1?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Architecture](https://img.shields.io/badge/Architecture-Dual--Engine%20BI-059669?style=for-the-badge)]()

<br/><br/>

<img src="docs/images/ecommerce_iq_hero.jpg" width="95%" alt="E-Commerce IQ Executive BI Dashboard & AI Copilot Preview" style="border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.25);" />

<br/>
<em>Executive Business Intelligence & Decision Support Platform with Deterministic Analytics & Conversational AI Copilot</em>

</div>

---

**E-Commerce IQ** is an enterprise-grade, AI-powered Business Intelligence and Decision Support System built for e-commerce business owners, operators, and executives. 

Unlike conventional dashboards that only display static graphs, or generative AI chatbots prone to hallucinating numbers, E-Commerce IQ pairs a **deterministic SQL analytical calculation engine** with an **intelligent conversational AI copilot**. It allows business leaders to query their underlying business metrics using natural language and receive verified, data-backed financial figures paired with strategic diagnostic insights.

---

## <img src="docs/images/icons/core_concepts.svg" width="22" height="22" valign="middle" /> Core Languages & Concepts

- <img src="docs/images/icons/python.svg" width="20" height="20" valign="middle" /> **Python (3.10+)**: Powers backend analytics computation engines, statistical anomaly detection, natural language processing, LLM orchestration, Streamlit UI, and automated test suites.
- <img src="docs/images/icons/sqlite.svg" width="20" height="20" valign="middle" /> **SQL (Relational SQL / SQLite / PostgreSQL Dialects)**: The deterministic foundation for all financial fact storage, data modeling, multi-table aggregations, time-series windowing, and safe Text-to-SQL generation.

---

## <img src="docs/images/icons/capabilities.svg" width="22" height="22" valign="middle" /> Key Capabilities

### <img src="docs/images/icons/sales_revenue.svg" width="18" height="18" valign="middle" /> 1. Sales & Revenue Intelligence
- Real-time tracking of Gross Merchandise Value (GMV), Net Revenue, Total Orders, and Average Order Value (AOV).
- Profit margin analysis and discount erosion tracking.
- Breakdown of payment methods, shipping costs, and tax liabilities.

### <img src="docs/images/icons/products.svg" width="18" height="18" valign="middle" /> 2. Product-Wise Performance
- Identification of high-margin bestsellers, cash cows, and lagging/dead inventory.
- Inventory turnover velocity and stockout risk monitoring.
- Unit economics per SKU and product category contribution margins.

### <img src="docs/images/icons/customers.svg" width="18" height="18" valign="middle" /> 3. Customer Behavior & Cohorts
- Customer retention, repeat purchase rates, and churn risk scoring.
- RFM (Recency, Frequency, Monetary) customer segmentation.
- Customer Lifetime Value (LTV) and regional sales distribution.

### <img src="docs/images/icons/reviews_sentiment.svg" width="18" height="18" valign="middle" /> 4. Customer Reviews & Sentiment Analysis
- Automated sentiment scoring (positive, neutral, negative) across written product feedback.
- Automated extraction of recurring complaints (e.g., sizing, zipper defects, late delivery) and top praises.
- Correlation between customer sentiment shifts and subsequent product sales trajectory.

### <img src="docs/images/icons/returns_refunds.svg" width="18" height="18" valign="middle" /> 5. Orders, Returns & Financial Leakage
- Comprehensive return rate calculation by product, category, and vendor.
- Categorization of return root causes (e.g., "Defective", "Not as Pictured", "Fit Issue").
- Tracking of net refund amounts and bottom-line margin loss due to returns.

### <img src="docs/images/icons/time_series.svg" width="18" height="18" valign="middle" /> 6. Temporal Performance & Comparative Variance
- Automated Month-over-Month (MoM), Week-over-Week (WoW), and Year-over-Year (YoY) comparisons.
- Variance analysis highlighting percentage changes and absolute delta values.

### <img src="docs/images/icons/ai_copilot.svg" width="18" height="18" valign="middle" /> 7. Natural Language Conversational Copilot
- Business owners can ask questions in plain English, such as:
  - *"What was my net revenue this month compared to last month?"*
  - *"Which products have a return rate higher than 15%, and what are customers complaining about?"*
  - *"Why did sales drop in the Electronics category last week?"*
  - *"What is our current Average Order Value and repeat customer percentage?"*
- Converts queries into safe, read-only SQL, executes them deterministically, and provides executive summaries.

---

## <img src="docs/images/icons/architecture.svg" width="22" height="22" valign="middle" /> System Architecture

E-Commerce IQ is architected around a **Dual-Engine BI Pattern**:

```
                  +----------------------------------------------+
                  |           User Interface (Streamlit)         |
                  |     Executive KPI Cards | Visual Charts      |
                  |           Conversational AI Copilot          |
                  +----------------------+-----------------------+
                                         |
                                         v
                  +----------------------------------------------+
                  |              Query Router / Agent            |
                  +----------------------+-----------------------+
                                         |
                   +---------------------+---------------------+
                   |                                           |
                   v                                           v
    +------------------------------+            +------------------------------+
    |    Deterministic Analytics   |            |      AI / NLP Copilot        |
    |          (Python)            |            |        (LLM Engine)          |
    | - Revenue & AOV calculations |            | - Text-to-SQL generation     |
    | - MoM / WoW Variance         |            | - AST Guardrails (Read-Only) |
    | - Return & Defect ratios     |            | - Review Sentiment & Topics  |
    | - Exact numerical results    |            | - Executive Narrative Synthes|
    +--------------+---------------+            +--------------+---------------+
                   |                                           |
                   +---------------------+---------------------+
                                         |
                                         v
                  +----------------------------------------------+
                  |         Relational Database Layer            |
                  |    (SQLite / DuckDB / PostgreSQL via ORM)    |
                  | Orders, Items, Products, Customers, Reviews  |
                  +----------------------------------------------+
```

---

## <img src="docs/images/icons/sql_engine.svg" width="22" height="22" valign="middle" /> Where and How SQL is Used in E-Commerce IQ

SQL serves as the **single source of truth** and the deterministic engine across all analytical stages. Here is an overview of where SQL is implemented and how it operates:

### <img src="docs/images/icons/schema_model.svg" width="18" height="18" valign="middle" /> 1. Relational Data Modeling & Integrity (`src/ecommerce_iq/database/schema.sql`)
- **Normalized Schema**: 8 core relational tables (`customers`, `categories`, `products`, `orders`, `order_items`, `payments`, `returns`, `reviews`, `review_insights`, and `sales`).
- **Integrity Constraints**: Enforces foreign keys (`ON DELETE CASCADE`), `CHECK` constraints (valid CSAT ratings `1-5`, positive prices, non-negative quantities), and performance indexes on `order_date`, `customer_id`, `product_id`.
- **Analytical Views with CTEs**: Defines pre-aggregated analytical views (`v_product_performance`, `v_daily_sales_summary`) using Common Table Expressions (`WITH` clauses) to eliminate join fan-out.

### <img src="docs/images/icons/query_gateway.svg" width="18" height="18" valign="middle" /> 2. High-Performance Native Query Gateway (`src/ecommerce_iq/database/connection.py`)
- **Direct Parameterized SQL**: `DatabaseManager.execute_query(sql, params)` runs raw SQL using Python's native `sqlite3` driver and `sqlite3.Row` dictionaries.
- **Connection Optimization**: Configures `PRAGMA foreign_keys = ON;` and thread-safe execution without ORM overhead.

### <img src="docs/images/icons/kpis_metrics.svg" width="18" height="18" valign="middle" /> 3. Financial KPIs & Time-Series Aggregations (`src/ecommerce_iq/analytics/kpis.py`)
- **Exact Accounting Formulations**:
  ```sql
  SELECT 
      ROUND(SUM(oi.total_price), 2) AS gross_sales,
      ROUND(SUM(oi.total_price) - COALESCE(SUM(r.refund_amount), 0), 2) AS net_revenue,
      COUNT(DISTINCT o.order_id) AS total_orders,
      ROUND(SUM(oi.total_price) / COUNT(DISTINCT o.order_id), 2) AS aov
  FROM orders o
  JOIN order_items oi ON o.order_id = oi.order_id
  LEFT JOIN returns r ON o.order_id = r.order_id AND r.status = 'Approved';
  ```
- **Monthly Trajectory Windowing**: Uses `strftime('%Y-%m', o.order_date)` to aggregate trends over the 14 operating months.

### <img src="docs/images/icons/sku_economics.svg" width="18" height="18" valign="middle" /> 4. SKU Unit Economics & Classification (`src/ecommerce_iq/analytics/products.py`)
- **Product Profitability & Margins**: Calculates profit margin per SKU using `ROUND((p.price - p.cost_price) * SUM(oi.quantity), 2)`.
- **Dead-Stock Inventory Detection**: Identifies slow-moving or unpurchased catalog items using `LEFT JOIN` and filtering for `NULL` order items.

### <img src="docs/images/icons/customer_rfm.svg" width="18" height="18" valign="middle" /> 5. Customer Behavior & RFM Quintiles (`src/ecommerce_iq/analytics/customers.py`)
- **Customer Lifetime Value (LTV)**: Aggregates total historical spend per customer account.
- **Order Frequency Distribution**: Uses SQL `CASE` statements to categorize customers into brackets (`1 Order`, `2-3 Orders`, `4-6 Orders`, `7-9 Orders`, `10+ Orders`).
- **Recency Calculation**: Computes days elapsed since last purchase via `CAST(julianday('now') - julianday(MAX(order_date)) AS INTEGER)`.

### <img src="docs/images/icons/leakage_tracking.svg" width="18" height="18" valign="middle" /> 6. Returns & Refund Leakage Tracking (`src/ecommerce_iq/analytics/returns.py`)
- **Return Rate by SKU**: Computes returned unit percentage:
  ```sql
  ROUND((COALESCE(SUM(ret.quantity), 0) * 100.0 / SUM(oi.quantity)), 2) AS return_rate
  ```
- **RMA Reasons Breakdown**: Evaluates return incident counts and bottom-line dollar refund leakage grouped by stated customer reason.

### <img src="docs/images/icons/text_to_sql.svg" width="18" height="18" valign="middle" /> 7. Natural-Language Text-to-SQL Copilot (`src/ecommerce_iq/ai/text_to_sql.py`)
- **Schema-Grounded Query Translation**: Automatically maps plain-English executive questions into syntactically valid SQL queries targeting relevant entities and date ranges.

### <img src="docs/images/icons/security_shield.svg" width="18" height="18" valign="middle" /> 8. SQL Security Guardrails & AST Verification (`src/ecommerce_iq/ai/sql_guardrails.py`)
- **AST Token Inspection**: Analyzes queries with Abstract Syntax Tree parsers to strictly enforce read-only `SELECT` and `WITH` statements.
- **Mutation & Injection Blocking**: Instantly blocks destructive tokens (`DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `TRUNCATE`, `--`, `;`).
- **Table Whitelisting & Limit Clamping**: Verifies that queries only access authorized business tables and injects or clamps `LIMIT` clauses to guarantee bounded execution.

---

## <img src="docs/images/icons/tech_stack.svg" width="22" height="22" valign="middle" /> Technology Stack

- <img src="docs/images/icons/python.svg" width="18" height="18" valign="middle" /> **Core Programming Language**: Python 3.10+
- <img src="docs/images/icons/pandas.svg" width="18" height="18" valign="middle" /> <img src="docs/images/icons/numpy.svg" width="18" height="18" valign="middle" /> **Data Manipulation & Math**: Pandas, NumPy
- <img src="docs/images/icons/sqlite.svg" width="18" height="18" valign="middle" /> <img src="docs/images/icons/postgresql.svg" width="18" height="18" valign="middle" /> **Database & Query Engine**: SQLite / DuckDB (local analytical storage) / PostgreSQL (production), managed via SQLAlchemy ORM
- <img src="docs/images/icons/security_shield.svg" width="18" height="18" valign="middle" /> **SQL Security & Parsing**: SQLGlot (AST parsing, read-only enforcement, injection protection)
- <img src="docs/images/icons/google.svg" width="18" height="18" valign="middle" /> **AI & Large Language Models**: Google Gemini API (`google-genai`), with pluggable support for OpenAI (`openai`)
- <img src="docs/images/icons/reviews_sentiment.svg" width="18" height="18" valign="middle" /> **Natural Language & Sentiment**: VADER Sentiment, TextBlob
- <img src="docs/images/icons/streamlit.svg" width="18" height="18" valign="middle" /> <img src="docs/images/icons/plotly.svg" width="18" height="18" valign="middle" /> **User Interface & Visualization**: Streamlit, Plotly
- <img src="docs/images/icons/pytest.svg" width="18" height="18" valign="middle" /> **Data Generation & Quality**: Faker, Pytest (117 automated unit & integration tests)
- <img src="docs/images/icons/git.svg" width="18" height="18" valign="middle" /> **Version Control & CI/CD**: Git, GitHub

---

## <img src="docs/images/icons/directory.svg" width="22" height="22" valign="middle" /> Directory Layout

```
E-Commerce-IQ/
├── .env.example                  # Environment configuration template
├── .gitignore                    # Git tracking rules
├── pyproject.toml                # Project packaging & build specifications
├── requirements.txt              # Pinned dependencies
├── README.md                     # Project documentation
│
├── config/                       # Application configuration
│   ├── __init__.py
│   └── settings.py               # Pydantic BaseSettings management
│
├── docs/                         # Technical architecture & schema docs
│   ├── architecture.md           # System architecture specification
│   ├── database_schema.md        # Relational schema reference
│   └── images/                   # Dashboard preview, animated SVG, and topic icons
│
├── src/ecommerce_iq/             # Core application package
│   ├── __init__.py
│   ├── database/                 # Connection pools, sessions, and engine setup
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   └── schema.sql
│   ├── models/                   # ORM entities and Pydantic validation schemas
│   │   ├── __init__.py
│   │   ├── entities.py
│   │   └── schemas.py
│   ├── analytics/                # Deterministic analytical computation engines
│   │   ├── __init__.py
│   │   ├── kpis.py
│   │   ├── comparisons.py
│   │   ├── products.py
│   │   └── returns.py
│   ├── business_logic/           # Domain workflows & strategic decision services
│   │   ├── __init__.py
│   │   ├── diagnosis.py
│   │   ├── segmentation.py
│   │   └── recommendations.py
│   ├── ai/                       # AI, Text-to-SQL, and NLP sentiment pipelines
│   │   ├── __init__.py
│   │   ├── llm_client.py
│   │   ├── text_to_sql.py
│   │   ├── sql_guardrails.py
│   │   ├── sentiment.py
│   │   └── advisor.py
│   └── utils/                    # Shared utilities
│       ├── __init__.py
│       ├── formatting.py
│       └── logging.py
│
├── ui/                           # Interactive Streamlit presentation layer
│   ├── __init__.py
│   ├── app.py                    # Main dashboard application entrypoint
│   ├── components/               # Modular UI widgets (cards, charts, copilot)
│   │   ├── __init__.py
│   │   ├── cards.py
│   │   ├── charts.py
│   │   └── chat.py
│   ├── views/                    # Internal analytical view implementations
│   └── pages/                    # 11 Sequentially-ordered stage views
│       ├── 01_Sales_and_Revenue.py
│       ├── 02_Product_Performance.py
│       ├── 03_Customer_Behavior.py
│       ├── 04_Customer_Reviews.py
│       ├── 05_Returns_and_Refunds.py
│       ├── 06_Root_Cause_Diagnosis.py
│       ├── 07_Strategic_Playbook.py
│       ├── 08_Conversational_Copilot.py
│       ├── 09_Natural_Language_Query.py
│       ├── 10_Executive_Summary.py
│       └── 11_Data_Management.py
│
├── tests/                        # Automated unit and integration test suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_config.py
│   ├── test_models.py
│   ├── test_analytics.py
│   └── test_ai.py
│
└── data/                         # Local database and dataset storage
    └── .gitkeep
```

---

## <img src="docs/images/icons/getting_started.svg" width="22" height="22" valign="middle" /> Getting Started

### <img src="docs/images/icons/prerequisites.svg" width="18" height="18" valign="middle" /> 1. Prerequisites
- Python 3.10 or higher
- Git

### <img src="docs/images/icons/terminal_setup.svg" width="18" height="18" valign="middle" /> 2. Environment Setup
```bash
# Clone repository
git clone https://github.com/AlankritaPaul/E-Commerce-IQ.git
cd E-Commerce-IQ

# Create a virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### <img src="docs/images/icons/config_key.svg" width="18" height="18" valign="middle" /> 3. Environment Configuration
Copy the sample environment file:
```bash
cp .env.example .env
```
Open `.env` and set your configuration variables (e.g., `GEMINI_API_KEY`).

### <img src="docs/images/icons/play_run.svg" width="18" height="18" valign="middle" /> 4. Running the Project
```bash
# Initialize the database schema
python scripts/init_db.py

# Seed the 14-month realistic dataset
python scripts/seed_mock_data.py

# Run all 117 automated unit and integration tests
python -m unittest discover -s tests

# Launch the interactive BI Dashboard
python -m streamlit run ui/app.py
```

---

## <img src="docs/images/icons/license.svg" width="22" height="22" valign="middle" /> License

This project is licensed under the [MIT License](LICENSE).
