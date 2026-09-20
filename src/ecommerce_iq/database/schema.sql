-- =============================================================================
-- E-Commerce IQ - Enterprise Relational Database Schema
-- Dialect: ANSI SQL / SQLite 3.x+ / PostgreSQL Compatible
-- =============================================================================

PRAGMA foreign_keys = ON;

-- -----------------------------------------------------------------------------
-- 1. CATEGORIES (Catalog Hierarchy)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(120) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_categories_name ON categories(name);
CREATE INDEX IF NOT EXISTS idx_categories_slug ON categories(slug);

-- -----------------------------------------------------------------------------
-- 2. CUSTOMERS (Master Profile & Segmentation)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(30),
    street_address VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100) NOT NULL DEFAULT 'USA',
    customer_segment VARCHAR(50) NOT NULL DEFAULT 'New' CHECK (customer_segment IN ('New', 'Regular', 'VIP High Value', 'At-Risk', 'Churned')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_customers_segment ON customers(customer_segment);
CREATE INDEX IF NOT EXISTS idx_customers_city_country ON customers(country, city);
CREATE INDEX IF NOT EXISTS idx_customers_created_at ON customers(created_at);

-- -----------------------------------------------------------------------------
-- 3. PRODUCTS (Catalog, Inventory & Unit Economics)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    sku VARCHAR(60) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    cost_price DECIMAL(10, 2) NOT NULL CHECK (cost_price >= 0),
    retail_price DECIMAL(10, 2) NOT NULL CHECK (retail_price >= 0),
    stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    low_stock_threshold INTEGER NOT NULL DEFAULT 10 CHECK (low_stock_threshold >= 0),
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_products_category_id ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);
CREATE INDEX IF NOT EXISTS idx_products_retail_price ON products(retail_price);
CREATE INDEX IF NOT EXISTS idx_products_stock ON products(stock_quantity);
CREATE INDEX IF NOT EXISTS idx_products_active ON products(is_active);

-- -----------------------------------------------------------------------------
-- 4. ORDERS (Transaction Headers)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    order_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'completed' CHECK (status IN ('pending', 'processing', 'completed', 'shipped', 'cancelled', 'refunded')),
    subtotal DECIMAL(10, 2) NOT NULL CHECK (subtotal >= 0),
    discount_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00 CHECK (discount_amount >= 0),
    tax_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00 CHECK (tax_amount >= 0),
    shipping_fee DECIMAL(10, 2) NOT NULL DEFAULT 0.00 CHECK (shipping_fee >= 0),
    total_amount DECIMAL(10, 2) NOT NULL CHECK (total_amount >= 0),
    shipping_address VARCHAR(255),
    billing_address VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_total_amount ON orders(total_amount);
CREATE INDEX IF NOT EXISTS idx_orders_customer_date ON orders(customer_id, order_date);

-- -----------------------------------------------------------------------------
-- 5. ORDER_ITEMS (Purchased Line Items with Historical Cost Snapshots)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL CHECK (unit_price >= 0),
    unit_cost DECIMAL(10, 2) NOT NULL CHECK (unit_cost >= 0),
    discount_applied DECIMAL(10, 2) NOT NULL DEFAULT 0.00 CHECK (discount_applied >= 0),
    item_total DECIMAL(10, 2) NOT NULL CHECK (item_total >= 0),
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_order_items_order_product ON order_items(order_id, product_id);

