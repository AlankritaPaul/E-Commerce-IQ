# E-Commerce IQ: 11 Implementation Stages Reference

This document maps all 11 project stages—using the **exact titles and serial numbers as defined by the user**—directly to their implementation files, UI screens, and test suites.

---

## Complete Stage Directory

| Stage Serial & Name | Core Implementation Files | Dedicated UI View File | Test Suite File | Status |
| :--- | :--- | :--- | :--- | :--- |
| **1. The Foundation of The Whole System** | `src/ecommerce_iq/database/schema.sql`<br>`src/ecommerce_iq/database/connection.py`<br>`src/ecommerce_iq/models/entities.py`<br>`src/ecommerce_iq/models/schemas.py`<br>`scripts/init_db.py` | `ui/pages/01_The_Foundation_of_The_Whole_System.py`<br>`ui/pages/foundation_view.py` | `tests/test_database.py`<br>`tests/test_models.py`<br>`tests/test_config.py` | ✅ Verified & Tested |
| **2. Realistic Business Dataset** | `src/ecommerce_iq/database/seeder.py`<br>`scripts/seed_mock_data.py` | `ui/pages/02_Realistic_Business_Dataset.py`<br>`ui/pages/dataset_view.py` | `tests/test_dataset.py` | ✅ Verified & Tested |
| **3. Sales & Revenue Analytics** | `src/ecommerce_iq/analytics/kpis.py`<br>`src/ecommerce_iq/analytics/comparisons.py` | `ui/pages/03_Sales_and_Revenue_Analytics.py`<br>`ui/pages/sales_view.py` | `tests/test_analytics.py` | ✅ Verified & Tested |
| **4. Product Performance** | `src/ecommerce_iq/analytics/products.py` | `ui/pages/04_Product_Performance.py`<br>`ui/pages/products_view.py` | `tests/test_analytics.py` | ✅ Verified & Tested |
| **5. Customer Analysis** | `src/ecommerce_iq/analytics/customers.py`<br>`src/ecommerce_iq/business_logic/segmentation.py` | `ui/pages/05_Customer_Analysis.py`<br>`ui/pages/customers_view.py` | `tests/test_customers.py` | ✅ Verified & Tested |
| **6. Customer Response** | `src/ecommerce_iq/analytics/reviews.py`<br>`src/ecommerce_iq/ai/sentiment.py` | `ui/pages/06_Customer_Response.py`<br>`ui/pages/reviews_view.py` | `tests/test_reviews.py` | ✅ Verified & Tested |
| **7. Returns & Refunds** | `src/ecommerce_iq/analytics/returns.py` | `ui/pages/07_Returns_and_Refunds.py`<br>`ui/pages/returns_view.py` | `tests/test_returns.py` | ✅ Verified & Tested |
| **8. Why did sales decrease?** | `src/ecommerce_iq/business_logic/diagnosis.py` | `ui/pages/08_Why_Did_Sales_Decrease.py`<br>`ui/pages/diagnosis_view.py` | `tests/test_diagnosis.py` | ✅ Verified & Tested |
| **9. Natural-language business questions:** | `src/ecommerce_iq/ai/query_engine.py`<br>`src/ecommerce_iq/ai/text_to_sql.py`<br>`src/ecommerce_iq/ai/sql_guardrails.py`<br>`src/ecommerce_iq/ai/advisor.py` | `ui/pages/09_Natural_Language_Business_Questions.py`<br>`ui/pages/copilot_view.py` | `tests/test_ai.py` | ✅ Verified & Tested |
| **10. AI answer layer:** | `src/ecommerce_iq/ai/interpretation.py`<br>(`AnalyticsInterpreter`, `NumericalGroundingVerifier`) | `ui/pages/10_AI_Answer_Layer.py`<br>`ui/pages/interpretation_view.py` | `tests/test_interpretation.py` | ✅ Verified & Tested |
| **11. Professional Interface** | `ui/app.py`<br>`ui/components/cards.py`<br>`ui/components/charts.py`<br>`ui/components/chat.py` | `ui/pages/11_Professional_Interface.py`<br>`ui/app.py` | `tests/test_ui.py` | ✅ Verified & Tested |

---

## Detailed Stage Breakdown

