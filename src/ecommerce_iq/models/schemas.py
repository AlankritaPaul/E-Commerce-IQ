"""
Data Transfer Objects and Typed Validation Schemas.

Defines schemas for:
- Core entity representations (Customers, Products, Orders, Reviews)
- Analytical summaries (KPIs, Period comparisons, Return metrics)
- AI Copilot interactions (Query requests, SQL generation, executive responses)
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from config.constants import CustomerSegment, OrderStatus, PeriodType, ReturnReason, SentimentLabel


# ==============================================================================
# Analytical Metrics Schemas
# ==============================================================================

@dataclass
class KPISummary:
    """High-level executive business performance scorecard."""
    total_revenue: float
    net_revenue: float
    total_orders: int
    average_order_value: float
    total_refunds: float
    return_rate_percentage: float
    active_customers: int
    gross_margin_percentage: Optional[float] = None


@dataclass
class PeriodComparisonResult:
    """Variance analysis between two temporal periods (MoM, WoW, YoY)."""
    metric_name: str
    current_value: float
    previous_value: float
    absolute_change: float
    percentage_change: float
    trend_direction: str  # 'positive', 'negative', 'neutral'


@dataclass
class ProductPerformanceMetric:
    """Product-level revenue, unit sales, and return velocity."""
    product_id: int
    sku: str
    title: str
    category_name: str
    units_sold: int
    total_revenue: float
    total_returns: int
    return_rate_pct: float
    avg_rating: float


@dataclass
class ReturnReasonMetric:
    """Breakdown of return causes and associated financial loss."""
    reason: str
    incident_count: int
    total_refund_amount: float
    percentage_of_all_returns: float


@dataclass
class ReviewSentimentSummary:
    """Overall review sentiment breakdown."""
    total_reviews: int
    average_rating: float
    positive_count: int
    neutral_count: int
    negative_count: int
    positive_percentage: float
    negative_percentage: float
    top_complaints: List[str] = field(default_factory=list)
    top_praises: List[str] = field(default_factory=list)


@dataclass
class CustomerAggregateSummary:
    """High-level customer behavioral intelligence scorecard."""
    total_registered_customers: int
    active_purchasers: int
    repeat_customers: int
    one_time_buyers: int
    repeat_purchase_rate_pct: float
    average_customer_ltv: float
    average_order_frequency: float
    customer_return_rate_pct: float
    review_participation_rate_pct: float
    segment_breakdown: Dict[str, int] = field(default_factory=dict)


@dataclass
class CustomerProfile:
    """Customer profile record with PII-protected display formatting."""
    customer_id: int
    display_name: str  # e.g. "Emma S." (PII protected)
    city: str
    country: str
    segment: str
    order_count: int
    total_spend: float  # Lifetime spend
    average_order_value: float
    first_order_date: str
    last_order_date: str
    days_since_last_order: int
    returns_count: int
    total_refunds: float
    return_rate_pct: float
    reviews_count: int
    average_rating_given: float
    is_repeat_buyer: bool


@dataclass
class RFMCustomerScore:
    """Individual customer Recency, Frequency, and Monetary (RFM) quintile evaluation."""
    customer_id: int
    display_name: str  # Masked PII: "First L."
    city: str
    country: str
    recency_days: int
    frequency_orders: int
    monetary_spend: float
    r_score: int  # 1 (least recent) to 5 (most recent)
    f_score: int  # 1 (lowest frequency) to 5 (highest frequency)
    m_score: int  # 1 (lowest spend) to 5 (highest spend)
    rfm_score_str: str  # e.g. "555"
    rfm_segment: str   # e.g. "Champions", "Loyal Customers", "At Risk"


@dataclass
class ChurnRiskCustomer:
    """Customer flagged for potential churn based on recency and past spending."""
    customer_id: int
    display_name: str  # Masked PII: "First L."
    city: str
    country: str
    segment: str
    orders_placed: int
    total_spend: float
    average_order_value: float
    days_since_last_order: int
    risk_level: str  # 'Critical', 'High', 'Moderate'
    estimated_revenue_at_risk: float


# ==============================================================================
# AI & Copilot Schemas
# ==============================================================================

@dataclass
class AIQueryRequest:
    """Incoming user query to the AI BI Copilot."""
    user_query: str
    session_id: Optional[str] = None
    date_filter: Optional[str] = None


@dataclass
class AIQueryResponse:
    """Structured response from the natural language query copilot."""
    user_query: str
    generated_sql: str
    is_safe: bool
    data: Optional[List[Dict[str, Any]]] = None
    executive_summary: Optional[str] = None
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0


@dataclass
class DiagnosticReport:
    """Automated root-cause analysis report for business performance shifts."""
    title: str
    period_analyzed: str
    primary_finding: str
    contributing_factors: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)


@dataclass
class RecommendationItem:
    """Actionable operational business recommendation."""
    priority: str  # 'High', 'Medium', 'Low'
    category: str  # 'Inventory', 'Quality', 'Marketing', 'Customer Support'
    title: str
    action: str
    expected_impact: str
