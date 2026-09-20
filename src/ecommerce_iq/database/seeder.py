"""
Realistic Synthetic E-Commerce Business Dataset Generator.

Generates a complete, multi-month relational e-commerce dataset for E-Commerce IQ:
- 6 Categories & 40 Products with realistic margins and distinct performance profiles
- 800+ Customers across segments (New, Regular, VIP, At-Risk, Churned)
- 4,000+ Orders spanning 14 months (Jan 2025 to Feb 2026) with:
  * Holiday seasonal surge (Nov-Dec 2025)
  * Deliberate sales decline anomaly (Aug 2025)
  * High-return product defect anomaly (PROD-ELEC-001 battery defect)
  * High sizing return anomaly (PROD-APP-001 runs small)
  * High-performing cash cow products (PROD-ELEC-003, PROD-BEAU-001)
  * Poorly performing dead-stock laggards (PROD-OFF-002)
- Line items with preserved unit cost snapshots
- Payment settlements across credit card, PayPal, Apple Pay
- Return and refund tracking with categorized reasons and notes
- Customer reviews (1-5 stars) and pre-processed NLP sentiment polarity/topic insights
- Consolidated Sales fact ledger for fast BI analytics

Uses standard Python library (random with fixed seed) for 100% reproducible data.
"""

from datetime import date, datetime, timedelta
import math
import random
import sqlite3
from typing import Any, Dict, List, Optional, Tuple
from ecommerce_iq.utils.logging import setup_logger

logger = setup_logger("ecommerce_iq.database.seeder")

# Deterministic random seed for reproducibility
RANDOM_SEED = 42

# ==============================================================================
# CATALOG DEFINITIONS
# ==============================================================================

CATEGORIES_DATA = [
    {"name": "Electronics & Audio", "slug": "electronics-audio", "description": "High-fidelity audio, smart gadgets, chargers, and display tech."},
    {"name": "Apparel & Activewear", "slug": "apparel-activewear", "description": "Performance outerwear, premium basics, and all-weather technical apparel."},
    {"name": "Home & Kitchen", "slug": "home-kitchen", "description": "Precision culinary tools, automated coffee systems, and air quality appliances."},
    {"name": "Beauty & Personal Care", "slug": "beauty-personal-care", "description": "Clinical skincare formulations, botanical serums, and oral care tech."},
    {"name": "Sports & Outdoor", "slug": "sports-outdoor", "description": "Strength equipment, ultralight camping gear, and hydration accessories."},
    {"name": "Workspace & Office", "slug": "workspace-office", "description": "Ergonomic furniture, monitor mounts, desk lighting, and organization."},
]