-- -----------------------------------------------------------------------------
-- 6. PAYMENTS (Transaction Settlement Records)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    payment_method VARCHAR(50) NOT NULL CHECK (payment_method IN ('credit_card', 'debit_card', 'paypal', 'apple_pay', 'google_pay', 'bank_transfer', 'store_credit')),
    transaction_reference VARCHAR(100) NOT NULL UNIQUE,
    amount DECIMAL(10, 2) NOT NULL CHECK (amount >= 0),
    status VARCHAR(50) NOT NULL DEFAULT 'completed' CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
    payment_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_payments_order_id ON payments(order_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_method ON payments(payment_method);
CREATE INDEX IF NOT EXISTS idx_payments_date ON payments(payment_date);

-- -----------------------------------------------------------------------------
-- 7. RETURNS (Returns, Defect Tracking & Refunds Issued)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS returns (
    return_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    order_item_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    quantity_returned INTEGER NOT NULL DEFAULT 1 CHECK (quantity_returned > 0),
    return_reason VARCHAR(100) NOT NULL CHECK (return_reason IN (
        'Defective/Damaged',
        'Incorrect Size/Fit',
        'Item Not as Pictured',
        'Customer Changed Mind',
        'Arrived Too Late',
        'Wrong Item Shipped',
        'Other'
    )),
    detailed_notes TEXT,
    refund_amount DECIMAL(10, 2) NOT NULL CHECK (refund_amount >= 0),
    status VARCHAR(50) NOT NULL DEFAULT 'approved' CHECK (status IN ('requested', 'approved', 'rejected', 'completed')),
    return_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (order_item_id) REFERENCES order_items(order_item_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_returns_order_id ON returns(order_id);
CREATE INDEX IF NOT EXISTS idx_returns_item_id ON returns(order_item_id);
CREATE INDEX IF NOT EXISTS idx_returns_product_id ON returns(product_id);
CREATE INDEX IF NOT EXISTS idx_returns_customer_id ON returns(customer_id);
CREATE INDEX IF NOT EXISTS idx_returns_reason ON returns(return_reason);
CREATE INDEX IF NOT EXISTS idx_returns_date ON returns(return_date);
CREATE INDEX IF NOT EXISTS idx_returns_status ON returns(status);
CREATE INDEX IF NOT EXISTS idx_returns_product_reason ON returns(product_id, return_reason);

-- -----------------------------------------------------------------------------
-- 8. REVIEWS (Customer Feedback & Star Ratings)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    order_id INTEGER,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(255),
    comment TEXT NOT NULL,
    review_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    verified_purchase BOOLEAN NOT NULL DEFAULT 1,
    helpful_votes INTEGER NOT NULL DEFAULT 0 CHECK (helpful_votes >= 0),
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE RESTRICT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_reviews_product_id ON reviews(product_id);
CREATE INDEX IF NOT EXISTS idx_reviews_customer_id ON reviews(customer_id);
CREATE INDEX IF NOT EXISTS idx_reviews_rating ON reviews(rating);
CREATE INDEX IF NOT EXISTS idx_reviews_date ON reviews(review_date);
CREATE INDEX IF NOT EXISTS idx_reviews_product_rating ON reviews(product_id, rating);

-- -----------------------------------------------------------------------------
-- 9. REVIEW_INSIGHTS (NLP Sentiment & Topic Classification)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS review_insights (
    insight_id INTEGER PRIMARY KEY AUTOINCREMENT,
    review_id INTEGER NOT NULL UNIQUE,
    sentiment_label VARCHAR(20) NOT NULL CHECK (sentiment_label IN ('positive', 'neutral', 'negative')),
    sentiment_score DECIMAL(5, 4) NOT NULL CHECK (sentiment_score >= -1.0 AND sentiment_score <= 1.0),
    primary_topic VARCHAR(100),
    detected_issue VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (review_id) REFERENCES reviews(review_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_insights_review_id ON review_insights(review_id);
CREATE INDEX IF NOT EXISTS idx_insights_sentiment ON review_insights(sentiment_label);
CREATE INDEX IF NOT EXISTS idx_insights_topic ON review_insights(primary_topic);

-- -----------------------------------------------------------------------------
-- 10. SALES (Consolidated Performance & Margin Fact Table)
-- Provides fast, O(1) aggregation for BI queries without multi-table joins.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sales (
    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    order_item_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    sale_date DATE NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    gross_revenue DECIMAL(10, 2) NOT NULL CHECK (gross_revenue >= 0),
    discount_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00 CHECK (discount_amount >= 0),
    net_revenue DECIMAL(10, 2) NOT NULL CHECK (net_revenue >= 0),
    cost_of_goods_sold DECIMAL(10, 2) NOT NULL CHECK (cost_of_goods_sold >= 0),
    gross_profit DECIMAL(10, 2) NOT NULL,
    profit_margin_pct DECIMAL(6, 2) NOT NULL,
    is_refunded BOOLEAN NOT NULL DEFAULT 0,
    refund_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00 CHECK (refund_amount >= 0),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (order_item_id) REFERENCES order_items(order_item_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_sales_sale_date ON sales(sale_date);
CREATE INDEX IF NOT EXISTS idx_sales_product_id ON sales(product_id);
CREATE INDEX IF NOT EXISTS idx_sales_customer_id ON sales(customer_id);
CREATE INDEX IF NOT EXISTS idx_sales_order_id ON sales(order_id);
CREATE INDEX IF NOT EXISTS idx_sales_is_refunded ON sales(is_refunded);
CREATE INDEX IF NOT EXISTS idx_sales_date_product ON sales(sale_date, product_id);
CREATE INDEX IF NOT EXISTS idx_sales_date_revenue ON sales(sale_date, net_revenue);

-- -----------------------------------------------------------------------------
-- ANALYTICAL VIEWS FOR HIGH-PERFORMANCE BI
-- -----------------------------------------------------------------------------

-- View 1: Product Performance & Return Rate Aggregation (CTE to prevent join fan-out)
CREATE VIEW IF NOT EXISTS v_product_performance_summary AS
WITH sales_agg AS (
    SELECT 
        oi.product_id,
        COALESCE(SUM(oi.quantity), 0) AS total_units_sold,
        COALESCE(SUM(oi.item_total), 0.00) AS total_gross_revenue
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id AND o.status = 'completed'
    GROUP BY oi.product_id
),
returns_agg AS (
    SELECT 
        product_id,
        COALESCE(SUM(quantity_returned), 0) AS total_units_returned
    FROM returns
    GROUP BY product_id
),
reviews_agg AS (
    SELECT 
        product_id,
        ROUND(AVG(rating), 2) AS average_rating,
        COUNT(review_id) AS total_reviews
    FROM reviews
    GROUP BY product_id
)
SELECT 
    p.product_id,
    p.sku,
    p.title,
    c.name AS category_name,
    p.cost_price,
    p.retail_price,
    p.stock_quantity,
    COALESCE(s.total_units_sold, 0) AS total_units_sold,
    COALESCE(s.total_gross_revenue, 0.00) AS total_gross_revenue,
    COALESCE(r.total_units_returned, 0) AS total_units_returned,
    ROUND(
        CASE 
            WHEN COALESCE(s.total_units_sold, 0) > 0 
            THEN (COALESCE(r.total_units_returned, 0) * 100.0) / s.total_units_sold
            ELSE 0.0 
        END, 2
    ) AS return_rate_percentage,
    COALESCE(rev.average_rating, 0.0) AS average_rating,
    COALESCE(rev.total_reviews, 0) AS total_reviews
FROM products p
JOIN categories c ON p.category_id = c.category_id
LEFT JOIN sales_agg s ON p.product_id = s.product_id
LEFT JOIN returns_agg r ON p.product_id = r.product_id
LEFT JOIN reviews_agg rev ON p.product_id = rev.product_id;

-- View 2: Daily Business Scorecard Rollup (CTE to prevent join fan-out)
CREATE VIEW IF NOT EXISTS v_daily_business_summary AS
WITH daily_orders AS (
    SELECT 
        DATE(order_date) AS summary_date,
        COUNT(DISTINCT order_id) AS total_orders,
        COUNT(DISTINCT customer_id) AS active_purchasers,
        SUM(subtotal) AS gross_sales,
        SUM(discount_amount) AS total_discounts,
        SUM(total_amount) AS net_revenue,
        ROUND(AVG(total_amount), 2) AS average_order_value
    FROM orders
    WHERE status = 'completed'
    GROUP BY DATE(order_date)
),
daily_returns AS (
    SELECT 
        DATE(return_date) AS summary_date,
        COALESCE(SUM(refund_amount), 0.00) AS total_refunds_issued
    FROM returns
    GROUP BY DATE(return_date)
)
SELECT 
    d.summary_date,
    d.total_orders,
    d.active_purchasers,
    d.gross_sales,
    d.total_discounts,
    d.net_revenue,
    d.average_order_value,
    COALESCE(r.total_refunds_issued, 0.00) AS total_refunds_issued
FROM daily_orders d
LEFT JOIN daily_returns r ON d.summary_date = r.summary_date;
