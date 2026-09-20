# E-Commerce IQ Architecture Document

## 1. System Overview

**E-Commerce IQ** is designed as a modular, enterprise-ready decision support platform. It delivers real-time business intelligence to e-commerce executives by combining deterministic analytics with natural language understanding.

### Core Architectural Goals:
1. **Financial Accuracy**: Ensure that core metrics (revenue, margins, return rates) are computed via deterministic, auditable SQL and Python calculations rather than probabilistic LLM approximations.
2. **Context-Rich Intelligence**: Provide conversational inquiry that explains the *why* behind metric movements (e.g. why did sales dip, which products have defective batches).
3. **Pluggable & Secure AI**: Guardrail all LLM interactions using Abstract Syntax Tree (AST) validation to enforce read-only database operations.
4. **Decoupled Layers**: Enforce strict separation between data access, metric computation, domain business logic, AI orchestration, and presentation.

---

## 2. Layered Architecture

The system consists of five distinct architectural tiers:

```
[ Tier 1: Presentation Layer (Streamlit Multi-Page UI) ]
   ├── Executive Overview Dashboard
   ├── Product Performance Drilldowns
   ├── Customer Behavior & Sentiment Analysis
   └── Conversational BI Copilot (Chat Interface)
                            │
                            ▼
[ Tier 2: AI & Natural Language Processing Layer ]
   ├── Intent Classification & Query Routing
   ├── Text-to-SQL Generator (Schema-Grounded)
   ├── SQL Security Guardrails (AST Read-Only Validator)
   └── Executive Narrative Synthesizer (Insights & Root Cause)
                            │
                            ▼
[ Tier 3: Domain & Business Logic Layer ]
   ├── Performance Anomaly Diagnosis
   ├── RFM Customer Segmentation
   └── Actionable Strategy Recommendations
                            │
                            ▼
[ Tier 4: Deterministic Analytics Engine ]
   ├── KPI Metric Calculations (Revenue, GMV, AOV, Margin)
   ├── Period-over-Period Variance (MoM, WoW, YoY)
   ├── Return Rate & Defect Aggregations
   └── Review Sentiment & Polarity Indexing
                            │
                            ▼
[ Tier 5: Storage & Persistence Layer ]
   ├── Relational Analytical Database (SQLite / DuckDB / PostgreSQL)
   ├── SQLAlchemy Connection Management & Object Relational Mapping
   └── Materialized Daily Metric Rollups
```

---

## 3. The Dual-Engine Query Lifecycle

When a business owner submits a prompt (e.g., *"Why did sales decrease in Electronics this month?"*):

1. **Routing & Context Injection**:
   - The user's query is received by the application orchestrator.
   - Database schema definitions, business metric definitions, and current date context are injected into the prompt.
2. **Deterministic Query Generation**:
   - The AI engine generates candidate SQL queries targeting specific tables (`orders`, `order_items`, `products`, `returns_and_refunds`, `reviews`).
3. **AST Guardrail Validation**:
   - The query passes through the `sql_guardrails` module.
   - The SQL is parsed into an Abstract Syntax Tree (AST).
   - Only `SELECT` statements are permitted. Destructive operations (`DROP`, `DELETE`, `UPDATE`, `ALTER`, `TRUNCATE`) and schema modifications are blocked.
4. **Deterministic Execution**:
   - The validated query executes against the database via SQLAlchemy, returning a structured Pandas DataFrame.
5. **Synthesis & Insight Generation**:
   - The exact numerical results, along with historical period baselines and relevant review themes, are passed to the executive advisor.
   - The advisor synthesizes an answer that highlights the root cause: (e.g., *"Sales in Electronics fell 22% MoM. While volume was steady, returns spiked to 19% driven by battery defects reported in 12 customer reviews."*).
