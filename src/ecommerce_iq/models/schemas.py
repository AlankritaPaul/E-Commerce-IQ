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
