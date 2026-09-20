# E-Commerce IQ Module Reference

This document details the responsibilities, interfaces, and design patterns of each package and module in E-Commerce IQ.

---

## 1. `config/` (Configuration & Environment)

| Module | Responsibility | Public Symbols |
| :--- | :--- | :--- |
| `config.settings` | Loads environment variables from `.env` with validation and fallback. | `Settings`, `get_settings()` |
| `config.constants` | Standardized enums for orders, return causes, sentiment labels, segments. | `OrderStatus`, `ReturnReason`, `SentimentLabel`, `CustomerSegment`, `PeriodType` |

---

## 2. `src.ecommerce_iq.database/` (Data Persistence)

| Module | Responsibility | Public Symbols |
| :--- | :--- | :--- |
| `database.base` | Declarative Base class for SQLAlchemy ORM mapping. | `Base` |
| `database.connection` | Engine lifecycle, connection pooling, and context-managed sessions. | `DatabaseManager` (`session_scope()`, `execute_query()`) |

---

## 3. `src.ecommerce_iq.models/` (Data Models & Schemas)

| Module | Responsibility | Public Symbols |
| :--- | :--- | :--- |
| `models.entities` | Normalized SQLAlchemy ORM models representing the 8 core tables. | `Customer`, `Category`, `Product`, `Order`, `OrderItem`, `ReturnAndRefund`, `Review`, `ReviewInsight` |
| `models.schemas` | Pydantic / dataclass DTOs for KPI metrics, period variance, and AI queries. | `KPISummary`, `PeriodComparisonResult`, `ProductPerformanceMetric`, `AIQueryRequest`, `AIQueryResponse` |

---

## 4. `src.ecommerce_iq.analytics/` (Deterministic Analytics)

| Module | Responsibility | Public Symbols |
| :--- | :--- | :--- |
| `analytics.base` | Common base class with query helpers and date range formatting. | `BaseAnalyticsEngine` |
| `analytics.kpis` | Exact calculations for GMV, Net Revenue, AOV, Gross Margin. | `KPICalculator` |
| `analytics.comparisons` | Temporal variance calculations across MoM, WoW, and YoY. | `PeriodComparisonEngine` |
| `analytics.products` | Unit economics, top performers, and category distributions. | `ProductAnalyticsEngine` |
| `analytics.returns` | Product return rates, refund totals, and defect root causes. | `ReturnsAnalyticsEngine` |

---

## 5. `src.ecommerce_iq.business_logic/` (Domain Services)

| Module | Responsibility | Public Symbols |
| :--- | :--- | :--- |
| `business_logic.diagnosis` | Multi-factor anomaly detection and decline root-cause diagnosis. | `BusinessPerformanceDiagnostic` |
| `business_logic.segmentation` | RFM behavioral clustering and churn risk cohorts. | `CustomerSegmentationEngine` |
| `business_logic.recommendations` | Actionable executive recommendations based on diagnostic outputs. | `RecommendationEngine` |

---

## 6. `src.ecommerce_iq.ai/` (AI & Natural Language Processing)

| Module | Responsibility | Public Symbols |
| :--- | :--- | :--- |
| `ai.prompts` | Centralized system prompt templates for SQL generation and analysis. | `TEXT_TO_SQL_SYSTEM_PROMPT`, `BUSINESS_ADVISOR_SYSTEM_PROMPT` |
| `ai.sql_guardrails` | Security validator enforcing read-only SQL and blocking statement chaining. | `SQLGuardrail` (`validate_query()`) |
| `ai.llm_client` | Pluggable client interface for Gemini, OpenAI, and local LLMs. | `LLMClient` (`generate_text()`, `generate_structured()`) |
| `ai.text_to_sql` | Translates plain-English questions into schema-grounded SQL. | `TextToSQLGenerator` (`generate_sql()`) |
| `ai.sentiment` | Extracts review sentiment polarity, scores, and customer feedback topics. | `SentimentAnalyzer` (`analyze_text()`) |
| `ai.advisor` | Synthesizes verified data into concise executive explanations. | `BusinessAdvisor` (`synthesize_answer()`) |

---

## 7. `src.ecommerce_iq.utils/` (Cross-Cutting Utilities)

| Module | Responsibility | Public Symbols |
| :--- | :--- | :--- |
| `utils.formatting` | Formatters for currency (`$1,234.56`), percentages, and delta indicators. | `format_currency()`, `format_percentage()`, `format_delta_display()` |
| `utils.logging` | Application-wide structured logging configuration. | `setup_logger()` |
| `utils.validators` | Parameter sanitization and date range validation. | `validate_date_range()`, `clamp_limit()`, `sanitize_identifier()` |

---

## 8. `ui/` (Presentation & Dashboard)

| Directory / File | Responsibility |
| :--- | :--- |
| `ui.app` | Main Streamlit dashboard application entrypoint. |
| `ui.components.cards` | Executive KPI metric cards with directional trend indicators. |
| `ui.components.charts` | Interactive Plotly charts (Revenue trends, Category donuts, Return bars). |
| `ui.components.chat` | Natural language conversational Copilot interface. |
| `ui.pages` | 5 dedicated analytical drilldowns (Sales, Products, Customers, Returns, Reviews). |
