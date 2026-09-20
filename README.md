# E-Commerce IQ

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Architecture: Dual-Engine BI](https://img.shields.io/badge/Architecture-Dual--Engine%20BI-success.svg)]()

**E-Commerce IQ** is an enterprise-grade, AI-powered Business Intelligence and Decision Support System built for e-commerce business owners, operators, and executives. 

Unlike conventional dashboards that only display static graphs, or generative AI chatbots prone to hallucinating numbers, E-Commerce IQ pairs a **deterministic SQL analytical calculation engine** with an **intelligent conversational AI copilot**. It allows business leaders to query their underlying business metrics using natural language and receive verified, data-backed financial figures paired with strategic diagnostic insights.

---

## Key Capabilities

### 1. Sales & Revenue Intelligence
- Real-time tracking of Gross Merchandise Value (GMV), Net Revenue, Total Orders, and Average Order Value (AOV).
- Profit margin analysis and discount erosion tracking.
- Breakdown of payment methods, shipping costs, and tax liabilities.

### 2. Product-Wise Performance
- Identification of high-margin bestsellers, cash cows, and lagging/dead inventory.
- Inventory turnover velocity and stockout risk monitoring.
- Unit economics per SKU and product category contribution margins.

### 3. Customer Behavior & Cohorts
- Customer retention, repeat purchase rates, and churn risk scoring.
- RFM (Recency, Frequency, Monetary) customer segmentation.
- Customer Lifetime Value (LTV) and regional sales distribution.

### 4. Customer Reviews & Sentiment Analysis
- Automated sentiment scoring (positive, neutral, negative) across written product feedback.
- Automated extraction of recurring complaints (e.g., sizing, zipper defects, late delivery) and top praises.
- Correlation between customer sentiment shifts and subsequent product sales trajectory.

### 5. Orders, Returns & Financial Leakage
- Comprehensive return rate calculation by product, category, and vendor.
- Categorization of return root causes (e.g., "Defective", "Not as Pictured", "Fit Issue").
- Tracking of net refund amounts and bottom-line margin loss due to returns.

### 6. Temporal Performance & Comparative Variance
- Automated Month-over-Month (MoM), Week-over-Week (WoW), and Year-over-Year (YoY) comparisons.
- Variance analysis highlighting percentage changes and absolute delta values.

### 7. Natural Language Conversational Copilot
- Business owners can ask questions in plain English, such as:
  - *"What was my net revenue this month compared to last month?"*
  - *"Which products have a return rate higher than 15%, and what are customers complaining about?"*
  - *"Why did sales drop in the Electronics category last week?"*
  - *"What is our current Average Order Value and repeat customer percentage?"*
- Converts queries into safe, read-only SQL, executes them deterministically, and provides executive summaries.

---

## System Architecture

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

## Technology Stack

- **Core Programming Language**: Python 3.10+
- **Data Manipulation & Math**: Pandas, NumPy
- **Database & Query Engine**: SQLite / DuckDB (local analytical storage) / PostgreSQL (production), managed via SQLAlchemy ORM
- **SQL Security & Parsing**: SQLGlot (AST parsing, read-only enforcement, injection protection)
- **AI & Large Language Models**: Google Gemini API (`google-genai`), with pluggable support for OpenAI (`openai`)
- **Natural Language & Sentiment**: VADER Sentiment, TextBlob
- **User Interface & Visualization**: Streamlit, Plotly
- **Data Generation & Quality**: Faker, Pytest

---

## Directory Layout

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
│   └── database_schema.md        # Relational schema reference
│
├── src/ecommerce_iq/             # Core application package
│   ├── __init__.py
│   ├── database/                 # Connection pools, sessions, and engine setup
│   │   ├── __init__.py
│   │   └── connection.py
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
│   └── pages/                    # Dedicated analytical drill-down views
│       ├── 1_Sales_and_Revenue.py
│       ├── 2_Product_Performance.py
│       ├── 3_Customer_Behavior.py
│       ├── 4_Returns_and_Refunds.py
│       └── 5_Review_Sentiment.py
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

## Development Stages & Roadmap

| Phase | Milestone | Scope / Objectives | Status |
| :---: | :--- | :--- | :---: |
| **Phase 1** | **Project Foundation** | Architecture design, modular directory scaffolding, dependencies, configurations, and documentation. | **Current** |
| **Phase 2** | **Database & Data Generation** | Relational schemas, SQLAlchemy ORM entities, and realistic synthetic e-commerce dataset generation with seasonal trends and anomalies. | Upcoming |
| **Phase 3** | **Analytical Engine** | Deterministic formulas for sales, revenue, AOV, MoM/WoW comparative metrics, and return rate diagnostics. | Upcoming |
| **Phase 4** | **Customer Review NLP** | Sentiment classification, customer complaint topic extraction, and praise-driver identification. | Upcoming |
| **Phase 5** | **AI Copilot & Text-to-SQL** | Schema-grounded query generation, AST-based security validation, and executive business insight synthesis. | Upcoming |
| **Phase 6** | **Interactive UI Dashboard** | Multi-page Streamlit dashboard with executive KPI cards, Plotly visual charts, and conversational copilot chat. | Upcoming |
| **Phase 7** | **Testing, Verification & Git** | Comprehensive test coverage, end-to-end question verification, and publishing to GitHub. | Upcoming |

---

## Getting Started

### 1. Prerequisites
- Python 3.10 or higher
- Git

### 2. Environment Setup
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

### 3. Environment Configuration
Copy the sample environment file:
```bash
cp .env.example .env
```
Open `.env` and set your configuration variables (e.g., `GEMINI_API_KEY`).

### 4. Running the Project (When Implemented)
```bash
# Initialize and seed the analytical database (Phase 2)
python -m scripts.seed_data

# Run unit tests
pytest

# Launch the interactive BI Dashboard (Phase 6)
streamlit run ui/app.py
```

---

## License

This project is licensed under the [MIT License](LICENSE).
