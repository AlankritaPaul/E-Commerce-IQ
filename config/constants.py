"""
Application-Wide Business Constants and Enums.

Defines standardized enumerations for order statuses, return reasons,
sentiment labels, customer segments, and temporal periods.
"""

from enum import Enum


class OrderStatus(str, Enum):
    """Lifecycle statuses for customer orders."""
    COMPLETED = "completed"
    PENDING = "pending"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class ReturnReason(str, Enum):
    """Standard taxonomy of customer-stated return causes."""
    DEFECTIVE = "Defective/Damaged"
    WRONG_SIZE = "Incorrect Size/Fit"
    NOT_AS_PICTURED = "Item Not as Pictured"
    CHANGED_MIND = "Customer Changed Mind"
    LATE_DELIVERY = "Arrived Too Late"
    WRONG_ITEM = "Wrong Item Shipped"


class SentimentLabel(str, Enum):
    """Categorical sentiment ratings for customer reviews."""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class CustomerSegment(str, Enum):
    """Customer behavioral segment classifications."""
    NEW = "New"
    REGULAR = "Regular"
    VIP = "VIP High Value"
    AT_RISK = "At-Risk"
    CHURNED = "Churned"


class PeriodType(str, Enum):
    """Granularity for comparative time-series analytics."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