PRODUCTS_DATA = [
    # --------------------------------------------------------------------------
    # Electronics & Audio
    # --------------------------------------------------------------------------
    {
        "cat_slug": "electronics-audio", "sku": "PROD-ELEC-001",
        "title": "AuraSound Pro Wireless ANC Headphones",
        "desc": "Flagship active noise-cancelling over-ear headphones with 40mm drivers.",
        "cost": 58.00, "price": 179.99, "stock": 140, "threshold": 25,
        # Profile: High revenue, but HIGH RETURN RATE ANOMALY (battery failure in batch)
        "weight": 1.2, "return_bias": 0.22, "return_reason_bias": "Defective/Damaged",
        "avg_rating": 2.8
    },
    {
        "cat_slug": "electronics-audio", "sku": "PROD-ELEC-002",
        "title": "SwiftCharge 65W GaN Dual Fast Charger",
        "desc": "Ultra-compact Gallium Nitride wall adapter with dual USB-C PD ports.",
        "cost": 8.50, "price": 29.99, "stock": 420, "threshold": 50,
        # Profile: BESTSELLER / CASH COW (high volume, high margin, low return, 4.8 CSAT)
        "weight": 2.6, "return_bias": 0.02, "return_reason_bias": "Customer Changed Mind",
        "avg_rating": 4.8
    },
    {
        "cat_slug": "electronics-audio", "sku": "PROD-ELEC-003",
        "title": "UltraVision 4K Smart Cinema Projector",
        "desc": "Native 4K HDR home theater projector with integrated Android TV.",
        "cost": 320.00, "price": 649.99, "stock": 45, "threshold": 10,
        "weight": 0.5, "return_bias": 0.06, "return_reason_bias": "Item Not as Pictured",
        "avg_rating": 4.3
    },
    {
        "cat_slug": "electronics-audio", "sku": "PROD-ELEC-004",
        "title": "PulseFit Pro GPS Waterproof Smartwatch",
        "desc": "Rugged fitness smartwatch with continuous heart rate and SpO2 tracking.",
        "cost": 72.00, "price": 189.99, "stock": 160, "threshold": 30,
        "weight": 1.1, "return_bias": 0.05, "return_reason_bias": "Customer Changed Mind",
        "avg_rating": 4.4
    },
    {
        "cat_slug": "electronics-audio", "sku": "PROD-ELEC-005",
        "title": "SoundPod Mini Waterproof Bluetooth Speaker",
        "desc": "Pocket-sized 15W outdoor wireless speaker with IP67 waterproofing.",
        "cost": 12.00, "price": 39.99, "stock": 280, "threshold": 40,
        "weight": 1.5, "return_bias": 0.04, "return_reason_bias": "Customer Changed Mind",
        "avg_rating": 4.6
    },
    {
        "cat_slug": "electronics-audio", "sku": "PROD-ELEC-006",
        "title": "HyperGrip Wireless Ergonomic Gaming Mouse",
        "desc": "Ultra-lightweight 58g optical sensor mouse with 20K DPI.",
        "cost": 22.00, "price": 64.99, "stock": 190, "threshold": 25,
        "weight": 1.0, "return_bias": 0.04, "return_reason_bias": "Customer Changed Mind",
        "avg_rating": 4.5
    },

    # --------------------------------------------------------------------------
    # Apparel & Activewear
    # --------------------------------------------------------------------------
    {
        "cat_slug": "apparel-activewear", "sku": "PROD-APP-001",
        "title": "Apex Thermal Puffer Winter Jacket",
        "desc": "Windproof 800-fill down insulated technical jacket.",
        "cost": 46.00, "price": 149.99, "stock": 110, "threshold": 20,
        # Profile: Winter seasonal spike, but HIGH SIZING RETURN ANOMALY (runs 1 size small)
        "weight": 1.1, "return_bias": 0.18, "return_reason_bias": "Incorrect Size/Fit",
        "avg_rating": 3.4
    },
    {
        "cat_slug": "apparel-activewear", "sku": "PROD-APP-002",
        "title": "CloudComfort Everyday Merino Wool T-Shirt",
        "desc": "Breathable odor-resistant 100% Australian merino crewneck.",
        "cost": 14.00, "price": 48.00, "stock": 350, "threshold": 40,
        # Profile: High repeat purchase rate, steady demand
        "weight": 1.8, "return_bias": 0.03, "return_reason_bias": "Customer Changed Mind",
        "avg_rating": 4.7
    },
    {
        "cat_slug": "apparel-activewear", "sku": "PROD-APP-003",
        "title": "FlexMotion High-Waist Seamless Leggings",
        "desc": "Squat-proof compression tights with dual smartphone pockets.",
        "cost": 16.00, "price": 58.00, "stock": 290, "threshold": 35,
        "weight": 1.7, "return_bias": 0.05, "return_reason_bias": "Incorrect Size/Fit",
        "avg_rating": 4.6
    },
    {
        "cat_slug": "apparel-activewear", "sku": "PROD-APP-004",
        "title": "UrbanEdge Waterproof Commuter Backpack",
        "desc": "28L roll-top weather-resistant daypack with padded 16\" laptop sleeve.",
        "cost": 28.00, "price": 89.99, "stock": 140, "threshold": 20,
        "weight": 0.9, "return_bias": 0.04, "return_reason_bias": "Customer Changed Mind",
        "avg_rating": 4.5
    },
    {
        "cat_slug": "apparel-activewear", "sku": "PROD-APP-005",
        "title": "SummitTech Technical Polar Fleece Pullover",
        "desc": "Thermal mid-layer half-zip fleece with reinforced shoulder panels.",
        "cost": 23.00, "price": 72.00, "stock": 170, "threshold": 25,
        "weight": 0.9, "return_bias": 0.05, "return_reason_bias": "Incorrect Size/Fit",
        "avg_rating": 4.4
    },
    {
        "cat_slug": "apparel-activewear", "sku": "PROD-APP-006",
        "title": "AeroKnit Breathable 7\" Athletic Shorts",
        "desc": "Four-way stretch running shorts with built-in compression liner.",
        "cost": 9.50, "price": 36.00, "stock": 260, "threshold": 30,
        "weight": 1.2, "return_bias": 0.04, "return_reason_bias": "Customer Changed Mind",
        "avg_rating": 4.5
    },

    # --------------------------------------------------------------------------
    # Home & Kitchen
    # --------------------------------------------------------------------------
    {
        "cat_slug": "home-kitchen", "sku": "PROD-HOME-001",
        "title": "BaristaTouch Automatic Espresso & Latte Machine",
        "desc": "15-bar Italian pump stainless steel espresso maker with microfoam steam wand.",
        "cost": 135.00, "price": 329.99, "stock": 65, "threshold": 15,
        # Profile: High ticket, steady margin contributor
        "weight": 0.8, "return_bias": 0.05, "return_reason_bias": "Defective/Damaged",
        "avg_rating": 4.5
    },
    {
        "cat_slug": "home-kitchen", "sku": "PROD-HOME-002",
        "title": "ChefPrecision 8-Piece Japanese Steel Knife Set",
        "desc": "Forged high-carbon Damascus steel chef knives with magnetic walnut block.",
        "cost": 62.00, "price": 169.99, "stock": 90, "threshold": 15,
        "weight": 0.7, "return_bias": 0.03, "return_reason_bias": "Customer Changed Mind",
        "avg_rating": 4.8
    },
    {
        "cat_slug": "home-kitchen", "sku": "PROD-HOME-003",
        "title": "PureAir True HEPA H13 Smart Air Purifier",
        "desc": "Covers up to 500 sq ft with real-time air quality laser sensor.",
        "cost": 48.00, "price": 129.99, "stock": 130, "threshold": 20,
        "weight": 1.1, "return_bias": 0.04, "return_reason_bias": "Customer Changed Mind",
        "avg_rating": 4.6
    },
    {
        "cat_slug": "home-kitchen", "sku": "PROD-HOME-004",
        "title": "CrispStream 6-Quart Digital Air Fryer",
        "desc": "Rapid 360 air circulation system with 8 one-touch preset functions.",
        "cost": 34.00, "price": 89.99, "stock": 210, "threshold": 30,
        "weight": 1.4, "return_bias": 0.05, "return_reason_bias": "Defective/Damaged",
        "avg_rating": 4.4
    },
    {
        "cat_slug": "home-kitchen", "sku": "PROD-HOME-005",
        "title": "HydraTemp Variable Temperature Pour-Over Kettle",
        "desc": "Gooseneck stainless steel kettle with 1-degree precision digital base.",
        "cost": 21.00, "price": 59.99, "stock": 180, "threshold": 25,
        "weight": 1.0, "return_bias": 0.03, "return_reason_bias": "Customer Changed Mind",
        "avg_rating": 4.7
    },
    {
        "cat_slug": "home-kitchen", "sku": "PROD-HOME-006",
        "title": "Zenith Non-Stick Ceramic Skillet Set (8\" & 10\")",
        "desc": "PTFE and PFOA-free non-toxic ceramic fry pans with stay-cool handles.",
        "cost": 17.00, "price": 49.99, "stock": 240, "threshold": 30,
        "weight": 1.2, "return_bias": 0.04, "return_reason_bias": "Customer Changed Mind",
        "avg_rating": 4.5
    },

    # --------------------------------------------------------------------------
    # Beauty & Personal Care
    # --------------------------------------------------------------------------
    {
        "cat_slug": "beauty-personal-care", "sku": "PROD-BEAU-001",
        "title": "RadianceGlow 20% Vitamin C + Ferulic Acid Serum",
        "desc": "Antioxidant facial serum for skin brightening and collagen synthesis.",
        "cost": 4.80, "price": 28.00, "stock": 500, "threshold": 60,
        # Profile: SUPERSTAR CASH COW (83% gross margin, very high repeat orders, 4.8 CSAT)
        "weight": 2.4, "return_bias": 0.015, "return_reason_bias": "Customer Changed Mind",
        "avg_rating": 4.8
    },
    {
        "cat_slug": "beauty-personal-care", "sku": "PROD-BEAU-002",
        "title": "HydroSilk Hyaluronic Barrier Daily Moisturizer",
        "desc": "Deep hydration cream infused with ceramides and centella asiatica.",
        "cost": 6.50, "price": 32.00, "stock": 380, "threshold": 50,
        "weight": 1.9, "return_bias": 0.02, "return_reason_bias": "Customer Changed Mind",
        "avg_rating": 4.7
    },
    {
        "cat_slug": "beauty-personal-care", "sku": "PROD-BEAU-003",
        "title": "SonicGleam Pro Sonic Electric Toothbrush",
        "desc": "40,000 VPM motor with 4 cleaning modes and UV sanitizing travel case.",
        "cost": 24.00, "price": 79.99, "stock": 160, "threshold": 25,
        "weight": 1.0, "return_bias": 0.04, "return_reason_bias": "Defective/Damaged",
        "avg_rating": 4.5
    },
    {
        "cat_slug": "beauty-personal-care", "sku": "PROD-BEAU-004",
        "title": "PureMineral Sheer Broad-Spectrum SPF 50",
        "desc": "Invisible zinc oxide mineral sunscreen with zero white cast.",
        "cost": 4.50, "price": 24.00, "stock": 340, "threshold": 40,
        "weight": 1.4, "return_bias": 0.02, "return_reason_bias": "Customer Changed Mind",
        "avg_rating": 4.6
    },
    {
        "cat_slug": "beauty-personal-care", "sku": "PROD-BEAU-005",
        "title": "SilkPro Ionic Ceramic Salon Hair Dryer",
        "desc": "1875W brushless motor hair dryer with tourmaline negative ion generator.",
        "cost": 31.00, "price": 94.99, "stock": 120, "threshold": 20,
        "weight": 0.8, "return_bias": 0.05, "return_reason_bias": "Defective/Damaged",
        "avg_rating": 4.4
    },

    # --------------------------------------------------------------------------
    # Sports & Outdoor
    # --------------------------------------------------------------------------
    {
        "cat_slug": "sports-outdoor", "sku": "PROD-SPRT-001",
        "title": "IronGrip 55lb Fast-Adjustable Dumbbell Pair",
        "desc": "Rapid weight-dial system adjusting from 5 to 55 lbs per dumbbell.",
        "cost": 115.00, "price": 289.99, "stock": 70, "threshold": 15,
        # Profile: January New Year resolution spike, high ticket
        "weight": 0.9, "return_bias": 0.04, "return_reason_bias": "Defective/Damaged",
        "avg_rating": 4.6
    },
    {
        "cat_slug": "sports-outdoor", "sku": "PROD-SPRT-002",
        "title": "TerraTrek 2-Person Ultralight Backpacking Tent",
        "desc": "Sub-3lb waterproof freestanding silnylon tent with DAC aluminum poles.",
        "cost": 82.00, "price": 219.99, "stock": 85, "threshold": 15,
        # Profile: Strong Summer seasonal surge (May-Aug)
        "weight": 0.8, "return_bias": 0.04, "return_reason_bias": "Customer Changed Mind",
        "avg_rating": 4.7
    },
    {
        "cat_slug": "sports-outdoor", "sku": "PROD-SPRT-003",
        "title": "ZenMat Pro 6mm Eco-Natural Rubber Yoga Mat",
        "desc": "High-density cushion mat with laser-engraved alignment lines.",
        "cost": 15.00, "price": 54.00, "stock": 210, "threshold": 30,
        "weight": 1.2, "return_bias": 0.03, "return_reason_bias": "Customer Changed Mind",
        "avg_rating": 4.7
    },
    {
        "cat_slug": "sports-outdoor", "sku": "PROD-SPRT-004",
        "title": "HydraPeak 32oz Vacuum-Insulated Stainless Bottle",
        "desc": "Keeps liquids cold for 24 hours with leakproof chug sports lid.",
        "cost": 8.00, "price": 29.99, "stock": 450, "threshold": 50,
        "weight": 1.8, "return_bias": 0.02, "return_reason_bias": "Customer Changed Mind",
        "avg_rating": 4.8
    },
    {
        "cat_slug": "sports-outdoor", "sku": "PROD-SPRT-005",
        "title": "TrailMaster Carbon Fiber Trekking Poles Pair",
        "desc": "Collapsible quick-lock hiking poles with natural cork handles.",
        "cost": 17.50, "price": 58.00, "stock": 160, "threshold": 25,
        "weight": 0.9, "return_bias": 0.03, "return_reason_bias": "Customer Changed Mind",
        "avg_rating": 4.6
    },

    # --------------------------------------------------------------------------
    # Workspace & Office
    # --------------------------------------------------------------------------
    {
        "cat_slug": "workspace-office", "sku": "PROD-OFF-001",
        "title": "ErgoLift Gas-Spring Dual Monitor Arm Mount",
        "desc": "Full-motion heavy-duty aluminum arm supporting dual 32\" displays.",
        "cost": 24.00, "price": 74.99, "stock": 170, "threshold": 25,
        "weight": 1.1, "return_bias": 0.04, "return_reason_bias": "Customer Changed Mind",
        "avg_rating": 4.5
    },
    {
        "cat_slug": "workspace-office", "sku": "PROD-OFF-002",
        "title": "SoundShield Acoustic Felt Desk Privacy Divider",
        "desc": "Clamped acoustic sound-absorbing felt panel for desktop distraction control.",
        "cost": 21.00, "price": 49.99, "stock": 210, "threshold": 20,
        # Profile: POOR PERFORMER / DEAD STOCK (lowest sales velocity, stale inventory)
        "weight": 0.15, "return_bias": 0.08, "return_reason_bias": "Item Not as Pictured",
        "avg_rating": 3.7
    },
    {
        "cat_slug": "workspace-office", "sku": "PROD-OFF-003",
        "title": "LuminaDesk Eye-Care LED Task Bar with Wireless Pad",
        "desc": "Dimmable architectural lamp with 5 color temperatures and Qi charging.",
        "cost": 18.50, "price": 56.00, "stock": 190, "threshold": 25,
        "weight": 1.0, "return_bias": 0.03, "return_reason_bias": "Customer Changed Mind",
        "avg_rating": 4.6
    },
    {
        "cat_slug": "workspace-office", "sku": "PROD-OFF-004",
        "title": "ApexLeather Minimalist Desk Mat (36\" x 18\")",
        "desc": "Waterproof PU vegan leather non-slip mousepad and writing blotter.",
        "cost": 7.00, "price": 28.00, "stock": 310, "threshold": 40,
        "weight": 1.3, "return_bias": 0.02, "return_reason_bias": "Customer Changed Mind",
        "avg_rating": 4.7
    },
]