### 1. The Foundation of The Whole System
- **Purpose**: Establishes a production-grade normalized SQL relational schema with foreign key constraints, check constraints, and typed ORM entity mappings.
- **Implemented In**:
  - `src/ecommerce_iq/database/schema.sql` (8 normalized tables + 2 analytical views)
  - `src/ecommerce_iq/database/connection.py` (`DatabaseManager`)
  - `src/ecommerce_iq/models/entities.py` (SQLAlchemy ORM Entities)
  - `src/ecommerce_iq/models/schemas.py` (Typed Pydantic & Dataclass DTOs)

### 2. Realistic Business Dataset
- **Purpose**: Generates a deterministic 14-month synthetic business dataset with embedded anomalies (e.g. August 2025 -61% sales dip, Q4 holiday peak, defective batch return spike).
- **Implemented In**:
  - `src/ecommerce_iq/database/seeder.py` (4,061 orders, 850 customers, 2,067 reviews, $647,823.33 revenue)
  - `scripts/seed_mock_data.py` (CLI dataset seeder)

### 3. Sales & Revenue Analytics
- **Purpose**: Direct SQL calculation engines for GMV, Net Revenue, completed orders, AOV, and Month-over-Month (MoM) / Week-over-Week (WoW) variance.
- **Implemented In**:
  - `src/ecommerce_iq/analytics/kpis.py` (`KPICalculator`)
  - `src/ecommerce_iq/analytics/comparisons.py` (`PeriodComparisonEngine`)

### 4. Product Performance
- **Purpose**: Multi-dimensional SKU performance analysis, unit profit margins, bestsellers, dead stock, and composite 0–100 Product Health Scores.
- **Implemented In**:
  - `src/ecommerce_iq/analytics/products.py` (`ProductAnalyticsEngine`)

### 5. Customer Analysis
- **Purpose**: Behavioral profiling, repeat purchase rates (96.75%), RFM quintile segmentation (Champions, Loyal, At-Risk), churn risk cohorts, and strict PII masking.
- **Implemented In**:
  - `src/ecommerce_iq/analytics/customers.py` (`CustomerAnalyticsEngine`)
  - `src/ecommerce_iq/business_logic/segmentation.py` (`CustomerSegmentationEngine`)

### 6. Customer Response
- **Purpose**: CSAT rating metrics, 1–5 star distributions, explainable sentiment polarity scoring, recurring defect topic clustering, and verbatim quote extraction.
- **Implemented In**:
  - `src/ecommerce_iq/analytics/reviews.py` (`ReviewAnalyticsEngine`)
  - `src/ecommerce_iq/ai/sentiment.py` (`SentimentAnalyzer`)

### 7. Returns & Refunds
- **Purpose**: Platform return rate (4.76%), refund dollar leakage ($41,137.50), customer RMA return reasons, high-risk SKUs, and cross-triangulation with customer reviews.
- **Implemented In**:
  - `src/ecommerce_iq/analytics/returns.py` (`ReturnsAnalyticsEngine`)

### 8. Why did sales decrease?
- **Purpose**: Empirical business diagnosis module investigating performance declines (such as the August 2025 -61.03% revenue collapse), identifying 8 quantitative metrics, product decline attribution, and review signals.
- **Implemented In**:
  - `src/ecommerce_iq/business_logic/diagnosis.py` (`BusinessPerformanceDiagnostic`)

### 9. Natural-language business questions:
- **Purpose**: Secure conversational copilot translating business owner questions into schema-grounded SQL with AST read-only guardrails, token inspection, and row limits.
- **Implemented In**:
  - `src/ecommerce_iq/ai/query_engine.py` (`NaturalLanguageQueryEngine`)
  - `src/ecommerce_iq/ai/text_to_sql.py` (`TextToSQLGenerator`)
  - `src/ecommerce_iq/ai/sql_guardrails.py` (`SQLGuardrail`)
  - `src/ecommerce_iq/ai/advisor.py` (`BusinessAdvisor`)

### 10. AI answer layer:
- **Purpose**: Translates analytical outputs into executive business briefings with strict anti-hallucination numerical grounding, auditing every number against verified database facts.
- **Implemented In**:
  - `src/ecommerce_iq/ai/interpretation.py` (`AnalyticsInterpreter`, `NumericalGroundingVerifier`)

### 11. Professional Interface
- **Purpose**: Clean, corporate-grade Streamlit decision intelligence application with multi-page drilldowns, interactive Plotly visualizations, metric cards, and natural-language AI copilot.
- **Implemented In**:
  - `ui/app.py` (Application routing & Executive Overview)
  - `ui/components/cards.py`, `charts.py`, `chat.py`
  - `ui/pages/` (All 11 numbered stage drilldown pages)
