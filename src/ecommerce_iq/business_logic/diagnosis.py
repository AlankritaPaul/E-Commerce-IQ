"""
Performance Anomaly and Decline Diagnosis Engine.

Investigates and explains multi-dimensional causes behind business performance shifts:
- Decomposes top-line revenue declines into order volume, units sold, and AOV shifts
- Identifies product-level drag and connects with return rates and CSAT ratings
- Corroborates quantitative drops with qualitative customer review sentiment
- Detects statistical operational anomalies across historical periods
- Enforces strict empirical evidence behind every finding without speculation
"""

from calendar import monthrange
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from ecommerce_iq.database.connection import DatabaseManager
from ecommerce_iq.models.schemas import (
    DiagnosticReport,
    MetricEvidence,
    ProductDeclineFactor,
)


class BusinessPerformanceDiagnostic:
    """
    Evaluates multi-dimensional empirical root causes behind revenue declines.
    """

    def __init__(
        self,
        db_manager: Optional[DatabaseManager] = None,
        analytics_engine: Optional[Any] = None
    ) -> None:
        self.db = db_manager or DatabaseManager()
        self.analytics = analytics_engine

    @staticmethod
    def _safe_divide(numerator: float, denominator: float) -> float:
        if not denominator or denominator == 0.0:
            return 0.0
        return numerator / denominator

    @staticmethod
    def _calc_pct_change(current: float, baseline: float) -> float:
        if baseline == 0.0:
            return 100.0 if current > 0 else 0.0
        return round(((current - baseline) / baseline) * 100.0, 2)

    def diagnose_revenue_decline(
        self,
        current_start: date,
        current_end: date,
        baseline_start: date,
        baseline_end: date
    ) -> DiagnosticReport:
        """
        Perform a comprehensive, evidence-backed diagnosis of performance shifts
        between an evaluated operational period and a baseline period.
        """
        cur_s_str = current_start.isoformat()
        cur_e_str = f"{current_end.isoformat()} 23:59:59"
        base_s_str = baseline_start.isoformat()
        base_e_str = f"{baseline_end.isoformat()} 23:59:59"

        # ----------------------------------------------------------------------
        # 1. Macro Sales & Revenue Metrics (Evidence Computation)
        # ----------------------------------------------------------------------
        def _get_period_macro_metrics(start_iso: str, end_iso: str) -> Dict[str, float]:
            # Sales & Orders
            sales_q = f"""
                SELECT 
                    COUNT(DISTINCT o.order_id) AS orders,
                    COALESCE(SUM(o.total_amount), 0.0) AS gross_revenue,
                    COALESCE(SUM(oi.quantity), 0) AS units_sold,
                    COALESCE(SUM(oi.quantity * oi.unit_cost), 0.0) AS total_cogs
                FROM orders o
                JOIN order_items oi ON o.order_id = oi.order_id
                WHERE o.status = 'completed'
                  AND o.order_date >= '{start_iso}'
                  AND o.order_date <= '{end_iso}';
            """
            s_row = self.db.execute_query(sales_q)[0]
            orders = float(s_row["orders"] or 0)
            gross_rev = float(s_row["gross_revenue"] or 0.0)
            units = float(s_row["units_sold"] or 0)
            cogs = float(s_row["total_cogs"] or 0.0)

            # Refunds & Returns
            ret_q = f"""
                SELECT 
                    COUNT(r.return_id) AS return_events,
                    COALESCE(SUM(r.quantity_returned), 0) AS units_returned,
                    COALESCE(SUM(r.refund_amount), 0.0) AS total_refunds
                FROM returns r
                WHERE r.return_date >= '{start_iso}'
                  AND r.return_date <= '{end_iso}';
            """
            r_row = self.db.execute_query(ret_q)[0]
            units_returned = float(r_row["units_returned"] or 0)
            total_refunds = float(r_row["total_refunds"] or 0.0)

            # Reviews
            rev_q = f"""
                SELECT 
                    COUNT(r.review_id) AS total_reviews,
                    COALESCE(AVG(r.rating), 0.0) AS avg_rating,
                    SUM(CASE WHEN ri.sentiment_label = 'negative' THEN 1 ELSE 0 END) AS neg_reviews
                FROM reviews r
                LEFT JOIN review_insights ri ON r.review_id = ri.review_id
                WHERE r.review_date >= '{start_iso}'
                  AND r.review_date <= '{end_iso}';
            """
            rev_row = self.db.execute_query(rev_q)[0]
            total_reviews = float(rev_row["total_reviews"] or 0)
            avg_rating = float(rev_row["avg_rating"] or 0.0)
            neg_reviews = float(rev_row["neg_reviews"] or 0)

            net_rev = max(0.0, gross_rev - total_refunds)
            aov = self._safe_divide(gross_rev, orders)
            gross_profit = net_rev - cogs
            return_rate = self._safe_divide(units_returned, units) * 100.0

            return {
                "orders": orders,
                "gross_revenue": round(gross_rev, 2),
                "net_revenue": round(net_rev, 2),
                "units_sold": units,
                "aov": round(aov, 2),
                "gross_profit": round(gross_profit, 2),
                "units_returned": units_returned,
                "total_refunds": round(total_refunds, 2),
                "return_rate_pct": round(return_rate, 2),
                "avg_rating": round(avg_rating, 2),
                "total_reviews": total_reviews,
                "neg_reviews": neg_reviews,
            }

        cur_macro = _get_period_macro_metrics(cur_s_str, cur_e_str)
        base_macro = _get_period_macro_metrics(base_s_str, base_e_str)

        # Build MetricEvidence collection
        metric_configs = [
            ("Net Revenue", "net_revenue", "$"),
            ("Total Completed Orders", "orders", "orders"),
            ("Total Units Sold", "units_sold", "units"),
            ("Average Order Value (AOV)", "aov", "$"),
            ("Gross Profit", "gross_profit", "$"),
            ("Return Rate", "return_rate_pct", "%"),
            ("Total Refunds Issued", "total_refunds", "$"),
            ("Average Customer Rating", "avg_rating", "stars"),
        ]

        metric_evidences: List[MetricEvidence] = []
        for label, key, unit in metric_configs:
            c_val = cur_macro[key]
            b_val = base_macro[key]
            abs_chg = round(c_val - b_val, 2)
            pct_chg = self._calc_pct_change(c_val, b_val)

            # Determine impact direction and significance
            if key in ("return_rate_pct", "total_refunds"):
                impact = "Negative" if abs_chg > 0 else "Positive"
            else:
                impact = "Negative" if abs_chg < 0 else "Positive"

            if key == "net_revenue" or (abs(pct_chg) >= 25.0 and key in ("orders", "units_sold")):
                significance = "Major Driver"
            elif abs(pct_chg) >= 10.0:
                significance = "Contributing Factor"
            else:
                significance = "Secondary"

            metric_evidences.append(
                MetricEvidence(
                    metric_name=label,
                    current_value=c_val,
                    baseline_value=b_val,
                    absolute_change=abs_chg,
                    percentage_change=pct_chg,
                    unit=unit,
                    impact_direction=impact,
                    significance=significance,
                )
            )

        # ----------------------------------------------------------------------
        # 2. Product-Level Decomposition (Identify Drag Products)
        # ----------------------------------------------------------------------
        prod_q = f"""
            WITH base_prod AS (
                SELECT 
                    oi.product_id,
                    p.sku,
                    p.title,
                    c.name AS category_name,
                    SUM(oi.item_total) AS base_rev,
                    SUM(oi.quantity) AS base_units
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.order_id
                JOIN products p ON oi.product_id = p.product_id
                JOIN categories c ON p.category_id = c.category_id
                WHERE o.status = 'completed'
                  AND o.order_date >= '{base_s_str}'
                  AND o.order_date <= '{base_e_str}'
                GROUP BY oi.product_id, p.sku, p.title, c.name
            ),
            cur_prod AS (
                SELECT 
                    oi.product_id,
                    SUM(oi.item_total) AS cur_rev,
                    SUM(oi.quantity) AS cur_units
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.order_id
                WHERE o.status = 'completed'
                  AND o.order_date >= '{cur_s_str}'
                  AND o.order_date <= '{cur_e_str}'
                GROUP BY oi.product_id
            ),
            cur_ret AS (
                SELECT 
                    r.product_id,
                    SUM(r.quantity_returned) AS units_ret
                FROM returns r
                WHERE r.return_date >= '{cur_s_str}'
                  AND r.return_date <= '{cur_e_str}'
                GROUP BY r.product_id
            ),
            cur_revs AS (
                SELECT 
                    r.product_id,
                    AVG(r.rating) AS avg_rat,
                    COALESCE(ri.detected_issue, ri.primary_topic) AS complaint,
                    ROW_NUMBER() OVER (PARTITION BY r.product_id ORDER BY COUNT(*) DESC) AS rn
                FROM reviews r
                LEFT JOIN review_insights ri ON r.review_id = ri.review_id
                WHERE r.review_date >= '{cur_s_str}'
                  AND r.review_date <= '{cur_e_str}'
                GROUP BY r.product_id, complaint
            )
            SELECT 
                b.product_id,
                b.sku,
                b.title,
                b.category_name,
                b.base_rev,
                b.base_units,
                COALESCE(c.cur_rev, 0.0) AS cur_rev,
                COALESCE(c.cur_units, 0) AS cur_units,
                (COALESCE(c.cur_rev, 0.0) - b.base_rev) AS rev_diff,
                COALESCE(cr.units_ret, 0) AS cur_units_ret,
                COALESCE(rev.avg_rat, 0.0) AS cur_avg_rat,
                COALESCE(rev.complaint, 'None') AS cur_complaint
            FROM base_prod b
            LEFT JOIN cur_prod c ON b.product_id = c.product_id
            LEFT JOIN cur_ret cr ON b.product_id = cr.product_id
            LEFT JOIN cur_revs rev ON b.product_id = rev.product_id AND rev.rn = 1
            ORDER BY rev_diff ASC;
        """
        prod_rows = self.db.execute_query(prod_q)
        top_declining_products: List[ProductDeclineFactor] = []

        for pr in prod_rows[:5]:
            loss = float(pr["rev_diff"])
            if loss >= 0:
                continue

            b_rev = float(pr["base_rev"])
            c_rev = float(pr["cur_rev"])
            pct = self._calc_pct_change(c_rev, b_rev)
            c_units = int(pr["cur_units"])
            b_units = int(pr["base_units"])
            unit_diff = c_units - b_units

            ret_rate = round(self._safe_divide(float(pr["cur_units_ret"]), float(c_units)) * 100.0, 1)
            rat = round(float(pr["cur_avg_rat"]), 2)

            # Driver type classification
            if ret_rate >= 15.0 or (rat > 0 and rat <= 2.8):
                driver_type = "Quality/Return Defect"
            elif unit_diff < 0:
                driver_type = "Volume Drop"
            else:
                driver_type = "Pricing/AOV Shift"

            top_declining_products.append(
                ProductDeclineFactor(
                    product_id=pr["product_id"],
                    sku=pr["sku"],
                    title=pr["title"],
                    category_name=pr["category_name"],
                    current_revenue=round(c_rev, 2),
                    baseline_revenue=round(b_rev, 2),
                    revenue_loss=round(loss, 2),
                    percentage_change=pct,
                    units_sold_change=unit_diff,
                    return_rate_pct=ret_rate,
                    average_rating=rat,
                    top_complaint_theme=pr["cur_complaint"],
                    primary_driver_type=driver_type,
                )
            )

        # ----------------------------------------------------------------------
        # 3. Customer Review Sentiment Signals
        # ----------------------------------------------------------------------
        review_signals: List[str] = []
        c_rat = cur_macro["avg_rating"]
        b_rat = base_macro["avg_rating"]
        c_neg = cur_macro["neg_reviews"]
        b_neg = base_macro["neg_reviews"]

        if c_rat < b_rat:
            review_signals.append(
                f"Customer CSAT rating dropped from {b_rat} to {c_rat} stars ({self._calc_pct_change(c_rat, b_rat):+.1f}%)."
            )
        if c_neg > 0:
            review_signals.append(
                f"Identified {int(c_neg)} negative reviews during the current period, with top recurring issues affecting high-value products."
            )

        # Add specific complaints from top declining products
        for dp in top_declining_products:
            if dp.top_complaint_theme != "None":
                review_signals.append(
                    f"{dp.sku} ({dp.title}): Corroborated by customer complaints regarding '{dp.top_complaint_theme}'."
                )

        # ----------------------------------------------------------------------
        # 4. Evidence-Based Diagnostic Synthesis
        # ----------------------------------------------------------------------
        net_rev_chg = round(cur_macro["net_revenue"] - base_macro["net_revenue"], 2)
        net_rev_pct = self._calc_pct_change(cur_macro["net_revenue"], base_macro["net_revenue"])
        order_chg = int(cur_macro["orders"] - base_macro["orders"])
        order_pct = self._calc_pct_change(cur_macro["orders"], base_macro["orders"])
        aov_chg = round(cur_macro["aov"] - base_macro["aov"], 2)
        aov_pct = self._calc_pct_change(cur_macro["aov"], base_macro["aov"])

        # Determine severity
        if net_rev_pct <= -25.0:
            severity = "Critical"
        elif net_rev_pct <= -15.0:
            severity = "High"
        elif net_rev_pct <= -5.0:
            severity = "Moderate"
        else:
            severity = "Informational"

        period_label = f"{current_start.strftime('%b %d, %Y')} to {current_end.strftime('%b %d, %Y')}"
        baseline_label = f"{baseline_start.strftime('%b %d, %Y')} to {baseline_end.strftime('%b %d, %Y')}"

        # Construct primary finding narrative with exact empirical numbers
        if net_rev_chg < 0:
            primary_finding = (
                f"Net revenue contracted by ${abs(net_rev_chg):,.2f} ({net_rev_pct:+.2f}%) from "
                f"${base_macro['net_revenue']:,.2f} to ${cur_macro['net_revenue']:,.2f}. "
                f"The primary quantitative catalyst was a {order_pct:+.2f}% drop in completed order volume "
                f"({int(cur_macro['orders'])} vs. {int(base_macro['orders'])} orders), "
                f"reinforced by a {aov_pct:+.2f}% change in Average Order Value (${cur_macro['aov']:,.2f} vs. ${base_macro['aov']:,.2f})."
            )
        else:
            primary_finding = (
                f"Net revenue increased by ${net_rev_chg:,.2f} ({net_rev_pct:+.2f}%) from "
                f"${base_macro['net_revenue']:,.2f} to ${cur_macro['net_revenue']:,.2f}, "
                f"supported by {int(cur_macro['orders'])} completed orders."
            )

        # Contributing factors list with empirical evidence
        contributing_factors: List[str] = []
        if order_chg < 0:
            contributing_factors.append(
                f"Order Volume Contraction: Completed orders decreased by {abs(order_chg)} orders ({order_pct:+.2f}%), "
                f"representing the primary driver of top-line contraction."
            )
        if aov_chg < 0:
            contributing_factors.append(
                f"Average Order Value Erosion: AOV fell by ${abs(aov_chg):,.2f} ({aov_pct:+.2f}%), "
                f"indicating lower basket sizes or shifting demand to lower-tier products."
            )
        if top_declining_products:
            total_top_loss = sum(abs(p.revenue_loss) for p in top_declining_products)
            pct_of_loss = round(self._safe_divide(total_top_loss, abs(net_rev_chg)) * 100.0, 1) if net_rev_chg < 0 else 0.0
            top_names = ", ".join(f"{p.sku} (-${abs(p.revenue_loss):,.2f})" for p in top_declining_products[:3])
            contributing_factors.append(
                f"Concentrated Product Drag: The top {len(top_declining_products)} declining products accounted for "
                f"${total_top_loss:,.2f} ({pct_of_loss}% of total decline), led by {top_names}."
            )
        if cur_macro["return_rate_pct"] > base_macro["return_rate_pct"]:
            ret_delta = round(cur_macro["return_rate_pct"] - base_macro["return_rate_pct"], 2)
            contributing_factors.append(
                f"Elevated Return Rate: Product returns increased by {ret_delta:+.2f}% to {cur_macro['return_rate_pct']}%, "
                f"causing ${cur_macro['total_refunds']:,.2f} in financial leakage."
            )

        # Recommended data-backed actions
        recommended_actions: List[str] = []
        if order_pct < -15.0:
            recommended_actions.append(
                f"Launch targeted acquisition and reactivation campaigns to address the {order_pct:+.1f}% drop in customer orders."
            )
        if top_declining_products:
            top_sku = top_declining_products[0].sku
            recommended_actions.append(
                f"Audit inventory levels, pricing competitiveness, and supplier quality for primary revenue drag {top_sku}."
            )
        if any(p.primary_driver_type == "Quality/Return Defect" for p in top_declining_products):
            recommended_actions.append(
                "Address verified product defect complaints and update product listing specifications to curtail high return rates."
            )
        if not recommended_actions:
            recommended_actions.append("Maintain current operational trajectory while monitoring weekly order volume velocity.")

        return DiagnosticReport(
            title=f"Business Performance Diagnosis: {period_label} vs. {baseline_label}",
            period_analyzed=period_label,
            baseline_period=baseline_label,
            primary_finding=primary_finding,
            severity=severity,
            net_revenue_change=net_rev_chg,
            net_revenue_change_pct=net_rev_pct,
            metric_evidences=metric_evidences,
            top_declining_products=top_declining_products,
            contributing_factors=contributing_factors,
            customer_feedback_signals=review_signals,
            recommended_actions=recommended_actions,
        )

    def diagnose_month_over_month(
        self,
        target_year: int,
        target_month: int
    ) -> DiagnosticReport:
        """
        Automated month-over-month performance diagnostic comparing target_month to preceding month.
        """
        # Current month start and end
        _, cur_last_day = monthrange(target_year, target_month)
        cur_start = date(target_year, target_month, 1)
        cur_end = date(target_year, target_month, cur_last_day)

        # Previous month start and end
        if target_month == 1:
            base_year = target_year - 1
            base_month = 12
        else:
            base_year = target_year
            base_month = target_month - 1

        _, base_last_day = monthrange(base_year, base_month)
        base_start = date(base_year, base_month, 1)
        base_end = date(base_year, base_month, base_last_day)

        return self.diagnose_revenue_decline(
            current_start=cur_start,
            current_end=cur_end,
            baseline_start=base_start,
            baseline_end=base_end
        )

    def detect_anomalies(self, lookback_months: int = 14) -> List[Dict[str, Any]]:
        """
        Scan operational time-series across the catalog to identify statistically
        significant declines or performance anomalies.
        """
        query = f"""
            WITH monthly_summary AS (
                SELECT 
                    strftime('%Y-%m', o.order_date) AS period,
                    COUNT(DISTINCT o.order_id) AS orders,
                    COALESCE(SUM(o.total_amount), 0.0) AS gross_revenue,
                    COALESCE(SUM(oi.quantity), 0) AS units_sold
                FROM orders o
                JOIN order_items oi ON o.order_id = oi.order_id
                WHERE o.status = 'completed'
                GROUP BY period
                ORDER BY period ASC
            ),
            monthly_returns AS (
                SELECT 
                    strftime('%Y-%m', r.return_date) AS period,
                    COUNT(r.return_id) AS return_count,
                    COALESCE(SUM(r.quantity_returned), 0) AS units_returned,
                    COALESCE(SUM(r.refund_amount), 0.0) AS total_refunds
                FROM returns r
                GROUP BY period
            )
            SELECT 
                ms.period,
                ms.orders,
                ms.units_sold,
                ms.gross_revenue,
                COALESCE(mr.units_returned, 0) AS units_returned,
                COALESCE(mr.total_refunds, 0.0) AS total_refunds,
                ROUND(ms.gross_revenue - COALESCE(mr.total_refunds, 0.0), 2) AS net_revenue,
                ROUND(
                    CASE WHEN ms.units_sold > 0 
                         THEN (COALESCE(mr.units_returned, 0) * 100.0) / ms.units_sold 
                         ELSE 0.0 
                    END, 2
                ) AS return_rate_pct
            FROM monthly_summary ms
            LEFT JOIN monthly_returns mr ON ms.period = mr.period
            ORDER BY ms.period ASC
            LIMIT {lookback_months};
        """
        rows = self.db.execute_query(query)
        anomalies: List[Dict[str, Any]] = []

        for i in range(1, len(rows)):
            cur = rows[i]
            prev = rows[i - 1]

            cur_net = float(cur["net_revenue"])
            prev_net = float(prev["net_revenue"])
            rev_change_pct = self._calc_pct_change(cur_net, prev_net)

            cur_ret_rate = float(cur["return_rate_pct"])
            prev_ret_rate = float(prev["return_rate_pct"])

            # 1. Significant Revenue Contraction Anomaly (>= 20% drop)
            if rev_change_pct <= -20.0:
                anomalies.append({
                    "period": cur["period"],
                    "anomaly_type": "Revenue Contraction",
                    "severity": "Critical" if rev_change_pct <= -40.0 else "High",
                    "metric_name": "Net Revenue",
                    "current_value": cur_net,
                    "previous_value": prev_net,
                    "percentage_change": rev_change_pct,
                    "summary": (
                        f"Severe revenue drop of {rev_change_pct:+.1f}% in {cur['period']} "
                        f"(${cur_net:,.2f} vs. ${prev_net:,.2f} in {prev['period']})."
                    ),
                })

            # 2. Return Rate Surge Anomaly
            if cur_ret_rate >= 8.0 or (cur_ret_rate - prev_ret_rate) >= 3.0:
                anomalies.append({
                    "period": cur["period"],
                    "anomaly_type": "Return Rate Spike",
                    "severity": "High",
                    "metric_name": "Return Rate",
                    "current_value": cur_ret_rate,
                    "previous_value": prev_ret_rate,
                    "percentage_change": self._calc_pct_change(cur_ret_rate, prev_ret_rate),
                    "summary": (
                        f"Unusual return rate surge to {cur_ret_rate}% in {cur['period']} "
                        f"(vs. {prev_ret_rate}% in {prev['period']})."
                    ),
                })

        return anomalies
