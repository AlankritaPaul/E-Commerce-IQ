"""
Data Models Package.

Exports declarative ORM entities and Pydantic validation/response schemas.
"""

from ecommerce_iq.models.entities import (
    Category,
    Customer,
    Order,
    OrderItem,
    Payment,
    Product,
    Return,
    ReturnAndRefund,
    Review,
    ReviewInsight,
    Sale,
)
from ecommerce_iq.models.schemas import (
    AIQueryRequest,
    AIQueryResponse,
    DiagnosticReport,
    KPISummary,
    PeriodComparisonResult,
    ProductPerformanceMetric,
    RecommendationItem,
    ReturnReasonMetric,
    ReviewSentimentSummary,
)

__all__ = [
    # Entities
    "Category",
    "Customer",
    "Product",
    "Order",
    "OrderItem",
    "Payment",
    "Return",
    "ReturnAndRefund",
    "Review",
    "ReviewInsight",
    "Sale",
    # Schemas
    "KPISummary",
    "PeriodComparisonResult",
    "ProductPerformanceMetric",
    "ReturnReasonMetric",
    "ReviewSentimentSummary",
    "AIQueryRequest",
    "AIQueryResponse",
    "DiagnosticReport",
    "RecommendationItem",
]
