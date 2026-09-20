"""
SQLAlchemy ORM Entity Definitions.

Defines normalized relational models corresponding to the E-Commerce IQ SQL Schema:
- Customer: Profile master records, segmentation, geographic distribution
- Category: Product taxonomy hierarchy
- Product: Catalog items, pricing, inventory balances, unit economics
- Order: Transaction headers, timestamps, statuses, financial totals
- OrderItem: Purchased line items with historical unit cost snapshots
- Payment: Settlement transaction records, payment methods, transaction references
- Return / ReturnAndRefund: Returned products, customer reasons, refund totals
- Review: Numerical star ratings (1-5), titles, written feedback
- ReviewInsight: AI-extracted sentiment polarity, scores, complaint themes
- Sale: Consolidated analytical performance and gross profit/margin ledger
"""

from datetime import date, datetime
from typing import Any, List, Optional
from src.ecommerce_iq.database.base import Base

try:
    from sqlalchemy import Boolean, CheckConstraint, Column, Date, DateTime, Float, ForeignKey, Integer, Numeric, String, Text
    from sqlalchemy.orm import relationship

    class Category(Base):  # type: ignore[valid-type, misc]
        """Product classification category hierarchy."""
        __tablename__ = "categories"

        category_id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(String(100), unique=True, nullable=False, index=True)
        slug = Column(String(120), unique=True, nullable=False, index=True)
        description = Column(Text, nullable=True)
        created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

        # Relationships
        products = relationship("Product", back_populates="category")

    class Customer(Base):  # type: ignore[valid-type, misc]
        """Customer profile master record and behavioral segmentation."""
        __tablename__ = "customers"

        customer_id = Column(Integer, primary_key=True, autoincrement=True)
        first_name = Column(String(100), nullable=False)
        last_name = Column(String(100), nullable=False)
        email = Column(String(255), unique=True, nullable=False, index=True)
        phone = Column(String(30), nullable=True)
        street_address = Column(String(255), nullable=True)
        city = Column(String(100), nullable=False)
        state = Column(String(100), nullable=True)
        postal_code = Column(String(20), nullable=True)
        country = Column(String(100), nullable=False, default="USA")
        customer_segment = Column(String(50), nullable=False, default="New", index=True)
        created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

        # Relationships
        orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")
        reviews = relationship("Review", back_populates="customer")
        returns = relationship("Return", back_populates="customer")
        sales = relationship("Sale", back_populates="customer")

    class Product(Base):  # type: ignore[valid-type, misc]
        """Catalog item with pricing, inventory count, and unit economics."""
        __tablename__ = "products"

        product_id = Column(Integer, primary_key=True, autoincrement=True)
        category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False, index=True)
        sku = Column(String(60), unique=True, nullable=False, index=True)
        title = Column(String(255), nullable=False)
        description = Column(Text, nullable=True)
        cost_price = Column(Float, nullable=False)
        retail_price = Column(Float, nullable=False, index=True)
        stock_quantity = Column(Integer, nullable=False, default=0)
        low_stock_threshold = Column(Integer, nullable=False, default=10)
        is_active = Column(Boolean, nullable=False, default=True, index=True)
        created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

        # Relationships
        category = relationship("Category", back_populates="products")
        order_items = relationship("OrderItem", back_populates="product")
        reviews = relationship("Review", back_populates="product")
        returns = relationship("Return", back_populates="product")
        sales = relationship("Sale", back_populates="product")

    class Order(Base):  # type: ignore[valid-type, misc]
        """Transaction header record."""
        __tablename__ = "orders"

        order_id = Column(Integer, primary_key=True, autoincrement=True)
        customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False, index=True)
        order_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
        status = Column(String(50), nullable=False, default="completed", index=True)
        subtotal = Column(Float, nullable=False)
        discount_amount = Column(Float, default=0.0, nullable=False)
        tax_amount = Column(Float, default=0.0, nullable=False)
        shipping_fee = Column(Float, default=0.0, nullable=False)
        total_amount = Column(Float, nullable=False, index=True)
        shipping_address = Column(String(255), nullable=True)
        billing_address = Column(String(255), nullable=True)
        created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

        # Relationships
        customer = relationship("Customer", back_populates="orders")
        items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
        payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")
        returns = relationship("Return", back_populates="order", cascade="all, delete-orphan")
        sales = relationship("Sale", back_populates="order", cascade="all, delete-orphan")

    class OrderItem(Base):  # type: ignore[valid-type, misc]
        """Purchased line items with historical snapshot of cost and selling price."""
        __tablename__ = "order_items"

        order_item_id = Column(Integer, primary_key=True, autoincrement=True)
        order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=False, index=True)
        product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False, index=True)
        quantity = Column(Integer, nullable=False, default=1)
        unit_price = Column(Float, nullable=False)
        unit_cost = Column(Float, nullable=False)
        discount_applied = Column(Float, default=0.0, nullable=False)
        item_total = Column(Float, nullable=False)

        # Relationships
        order = relationship("Order", back_populates="items")
        product = relationship("Product", back_populates="order_items")
        returns = relationship("Return", back_populates="order_item")
        sale = relationship("Sale", back_populates="order_item", uselist=False)

    class Payment(Base):  # type: ignore[valid-type, misc]
        """Transaction settlement record."""
        __tablename__ = "payments"

        payment_id = Column(Integer, primary_key=True, autoincrement=True)
        order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=False, index=True)
        payment_method = Column(String(50), nullable=False, index=True)
        transaction_reference = Column(String(100), unique=True, nullable=False)
        amount = Column(Float, nullable=False)
        status = Column(String(50), nullable=False, default="completed", index=True)
        payment_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

        # Relationships
        order = relationship("Order", back_populates="payments")

    class Return(Base):  # type: ignore[valid-type, misc]
        """Returned product, customer complaint reason, and refund record."""
        __tablename__ = "returns"

        return_id = Column(Integer, primary_key=True, autoincrement=True)
        order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=False, index=True)
        order_item_id = Column(Integer, ForeignKey("order_items.order_item_id"), nullable=False, index=True)
        product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False, index=True)
        customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False, index=True)
        quantity_returned = Column(Integer, nullable=False, default=1)
        return_reason = Column(String(100), nullable=False, index=True)
        detailed_notes = Column(Text, nullable=True)
        refund_amount = Column(Float, nullable=False)
        status = Column(String(50), nullable=False, default="approved", index=True)
        return_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

        # Relationships
        order = relationship("Order", back_populates="returns")
        order_item = relationship("OrderItem", back_populates="returns")
        product = relationship("Product", back_populates="returns")
        customer = relationship("Customer", back_populates="returns")

    # Convenience alias for Return
    ReturnAndRefund = Return

    class Review(Base):  # type: ignore[valid-type, misc]
        """Customer product review and numerical star rating."""
        __tablename__ = "reviews"

        review_id = Column(Integer, primary_key=True, autoincrement=True)
        product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False, index=True)
        customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False, index=True)
        order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=True)
        rating = Column(Integer, nullable=False, index=True)
        title = Column(String(255), nullable=True)
        comment = Column(Text, nullable=False)
        review_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
        verified_purchase = Column(Boolean, default=True, nullable=False)
        helpful_votes = Column(Integer, default=0, nullable=False)

        # Relationships
        product = relationship("Product", back_populates="reviews")
        customer = relationship("Customer", back_populates="reviews")
        insight = relationship("ReviewInsight", back_populates="review", uselist=False)

    class ReviewInsight(Base):  # type: ignore[valid-type, misc]
        """Pre-processed NLP sentiment and topic classification record."""
        __tablename__ = "review_insights"

        insight_id = Column(Integer, primary_key=True, autoincrement=True)
        review_id = Column(Integer, ForeignKey("reviews.review_id"), unique=True, nullable=False)
        sentiment_label = Column(String(20), nullable=False, index=True)
        sentiment_score = Column(Float, nullable=False)
        primary_topic = Column(String(100), nullable=True, index=True)
        detected_issue = Column(String(255), nullable=True)
        created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

        # Relationships
        review = relationship("Review", back_populates="insight")

    class Sale(Base):  # type: ignore[valid-type, misc]
        """Consolidated transactional sales, COGS, and profit margin fact record."""
        __tablename__ = "sales"

        sale_id = Column(Integer, primary_key=True, autoincrement=True)
        order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=False, index=True)
        order_item_id = Column(Integer, ForeignKey("order_items.order_item_id"), nullable=False)
        product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False, index=True)
        customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False, index=True)
        sale_date = Column(Date, nullable=False, index=True)
        quantity = Column(Integer, nullable=False)
        gross_revenue = Column(Float, nullable=False)
        discount_amount = Column(Float, default=0.0, nullable=False)
        net_revenue = Column(Float, nullable=False)
        cost_of_goods_sold = Column(Float, nullable=False)
        gross_profit = Column(Float, nullable=False)
        profit_margin_pct = Column(Float, nullable=False)
        is_refunded = Column(Boolean, default=False, nullable=False, index=True)
        refund_amount = Column(Float, default=0.0, nullable=False)
        created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

        # Relationships
        order = relationship("Order", back_populates="sales")
        order_item = relationship("OrderItem", back_populates="sale")
        product = relationship("Product", back_populates="sales")
        customer = relationship("Customer", back_populates="sales")