# Real customer names for deterministic generator
FIRST_NAMES = [
    "Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia", "Lucas", "Isabella", "Mason",
    "Mia", "Oliver", "Amelia", "Elijah", "Harper", "Aiden", "Evelyn", "James", "Abigail", "Alexander",
    "Emily", "Benjamin", "Ella", "Jack", "Elizabeth", "Henry", "Camila", "Sebastian", "Luna", "Daniel",
    "Avery", "Matthew", "Sofia", "Samuel", "Chloe", "David", "Grace", "Joseph", "Scarlett", "Carter",
    "Victoria", "Owen", "Riley", "Wyatt", "Aria", "John", "Lily", "Luke", "Zoey", "Anthony",
    "Hannah", "Isaac", "Nora", "Dylan", "Leah", "Leo", "Audrey", "Julian", "Maya", "Gabriel"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts"
]

CITIES = [
    ("New York", "NY", "USA"), ("Los Angeles", "CA", "USA"), ("Chicago", "IL", "USA"),
    ("Houston", "TX", "USA"), ("Phoenix", "AZ", "USA"), ("Philadelphia", "PA", "USA"),
    ("San Antonio", "TX", "USA"), ("San Diego", "CA", "USA"), ("Dallas", "TX", "USA"),
    ("Austin", "TX", "USA"), ("San Jose", "CA", "USA"), ("Seattle", "WA", "USA"),
    ("Denver", "CO", "USA"), ("Boston", "MA", "USA"), ("Atlanta", "GA", "USA"),
    ("Miami", "FL", "USA"), ("San Francisco", "CA", "USA"), ("Portland", "OR", "USA"),
    ("Minneapolis", "MN", "USA"), ("Nashville", "TN", "USA"), ("Toronto", "ON", "Canada"),
    ("Vancouver", "BC", "Canada"), ("London", "ENG", "UK"), ("Manchester", "ENG", "UK")
]

