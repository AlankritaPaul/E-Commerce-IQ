"""
Analytics Package.

Deterministic calculation engines for revenue, sales performance, temporal
comparisons, product unit economics, and return rates.
"""

from ecommerce_iq.analytics.base import BaseAnalyticsEngine
from ecommerce_iq.analytics.kpis import KPICalculator
from ecommerce_iq.analytics.comparisons import PeriodComparisonEngine
from ecommerce_iq.analytics.products import ProductAnalyticsEngine
from ecommerce_iq.analytics.returns import ReturnsAnalyticsEngine
from ecommerce_iq.analytics.customers import CustomerAnalyticsEngine

__all__ = [
    "BaseAnalyticsEngine",
    "KPICalculator",
    "PeriodComparisonEngine",
    "ProductAnalyticsEngine",
    "ReturnsAnalyticsEngine",
    "CustomerAnalyticsEngine",
]