except ImportError:
    # Lightweight fallback entity class definitions for pre-dependency environments
    class Category(Base):  # type: ignore[no-redef]
        __tablename__ = "categories"
        category_id: int
        name: str
        slug: str
        description: Optional[str]

    class Customer(Base):  # type: ignore[no-redef]
        __tablename__ = "customers"
        customer_id: int
        first_name: str
        last_name: str
        email: str
        phone: Optional[str]
        city: str
        state: Optional[str]
        country: str
        customer_segment: str
        created_at: datetime

    class Product(Base):  # type: ignore[no-redef]
        __tablename__ = "products"
        product_id: int
        category_id: int
        sku: str
        title: str
        cost_price: float
        retail_price: float
        stock_quantity: int
        is_active: bool

    class Order(Base):  # type: ignore[no-redef]
        __tablename__ = "orders"
        order_id: int
        customer_id: int
        order_date: datetime
        status: str
        subtotal: float
        discount_amount: float
        tax_amount: float
        shipping_fee: float
        total_amount: float

    class OrderItem(Base):  # type: ignore[no-redef]
        __tablename__ = "order_items"
        order_item_id: int
        order_id: int
        product_id: int
        quantity: int
        unit_price: float
        unit_cost: float
        item_total: float

    class Payment(Base):  # type: ignore[no-redef]
        __tablename__ = "payments"
        payment_id: int
        order_id: int
        payment_method: str
        transaction_reference: str
        amount: float
        status: str

    class Return(Base):  # type: ignore[no-redef]
        __tablename__ = "returns"
        return_id: int
        order_id: int
        order_item_id: int
        product_id: int
        customer_id: int
        quantity_returned: int
        return_reason: str
        refund_amount: float
        status: str

    ReturnAndRefund = Return

    class Review(Base):  # type: ignore[no-redef]
        __tablename__ = "reviews"
        review_id: int
        product_id: int
        customer_id: int
        rating: int
        comment: str
        review_date: datetime

    class ReviewInsight(Base):  # type: ignore[no-redef]
        __tablename__ = "review_insights"
        insight_id: int
        review_id: int
        sentiment_label: str
        sentiment_score: float

    class Sale(Base):  # type: ignore[no-redef]
        __tablename__ = "sales"
        sale_id: int
        order_id: int
        order_item_id: int
        product_id: int
        customer_id: int
        sale_date: date
        gross_revenue: float
        net_revenue: float
        gross_profit: float
        profit_margin_pct: float
        is_refunded: bool