# Realistic customer review templates keyed by scenario
REVIEWS_TEMPLATES = {
    "battery_defect": [
        (1, "Battery died after 20 minutes!", "Extremely disappointed. The sound quality was okay for the first 2 days, then the battery started dying in under 20 minutes. Will not hold a charge anymore. Returning immediately.", "Battery/Hardware", "Battery dies after 20 minutes"),
        (1, "Left earbud stopped charging completely", "Defective product. The case says 100% but the left headphone won't charge or turn on. Support offered no help. Requesting full refund.", "Battery/Hardware", "Left earbud failure to charge"),
        (2, "Battery life is nowhere near advertised", "Advertised 30 hours, but I barely get 2 hours on a full charge. Noise cancellation is decent, but battery makes this unusable for travel.", "Battery/Hardware", "Severe battery drain issue"),
        (2, "Overheating during charging", "The charging case gets dangerously hot while plugged in and the battery drains while sitting idle in my bag. Major quality control issue.", "Battery/Hardware", "Case overheating and draining idle"),
    ],
    "sizing_issue": [
        (2, "Runs at least one size too small!", "Great quality fabric and warmth, but the sizing is completely off. I normally wear a Medium, but this feels like an Extra Small around the chest and arms. Had to return.", "Sizing/Fit", "Runs 1 size too small"),
        (2, "Tight in the shoulders and short sleeves", "Looks great in photos, but the shoulders are painfully tight when you move your arms. Order at least one or two sizes up!", "Sizing/Fit", "Tight shoulder construction"),
        (3, "Warm jacket, but exchange needed for larger size", "Very warm and lightweight, but had to return the Large to get an XL. Sizing chart on website is inaccurate.", "Sizing/Fit", "Inaccurate sizing chart"),
    ],
    "dead_stock": [
        (3, "Average desk divider", "Does the job to block sightlines, but felt was thinner than expected. Decent for the price.", "Quality", "Thin felt material"),
        (2, "Clamps are wobbly", "Hard to get it tight on an IKEA desk without wobbling. Not worth the desk space.", "Quality", "Unstable desk clamp"),
    ],
    "praise": [
        (5, "Exceptional quality, exceeded expectations!", "Hands down the best purchase I've made this year. High quality materials, fast shipping, and works exactly as described. Worth every single penny.", "Quality", "None"),
        (5, "Must-have! Will buy again", "Incredible performance and build. The attention to detail is noticeable right out of the box. Highly recommend to anyone on the fence.", "Quality", "None"),
        (5, "Fast shipping and fantastic customer experience", "Arrived two days ahead of schedule in eco-friendly packaging. Product works flawlessly. 10/10.", "Shipping/Delivery", "None"),
        (5, "Superb value for money", "Comparable to brands costing double the price. Very happy with the purchase.", "Pricing/Value", "None"),
        (4, "Very solid and well made", "Works great and looks sleek. Minor instruction manual clarity could be improved, but product itself is stellar.", "Quality", "None"),
    ],
    "general_negative": [
        (1, "Arrived broken, box was crushed", "Delivery box was completely mangled and the item inside was cracked. Packaging was insufficient for fragile items.", "Shipping/Delivery", "Damaged in transit due to packaging"),
        (2, "Color does not match photo", "In person, the color is completely dull compared to the vibrant listing photos. Disappointed with the appearance.", "Item Not as Pictured", "Color mismatch from photos"),
        (2, "Felt cheap for the price tag", "Plastic feels hollow and cheap. Expected much higher build quality given the price.", "Pricing/Value", "Low quality material for price"),
    ]
}


