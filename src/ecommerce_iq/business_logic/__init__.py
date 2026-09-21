"""
Business Logic & Domain Services Package.

Implements strategic performance diagnosis, customer segmentation algorithms,
and actionable business recommendations.
"""

from ecommerce_iq.business_logic.segmentation import CustomerSegmentationEngine
from ecommerce_iq.business_logic.diagnosis import BusinessPerformanceDiagnostic

__all__ = [
    "CustomerSegmentationEngine",
    "BusinessPerformanceDiagnostic",
]