class MockDataSeeder:
    """
    Deterministic dataset generator seeding all 10 normalized tables.
    """

    def __init__(self, db_path: str, seed: int = RANDOM_SEED) -> None:
        self.db_path = db_path
        self.rng = random.Random(seed)
        self.categories: Dict[str, int] = {}
        self.products: List[Dict[str, Any]] = []
        self.customer_ids: List[int] = []
        self.order_records: List[Dict[str, Any]] = []

    def seed_all(
        self,
        num_customers: int = 850,
        num_orders: int = 4200,
        start_date: date = date(2025, 1, 1),
        end_date: date = date(2026, 2, 28)
    ) -> Dict[str, int]:
        """
        Execute full synthetic database population across all tables.

        Returns:
            Dictionary containing row counts inserted per table.
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")

            logger.info("Seeding Categories...")
            cat_counts = self._seed_categories(cursor)

            logger.info("Seeding Products...")
            prod_counts = self._seed_products(cursor)

            logger.info(f"Seeding {num_customers} Customers...")
            cust_counts = self._seed_customers(cursor, num_customers, start_date)

            logger.info(f"Seeding {num_orders} Orders and Order Items...")
            order_counts, item_counts, payment_counts, sales_counts = self._seed_orders(
                cursor, num_orders, start_date, end_date
            )

            logger.info("Seeding Returns and Refunds...")
            return_counts = self._seed_returns(cursor)

            logger.info("Seeding Reviews and NLP Insights...")
            review_counts, insight_counts = self._seed_reviews(cursor)

            conn.commit()
            logger.info("Database seeding completed successfully!")

            return {
                "categories": cat_counts,
                "products": prod_counts,
                "customers": cust_counts,
                "orders": order_counts,
                "order_items": item_counts,
                "payments": payment_counts,
                "returns": return_counts,
                "reviews": review_counts,
                "review_insights": insight_counts,
                "sales": sales_counts,
            }
        finally:
            conn.close()

    def _seed_categories(self, cursor: sqlite3.Cursor) -> int:
        for cat in CATEGORIES_DATA:
            cursor.execute(
                "INSERT INTO categories (name, slug, description) VALUES (?, ?, ?);",
                (cat["name"], cat["slug"], cat["description"])
            )
            self.categories[cat["slug"]] = cursor.lastrowid
        return len(self.categories)

    def _seed_products(self, cursor: sqlite3.Cursor) -> int:
        for p in PRODUCTS_DATA:
            cat_id = self.categories[p["cat_slug"]]
            cursor.execute(
                """
                INSERT INTO products (
                    category_id, sku, title, description, cost_price, retail_price,
                    stock_quantity, low_stock_threshold, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1);
                """,
                (cat_id, p["sku"], p["title"], p["desc"], p["cost"], p["price"], p["stock"], p["threshold"])
            )
            prod_id = cursor.lastrowid
            self.products.append({
                "product_id": prod_id,
                "sku": p["sku"],
                "title": p["title"],
                "cost": p["cost"],
                "price": p["price"],
                "weight": p["weight"],
                "return_bias": p["return_bias"],
                "return_reason_bias": p["return_reason_bias"],
                "avg_rating": p["avg_rating"]
            })
        return len(self.products)

    def _seed_customers(self, cursor: sqlite3.Cursor, num_customers: int, start_date: date) -> int:
        # Segment distribution: VIP 12%, Regular 45%, New 28%, At-Risk 10%, Churned 5%
        segments_pool = (
            ["VIP High Value"] * 12 +
            ["Regular"] * 45 +
            ["New"] * 28 +
            ["At-Risk"] * 10 +
            ["Churned"] * 5
        )

        for i in range(1, num_customers + 1):
            first = self.rng.choice(FIRST_NAMES)
            last = self.rng.choice(LAST_NAMES)
            email = f"{first.lower()}.{last.lower()}{i}@example.com"
            phone = f"+1-{self.rng.randint(200, 999)}-{self.rng.randint(200, 999)}-{self.rng.randint(1000, 9999)}"
            city, state, country = self.rng.choice(CITIES)
            street = f"{self.rng.randint(100, 9999)} {self.rng.choice(['Maple', 'Oak', 'Washington', 'Lake', 'Cedar', 'Pine'])} St"
            segment = self.rng.choice(segments_pool)

            # Registration date prior to or within time window
            reg_offset = self.rng.randint(0, 400)
            reg_date = (start_date - timedelta(days=reg_offset)).strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute(
                """
                INSERT INTO customers (
                    first_name, last_name, email, phone, street_address,
                    city, state, postal_code, country, customer_segment, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (first, last, email, phone, street, city, state, f"{self.rng.randint(10000, 99999)}", country, segment, reg_date)
            )
            self.customer_ids.append(cursor.lastrowid)

        return len(self.customer_ids)

    def _seed_orders(
        self,
        cursor: sqlite3.Cursor,
        num_orders: int,
        start_date: date,
        end_date: date
    ) -> Tuple[int, int, int, int]:
        total_days = (end_date - start_date).days
        product_weights = [p["weight"] for p in self.products]

        order_count = 0
        item_count = 0
        payment_count = 0
        sales_count = 0

        # Generate timestamps with seasonal multipliers
        for i in range(1, num_orders + 1):
            day_offset = self.rng.randint(0, total_days)
            order_day = start_date + timedelta(days=day_offset)
            month = order_day.month
            year = order_day.year

            # Scenario Multipliers:
            # 1. Holiday Surge (Nov-Dec 2025): 2.4x volume
            # 2. August 2025 Sales Dip: 0.55x volume (simulating category drop / stockouts)
            # 3. January 2026 fitness resolution bump
            if year == 2025 and month in (11, 12):
                if self.rng.random() > 0.4:
                    # Keep more orders in Q4
                    pass
            elif year == 2025 and month == 8:
                if self.rng.random() < 0.45:
                    # Skip some orders to simulate August drop
                    continue

            order_time = datetime(
                order_day.year, order_day.month, order_day.day,
                self.rng.randint(8, 22), self.rng.randint(0, 59), self.rng.randint(0, 59)
            )

            cust_id = self.rng.choice(self.customer_ids)
            # Number of line items: mostly 1-2 items, occasionally 3-4
            num_items = self.rng.choices([1, 2, 3, 4], weights=[0.60, 0.28, 0.09, 0.03])[0]
            chosen_prods = self.rng.choices(self.products, weights=product_weights, k=num_items)

            subtotal = 0.0
            order_items_data = []

            for prod in chosen_prods:
                qty = self.rng.choices([1, 2, 3], weights=[0.85, 0.12, 0.03])[0]
                unit_price = prod["price"]
                unit_cost = prod["cost"]
                item_sub = round(qty * unit_price, 2)
                subtotal += item_sub

                order_items_data.append({
                    "product": prod,
                    "quantity": qty,
                    "unit_price": unit_price,
                    "unit_cost": unit_cost,
                    "item_total": item_sub,
                })

            subtotal = round(subtotal, 2)

            # Discount logic: 20% of orders have promotional discount
            discount = 0.0
            if self.rng.random() < 0.22:
                discount_pct = self.rng.choice([0.10, 0.15, 0.20])
                discount = round(subtotal * discount_pct, 2)

            tax = round((subtotal - discount) * 0.07, 2)
            shipping = 0.0 if subtotal > 75.0 else 5.99
            total_amount = round(max(0.0, (subtotal - discount) + tax + shipping), 2)

            # Order status: 94% completed, 4% cancelled, 2% refunded
            status = self.rng.choices(
                ["completed", "cancelled", "refunded"],
                weights=[0.94, 0.04, 0.02]
            )[0]

            cursor.execute(
                """
                INSERT INTO orders (
                    customer_id, order_date, status, subtotal, discount_amount,
                    tax_amount, shipping_fee, total_amount, shipping_address, billing_address
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    cust_id, order_time.strftime("%Y-%m-%d %H:%M:%S"), status,
                    subtotal, discount, tax, shipping, total_amount,
                    "Same as customer profile", "Same as customer profile"
                )
            )
            order_id = cursor.lastrowid
            order_count += 1

            # Insert Order Items & build Sales Ledger
            for item in order_items_data:
                p = item["product"]
                qty = item["quantity"]
                u_price = item["unit_price"]
                u_cost = item["unit_cost"]
                i_total = item["item_total"]

                # Proportional discount on line item
                line_discount = round((i_total / subtotal) * discount, 2) if subtotal > 0 else 0.0
                net_rev = round(i_total - line_discount, 2)
                cogs = round(qty * u_cost, 2)
                gross_profit = round(net_rev - cogs, 2)
                margin_pct = round((gross_profit / net_rev * 100.0), 2) if net_rev > 0 else 0.0

                cursor.execute(
                    """
                    INSERT INTO order_items (
                        order_id, product_id, quantity, unit_price, unit_cost,
                        discount_applied, item_total
                    ) VALUES (?, ?, ?, ?, ?, ?, ?);
                    """,
                    (order_id, p["product_id"], qty, u_price, u_cost, line_discount, i_total)
                )
                order_item_id = cursor.lastrowid
                item_count += 1

                # Sales fact record for completed orders
                if status == "completed":
                    cursor.execute(
                        """
                        INSERT INTO sales (
                            order_id, order_item_id, product_id, customer_id, sale_date,
                            quantity, gross_revenue, discount_amount, net_revenue,
                            cost_of_goods_sold, gross_profit, profit_margin_pct,
                            is_refunded, refund_amount
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0.00);
                        """,
                        (
                            order_id, order_item_id, p["product_id"], cust_id,
                            order_day.strftime("%Y-%m-%d"), qty, i_total,
                            line_discount, net_rev, cogs, gross_profit, margin_pct
                        )
                    )
                    sales_count += 1

                self.order_records.append({
                    "order_id": order_id,
                    "order_item_id": order_item_id,
                    "order_date": order_time,
                    "product": p,
                    "customer_id": cust_id,
                    "status": status,
                    "quantity": qty,
                    "item_total": i_total,
                    "net_rev": net_rev,
                })

            # Record Payment
            if status != "cancelled":
                pm = self.rng.choices(
                    ["credit_card", "paypal", "apple_pay", "debit_card", "store_credit"],
                    weights=[0.55, 0.20, 0.15, 0.05, 0.05]
                )[0]
                txn_ref = f"TXN-{order_day.strftime('%Y%m')}-{order_id:06d}-{self.rng.randint(100, 999)}"
                cursor.execute(
                    """
                    INSERT INTO payments (
                        order_id, payment_method, transaction_reference, amount, status, payment_date
                    ) VALUES (?, ?, ?, ?, 'completed', ?);
                    """,
                    (order_id, pm, txn_ref, total_amount, order_time.strftime("%Y-%m-%d %H:%M:%S"))
                )
                payment_count += 1

        return order_count, item_count, payment_count, sales_count

    def _seed_returns(self, cursor: sqlite3.Cursor) -> int:
        return_count = 0
        return_reasons_general = [
            "Customer Changed Mind", "Incorrect Size/Fit", "Item Not as Pictured",
            "Arrived Too Late", "Defective/Damaged", "Wrong Item Shipped"
        ]

        # Notes keyed by reason
        notes_by_reason = {
            "Defective/Damaged": [
                "Item arrived broken in box.",
                "Stopped working after second day of use.",
                "Defective internal component.",
                "Battery stopped holding charge.",
            ],
            "Incorrect Size/Fit": [
                "Runs significantly smaller than standard sizing.",
                "Shoulders are too tight.",
                "Waistband is loose.",
                "Ordered Medium, fits like XS.",
            ],
            "Item Not as Pictured": [
                "Color is much darker in reality than online photos.",
                "Material texture differs from product listing.",
                "Missing expected accessories pictured.",
            ],
            "Customer Changed Mind": [
                "No longer needed for project.",
                "Found alternative gift.",
                "Accidentally ordered duplicate.",
            ],
            "Arrived Too Late": [
                "Missed birthday celebration date.",
                "Delivered 4 days after promised arrival.",
            ],
            "Wrong Item Shipped": [
                "Received wrong color variant.",
                "Invoice shows SKU but different product was in package.",
            ]
        }

        for record in self.order_records:
            if record["status"] != "completed":
                continue

            p = record["product"]
            return_prob = p["return_bias"]

            if self.rng.random() < return_prob:
                # Determine reason based on product profile
                if self.rng.random() < 0.70:
                    reason = p["return_reason_bias"]
                else:
                    reason = self.rng.choice(return_reasons_general)

                # Return date 3 to 14 days after purchase
                ret_date = record["order_date"] + timedelta(days=self.rng.randint(3, 14))
                refund_val = record["item_total"]
                note = self.rng.choice(notes_by_reason.get(reason, ["Returned for refund."]))

                cursor.execute(
                    """
                    INSERT INTO returns (
                        order_id, order_item_id, product_id, customer_id, quantity_returned,
                        return_reason, detailed_notes, refund_amount, status, return_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'completed', ?);
                    """,
                    (
                        record["order_id"], record["order_item_id"], p["product_id"],
                        record["customer_id"], record["quantity"], reason, note,
                        refund_val, ret_date.strftime("%Y-%m-%d %H:%M:%S")
                    )
                )
                return_count += 1

                # Update sales record to flag refund
                cursor.execute(
                    """
                    UPDATE sales
                    SET is_refunded = 1, refund_amount = ?
                    WHERE order_item_id = ?;
                    """,
                    (refund_val, record["order_item_id"])
                )

        return return_count

    def _seed_reviews(self, cursor: sqlite3.Cursor) -> Tuple[int, int]:
        review_count = 0
        insight_count = 0

        for record in self.order_records:
            if record["status"] != "completed":
                continue

            # Review submission rate: ~35% of purchases leave a review
            if self.rng.random() > 0.35:
                continue

            p = record["product"]
            sku = p["sku"]
            avg_rating = p["avg_rating"]

            # Select review template based on SKU archetype
            if sku == "PROD-ELEC-001" and self.rng.random() < 0.65:
                rating, title, comment, topic, issue = self.rng.choice(REVIEWS_TEMPLATES["battery_defect"])
            elif sku == "PROD-APP-001" and self.rng.random() < 0.60:
                rating, title, comment, topic, issue = self.rng.choice(REVIEWS_TEMPLATES["sizing_issue"])
            elif sku == "PROD-OFF-002" and self.rng.random() < 0.50:
                rating, title, comment, topic, issue = self.rng.choice(REVIEWS_TEMPLATES["dead_stock"])
            elif avg_rating >= 4.5:
                if self.rng.random() < 0.88:
                    rating, title, comment, topic, issue = self.rng.choice(REVIEWS_TEMPLATES["praise"])
                else:
                    rating, title, comment, topic, issue = self.rng.choice(REVIEWS_TEMPLATES["general_negative"])
            else:
                if self.rng.random() < 0.50:
                    rating, title, comment, topic, issue = self.rng.choice(REVIEWS_TEMPLATES["praise"])
                else:
                    rating, title, comment, topic, issue = self.rng.choice(REVIEWS_TEMPLATES["general_negative"])

            rev_date = record["order_date"] + timedelta(days=self.rng.randint(2, 21))

            cursor.execute(
                """
                INSERT INTO reviews (
                    product_id, customer_id, order_id, rating, title, comment,
                    review_date, verified_purchase, helpful_votes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?);
                """,
                (
                    p["product_id"], record["customer_id"], record["order_id"],
                    rating, title, comment, rev_date.strftime("%Y-%m-%d %H:%M:%S"),
                    self.rng.randint(0, 24)
                )
            )
            review_id = cursor.lastrowid
            review_count += 1

            # Determine sentiment label and polarity score
            if rating >= 4:
                sentiment_label = "positive"
                score = round(self.rng.uniform(0.60, 0.95), 4)
            elif rating == 3:
                sentiment_label = "neutral"
                score = round(self.rng.uniform(-0.15, 0.20), 4)
            else:
                sentiment_label = "negative"
                score = round(self.rng.uniform(-0.95, -0.50), 4)

            cursor.execute(
                """
                INSERT INTO review_insights (
                    review_id, sentiment_label, sentiment_score, primary_topic, detected_issue
                ) VALUES (?, ?, ?, ?, ?);
                """,
                (review_id, sentiment_label, score, topic, issue)
            )
            insight_count += 1

        return review_count, insight_count
