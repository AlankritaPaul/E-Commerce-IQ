"""
AI Interpretation Layer for E-Commerce Analytics.

Translates verified analytical results, scorecards, period comparisons,
and diagnostic reports into simple, executive business language.

Core Principles:
1. Strict Numerical Grounding: Every number, dollar figure, unit count, and percentage
   MUST originate directly from verified underlying database/analytics results.
2. Zero Hallucination: An automated NumericalGroundingVerifier audits all claims.
3. Executive Clarity: Translates complex distributions into plain, actionable business insights.
"""

from dataclasses import asdict, is_dataclass
import math
import re
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from ecommerce_iq.models.schemas import (
    AnalyticalInterpretation,
    CategoryReturnMetric,
    ChurnRiskCustomer,
    CustomerAggregateSummary,
    DiagnosticReport,
    EvidenceCitation,
    KPISummary,
    PeriodComparisonResult,
    ProductPerformanceMetric,
    ProductReturnMetric,
    ReturnsOverallSummary,
    ReviewSentimentSummary,
    ThemeCluster,
)


class NumericalGroundingVerifier:
    """
    Automated evidence and anti-hallucination verification engine.
    Extracts all numerical values from an interpretation narrative and verifies
    that each figure originates from the underlying analytical dataset.
    """

    # Ignored numbers: structural identifiers, common calendar years, small ranking indices
    EXEMPT_NUMBERS: Set[float] = {
        1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0,
        2024.0, 2025.0, 2026.0, 2027.0, 0.0
    }

    @classmethod
    def collect_verified_numbers(cls, source_data: Any) -> Set[float]:
        """
        Extract all raw and rounded numerical values from an analytical source object,
        including numbers embedded in diagnostic strings or summary text.
        """
        numbers: Set[float] = set()

        def _traverse(obj: Any) -> None:
            if obj is None:
                return
            if isinstance(obj, (int, float)):
                if not math.isnan(obj) and not math.isinf(obj):
                    val = float(obj)
                    numbers.add(round(val, 2))
                    numbers.add(round(val, 1))
                    numbers.add(round(val, 0))
                    numbers.add(abs(round(val, 2)))
                    numbers.add(abs(round(val, 1)))
                    numbers.add(abs(round(val, 0)))
            elif isinstance(obj, str):
                # Extract numbers present in source strings (e.g. contributing factors or finding descriptions)
                for num, _ in cls.extract_numbers_from_text(obj):
                    numbers.add(round(num, 2))
                    numbers.add(round(num, 1))
                    numbers.add(round(num, 0))
                    numbers.add(abs(round(num, 2)))
                    numbers.add(abs(round(num, 1)))
                    numbers.add(abs(round(num, 0)))
            elif is_dataclass(obj):
                for k, v in asdict(obj).items():
                    _traverse(v)
            elif isinstance(obj, dict):
                for v in obj.values():
                    _traverse(v)
            elif isinstance(obj, (list, tuple, set)):
                for item in obj:
                    _traverse(item)

        _traverse(source_data)
        return numbers

    @classmethod
    def extract_numbers_from_text(cls, text: str) -> List[Tuple[float, str]]:
        """
        Extract numeric values along with their raw text snippet from a narrative.
        Captures currency, percentages, and standard numbers without double-counting.
        """
        results: List[Tuple[float, str]] = []
        cleaned = text.replace("**", "").replace("*", "")

        pattern = re.compile(
            r"(?P<curr>[-+]?\$[0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?)"
            r"|(?P<pct>[-+]?[0-9]+(?:\.[0-9]+)?\s*%)"
            r"|(?P<num>\b[-+]?[0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?\b|\b[0-9]+\.[0-9]+\b|\b[0-9]+\b)"
        )

        for match in pattern.finditer(cleaned):
            token = match.group(0).strip()
            if not token:
                continue
            num_str = token.replace("$", "").replace("%", "").replace(",", "").strip()
            try:
                val = float(num_str)
                results.append((val, token))
            except ValueError:
                continue

        return results

    @classmethod
    def verify(
        cls,
        interpretation: AnalyticalInterpretation,
        source_data: Any,
        tolerance_pct: float = 0.02
    ) -> Tuple[bool, List[str]]:
        """
        Audit the interpretation against source data.
        Returns (is_grounded, list_of_unverified_claims).
        """
        verified_pool = cls.collect_verified_numbers(source_data)
        unverified_claims: List[str] = []

        # Combine all narrative text for audit
        all_text = " ".join([
            interpretation.summary,
            " ".join(interpretation.key_findings),
            " ".join(interpretation.evidence_based_insights),
            " ".join(interpretation.actionable_recommendations)
        ])

        extracted = cls.extract_numbers_from_text(all_text)

        for num, token in extracted:
            abs_num = abs(num)
            # Skip trivial integers and structural years
            if abs_num in cls.EXEMPT_NUMBERS:
                continue

            # Check if this number exists in the verified numbers pool
            is_matched = False
            for v in verified_pool:
                abs_v = abs(v)
                if abs_v == 0.0:
                    if abs_num == 0.0:
                        is_matched = True
                        break
                    continue

                # Direct match or within tolerance (to handle rounded text like 61.0% vs 61.03%)
                if abs(abs_num - abs_v) <= 0.05 or abs(abs_num - abs_v) / abs_v <= tolerance_pct:
                    is_matched = True
                    break

            if not is_matched:
                unverified_claims.append(f"Unverified figure '{token}' ({num}) not present in source analytics data.")

        is_grounded = len(unverified_claims) == 0
        return is_grounded, unverified_claims


class AnalyticsInterpreter:
    """
    Translates verified business metrics into executive explanations,
    key findings, causal insights, and actionable advice.
    """

    def __init__(self, verifier: Optional[NumericalGroundingVerifier] = None) -> None:
        self.verifier = verifier or NumericalGroundingVerifier()

    # --------------------------------------------------------------------------
    # 1. KPI Scorecard Interpretation
    # --------------------------------------------------------------------------
    def interpret_kpis(self, kpis: KPISummary) -> AnalyticalInterpretation:
        """Explain high-level executive performance scorecard."""
        margin_text = (
            f" with a gross profit margin of **{kpis.gross_margin_percentage:.1f}%**"
            if kpis.gross_margin_percentage is not None
            else ""
        )

        summary = (
            f"Business operations delivered **${kpis.net_revenue:,.2f}** in net revenue across "
            f"**{kpis.total_orders:,} completed orders**{margin_text}. "
            f"Average Order Value (AOV) stands at **${kpis.average_order_value:,.2f}** "
            f"supported by **{kpis.active_customers:,} active purchasers**."
        )

        key_findings = [
            f"Total Gross Sales reached **${kpis.total_revenue:,.2f}** resulting in Net Revenue of **${kpis.net_revenue:,.2f}**.",
            f"Average transaction basket size (AOV) is **${kpis.average_order_value:,.2f}** across **{kpis.total_orders:,}** orders.",
            f"Processed **${kpis.total_refunds:,.2f}** in refunds, representing a **{kpis.return_rate_percentage:.2f}%** return rate.",
            f"Customer engagement encompasses **{kpis.active_customers:,}** unique purchasing accounts."
        ]

        insights = [
            "Revenue health is sustained by robust order density and steady customer purchasing frequency.",
            f"Refunds account for ${(kpis.total_revenue - kpis.net_revenue):,.2f} of gross top-line, which is well within normal e-commerce thresholds."
            if kpis.return_rate_percentage < 7.0
            else f"Return rate of {kpis.return_rate_percentage:.2f}% represents margin leakage that requires SKU-level quality triage."
        ]

        recommendations = [
            "Maintain current advertising channels while testing bundled offerings to increase AOV.",
            "Monitor product categories with elevated refund volumes to preserve net profit margins."
        ]

        citations = [
            EvidenceCitation("Net Revenue", kpis.net_revenue, f"${kpis.net_revenue:,.2f}", "net_revenue", "Final realized net sales"),
            EvidenceCitation("Total Orders", float(kpis.total_orders), f"{kpis.total_orders:,}", "total_orders", "Completed customer order volume"),
            EvidenceCitation("AOV", kpis.average_order_value, f"${kpis.average_order_value:,.2f}", "average_order_value", "Average order value per transaction"),
            EvidenceCitation("Return Rate", kpis.return_rate_percentage, f"{kpis.return_rate_percentage:.2f}%", "return_rate_percentage", "Platform return rate percentage"),
            EvidenceCitation("Active Purchasers", float(kpis.active_customers), f"{kpis.active_customers:,}", "active_customers", "Unique buyers placing orders"),
        ]

        interp = AnalyticalInterpretation(
            title="Executive KPI Scorecard Interpretation",
            summary=summary,
            key_findings=key_findings,
            evidence_based_insights=insights,
            actionable_recommendations=recommendations,
            evidence_citations=citations,
            source_analytics_type="KPISummary"
        )

        is_grounded, unverified = self.verifier.verify(interp, kpis)
        interp.is_grounded = is_grounded
        interp.unverified_claims = unverified
        return interp

    # --------------------------------------------------------------------------
    # 2. Period Comparison (MoM / WoW) Interpretation
    # --------------------------------------------------------------------------
    def interpret_period_comparison(
        self,
        comparisons: List[PeriodComparisonResult],
        period_label: str = "Month-over-Month"
    ) -> AnalyticalInterpretation:
        """Explain variance and trend trajectories across operational periods."""
        rev_comp = next((c for c in comparisons if "revenue" in c.metric_name.lower()), None)
        ord_comp = next((c for c in comparisons if "order" in c.metric_name.lower()), None)
        aov_comp = next((c for c in comparisons if "aov" in c.metric_name.lower() or "average order" in c.metric_name.lower()), None)

        if rev_comp:
            direction = "contracted" if rev_comp.percentage_change < 0 else "expanded"
            rev_change_str = (
                f"-${abs(rev_comp.absolute_change):,.2f}"
                if rev_comp.absolute_change < 0
                else f"+${rev_comp.absolute_change:,.2f}"
            )
            summary = (
                f"{period_label} performance {direction}: Net revenue shifted by "
                f"**{rev_comp.percentage_change:+.2f}%** (**{rev_change_str}**), moving from "
                f"**${rev_comp.previous_value:,.2f}** to **${rev_comp.current_value:,.2f}**."
            )
        else:
            summary = f"{period_label} variance analysis evaluated across {len(comparisons)} operational metrics."

        key_findings = []
        citations = []
        for c in comparisons:
            sign = "+" if c.absolute_change > 0 else ""
            key_findings.append(
                f"**{c.metric_name}**: {sign}{c.percentage_change:.2f}% shift ({sign}{c.absolute_change:,.2f}) "
                f"[Baseline: {c.previous_value:,.2f} -> Current: {c.current_value:,.2f}]."
            )
            citations.append(
                EvidenceCitation(
                    c.metric_name,
                    c.current_value,
                    f"{c.current_value:,.2f}",
                    c.metric_name,
                    f"Shift: {c.percentage_change:+.2f}%"
                )
            )

        insights = []
        if rev_comp and ord_comp:
            if rev_comp.percentage_change < -20.0 and ord_comp.percentage_change < -20.0:
                insights.append(
                    f"Revenue decline of {rev_comp.percentage_change:.2f}% was heavily driven by order volume contraction "
                    f"({ord_comp.percentage_change:.2f}%), indicating customer drop-off rather than price compression."
                )
            elif rev_comp.percentage_change > 20.0:
                insights.append(
                    f"Strong top-line acceleration of {rev_comp.percentage_change:+.2f}% was powered by "
                    f"order volume gains of {ord_comp.percentage_change:+.2f}%."
                )

        if aov_comp:
            insights.append(
                f"Basket value shifted by {aov_comp.percentage_change:+.2f}%, indicating "
                f"{'higher transaction depth' if aov_comp.percentage_change > 0 else 'lower unit attach rates'}."
            )

        recommendations = [
            "Align marketing ad-spend and promotional campaigns with the observed order volume patterns.",
            "Review product-level inventory availability during periods of rapid volume shifts."
        ]

        interp = AnalyticalInterpretation(
            title=f"{period_label} Variance & Trend Interpretation",
            summary=summary,
            key_findings=key_findings,
            evidence_based_insights=insights,
            actionable_recommendations=recommendations,
            evidence_citations=citations,
            source_analytics_type="List[PeriodComparisonResult]"
        )

        is_grounded, unverified = self.verifier.verify(interp, comparisons)
        interp.is_grounded = is_grounded
        interp.unverified_claims = unverified
        return interp

    # --------------------------------------------------------------------------
    # 3. Product Performance Interpretation
    # --------------------------------------------------------------------------
    def interpret_product_performance(
        self,
        products: List[ProductPerformanceMetric]
    ) -> AnalyticalInterpretation:
        """Explain SKU-level catalog performance, winners, and margin laggards."""
        if not products:
            return AnalyticalInterpretation(
                title="Product Catalog Performance",
                summary="No product performance data available to interpret.",
                is_grounded=True,
                source_analytics_type="List[ProductPerformanceMetric]"
            )

        sorted_by_rev = sorted(products, key=lambda p: p.total_revenue, reverse=True)
        top_sku = sorted_by_rev[0]
        total_catalog_rev = sum(p.total_revenue for p in products)

        summary = (
            f"Catalog analysis across **{len(products)} products** reveals total realized revenue of "
            f"**${total_catalog_rev:,.2f}**. Leading product **{top_sku.title}** ({top_sku.sku}) "
            f"generated **${top_sku.total_revenue:,.2f}** across **{top_sku.units_sold:,} units sold**."
        )

        key_findings = [
            f"Top Revenue Generator: **{top_sku.title}** contributed **${top_sku.total_revenue:,.2f}** ({top_sku.units_sold:,} units, {top_sku.avg_rating:.2f} stars).",
        ]

        for idx, p in enumerate(sorted_by_rev[1:4], 2):
            key_findings.append(
                f"Rank {idx}: **{p.title}** generated **${p.total_revenue:,.2f}** across **{p.units_sold:,} units** (Return rate: {p.return_rate_pct:.2f}%)."
            )

        high_returns = [p for p in products if p.return_rate_pct >= 10.0]
        if high_returns:
            worst = max(high_returns, key=lambda p: p.return_rate_pct)
            key_findings.append(
                f"Quality Concern: **{worst.title}** exhibits an elevated return rate of **{worst.return_rate_pct:.2f}%**."
            )

        insights = [
            f"Revenue is concentrated in top-tier bestsellers, with **{top_sku.title}** representing a substantial share of unit sales.",
            "Products maintaining return rates under 5% and CSAT above 4.0 demonstrate sustainable product-market fit."
        ]

        recommendations = [
            f"Maintain safety inventory buffers for **{top_sku.title}** to prevent stockouts.",
            "Investigate supplier batches for items with return rates exceeding 10%."
        ]

        citations = [
            EvidenceCitation(top_sku.title, top_sku.total_revenue, f"${top_sku.total_revenue:,.2f}", "total_revenue", "Top SKU Revenue"),
            EvidenceCitation(f"{top_sku.title} Units", float(top_sku.units_sold), f"{top_sku.units_sold:,}", "units_sold", "Units Sold"),
            EvidenceCitation("Catalog Total Revenue", total_catalog_rev, f"${total_catalog_rev:,.2f}", "catalog_total", "Summed catalog revenue"),
        ]

        interp = AnalyticalInterpretation(
            title="Product Catalog & Unit Economics Interpretation",
            summary=summary,
            key_findings=key_findings,
            evidence_based_insights=insights,
            actionable_recommendations=recommendations,
            evidence_citations=citations,
            source_analytics_type="List[ProductPerformanceMetric]"
        )

        is_grounded, unverified = self.verifier.verify(interp, products + [total_catalog_rev])
        interp.is_grounded = is_grounded
        interp.unverified_claims = unverified
        return interp

    # --------------------------------------------------------------------------
    # 4. Customer Behavioral & Retention Interpretation
    # --------------------------------------------------------------------------
    def interpret_customer_behavior(
        self,
        summary: CustomerAggregateSummary,
        churn_risks: Optional[List[ChurnRiskCustomer]] = None
    ) -> AnalyticalInterpretation:
        """Explain customer purchasing frequency, retention, LTV, and churn risk."""
        churn_count = len(churn_risks) if churn_risks else 0
        at_risk_revenue = sum(c.estimated_revenue_at_risk for c in churn_risks) if churn_risks else 0.0

        exec_summary = (
            f"Customer behavioral analysis shows a customer base of **{summary.total_registered_customers:,} registered accounts**, "
            f"of which **{summary.active_purchasers:,} are active purchasers**. "
            f"Repeat purchasing is strong at **{summary.repeat_purchase_rate_pct:.2f}%** "
            f"(**{summary.repeat_customers:,} repeat buyers**), driving an Average Lifetime Value (LTV) of **${summary.average_customer_ltv:,.2f}**."
        )

        key_findings = [
            f"Repeat Purchase Rate: **{summary.repeat_purchase_rate_pct:.2f}%** ({summary.repeat_customers:,} repeat vs {summary.one_time_buyers:,} one-time buyers).",
            f"Average Customer LTV: **${summary.average_customer_ltv:,.2f}** with an average purchase frequency of **{summary.average_order_frequency:.2f} orders**.",
            f"Customer Return Rate: **{summary.customer_return_rate_pct:.2f}%** of purchasing accounts have initiated a return.",
            f"Review Participation: **{summary.review_participation_rate_pct:.2f}%** of customers submitted feedback."
        ]

        if churn_count > 0:
            key_findings.append(
                f"Churn Risk Cohort: Identified **{churn_count} dormant high-value customers** with **${at_risk_revenue:,.2f}** in annualized revenue at risk."
            )

        insights = [
            f"High repeat purchase rate of {summary.repeat_purchase_rate_pct:.2f}% indicates high brand loyalty and strong product satisfaction.",
            f"Retaining existing active buyers is substantially more accretive than acquisition, given the ${summary.average_customer_ltv:,.2f} average LTV."
        ]

        recommendations = [
            "Launch personalized email re-engagement sequences with incentive discounts for the dormant high-value customer segment.",
            "Implement a VIP tiered loyalty rewards program to nurture high-frequency repeat buyers."
        ]

        citations = [
            EvidenceCitation("Repeat Purchase Rate", summary.repeat_purchase_rate_pct, f"{summary.repeat_purchase_rate_pct:.2f}%", "repeat_purchase_rate_pct"),
            EvidenceCitation("Average LTV", summary.average_customer_ltv, f"${summary.average_customer_ltv:,.2f}", "average_customer_ltv"),
            EvidenceCitation("Active Purchasers", float(summary.active_purchasers), f"{summary.active_purchasers:,}", "active_purchasers"),
            EvidenceCitation("Repeat Customers", float(summary.repeat_customers), f"{summary.repeat_customers:,}", "repeat_customers"),
        ]

        if churn_count > 0:
            citations.append(EvidenceCitation("Revenue at Risk", at_risk_revenue, f"${at_risk_revenue:,.2f}", "at_risk_revenue"))

        interp = AnalyticalInterpretation(
            title="Customer Retention & Behavioral Dynamics",
            summary=exec_summary,
            key_findings=key_findings,
            evidence_based_insights=insights,
            actionable_recommendations=recommendations,
            evidence_citations=citations,
            source_analytics_type="CustomerAggregateSummary"
        )

        is_grounded, unverified = self.verifier.verify(interp, [summary, at_risk_revenue, churn_count])
        interp.is_grounded = is_grounded
        interp.unverified_claims = unverified
        return interp

    # --------------------------------------------------------------------------
    # 5. Customer Reviews & Sentiment Interpretation
    # --------------------------------------------------------------------------
    def interpret_customer_reviews(
        self,
        summary: ReviewSentimentSummary,
        recurring_issues: Optional[List[ThemeCluster]] = None
    ) -> AnalyticalInterpretation:
        """Explain customer sentiment, rating distributions, and defect signals."""
        sentiment_verdict = (
            "strongly positive" if summary.average_rating >= 4.0
            else "moderate" if summary.average_rating >= 3.0
            else "concerning"
        )

        exec_summary = (
            f"Customer response intelligence across **{summary.total_reviews:,} verified reviews** reflects a "
            f"**{sentiment_verdict} satisfaction score of {summary.average_rating:.2f} / 5.0 stars**. "
            f"Positive feedback dominates at **{summary.positive_percentage:.2f}%** (**{summary.positive_count:,} reviews**), "
            f"while negative feedback comprises **{summary.negative_percentage:.2f}%** (**{summary.negative_count:,} reviews**)."
        )

        key_findings = [
            f"Overall Platform CSAT: **{summary.average_rating:.2f} / 5.0 stars** across **{summary.total_reviews:,}** submissions.",
            f"Sentiment Balance: **{summary.positive_count:,} positive** ({summary.positive_percentage:.2f}%), **{summary.neutral_count:,} neutral**, **{summary.negative_count:,} negative** ({summary.negative_percentage:.2f}%).",
        ]

        if summary.top_praises:
            key_findings.append(f"Top Customer Praise: '{summary.top_praises[0]}'.")

        if summary.top_complaints:
            key_findings.append(f"Leading Customer Complaint: '{summary.top_complaints[0]}'.")

        if recurring_issues:
            top_issue = recurring_issues[0]
            key_findings.append(
                f"Critical Defect Cluster: **'{top_issue.theme_title}'** referenced in **{top_issue.review_count} reviews** ({top_issue.percentage_of_reviews:.2f}% of catalog reviews)."
            )

        insights = [
            f"Customer sentiment demonstrates solid approval with {summary.positive_percentage:.2f}% positive ratings.",
            "Customer complaints provide direct feedback signals pointing to specific hardware, sizing, or packaging vulnerabilities."
        ]

        recommendations = [
            "Review customer complaint patterns with manufacturers to resolve verified hardware or material issues.",
            "Highlight top-rated customer praise themes in promotional copy to build buyer trust."
        ]

        citations = [
            EvidenceCitation("Average Rating", summary.average_rating, f"{summary.average_rating:.2f}", "average_rating"),
            EvidenceCitation("Total Reviews", float(summary.total_reviews), f"{summary.total_reviews:,}", "total_reviews"),
            EvidenceCitation("Positive Percentage", summary.positive_percentage, f"{summary.positive_percentage:.2f}%", "positive_percentage"),
            EvidenceCitation("Negative Percentage", summary.negative_percentage, f"{summary.negative_percentage:.2f}%", "negative_percentage"),
        ]

        interp = AnalyticalInterpretation(
            title="Customer Response & Sentiment Intelligence",
            summary=exec_summary,
            key_findings=key_findings,
            evidence_based_insights=insights,
            actionable_recommendations=recommendations,
            evidence_citations=citations,
            source_analytics_type="ReviewSentimentSummary"
        )

        is_grounded, unverified = self.verifier.verify(interp, [summary, recurring_issues])
        interp.is_grounded = is_grounded
        interp.unverified_claims = unverified
        return interp

    # --------------------------------------------------------------------------
    # 6. Returns & Refunds Interpretation
    # --------------------------------------------------------------------------
    def interpret_returns(
        self,
        summary: ReturnsOverallSummary,
        high_risk_products: Optional[List[ProductReturnMetric]] = None
    ) -> AnalyticalInterpretation:
        """Explain returns velocity, refund capital leakage, and defect root causes."""
        exec_summary = (
            f"Platform returns analytics report **{summary.total_return_events:,} return incidents** "
            f"encompassing **{summary.total_units_returned:,} units returned**, resulting in "
            f"**${summary.total_refund_amount:,.2f}** in total refunds. "
            f"The overall platform return rate is **{summary.platform_return_rate_pct:.2f}%** with a "
            f"**{summary.refund_ratio_pct:.2f}%** refund ratio."
        )

        key_findings = [
            f"Total Financial Refund Leakage: **${summary.total_refund_amount:,.2f}** across **{summary.total_units_returned:,} returned items**.",
            f"Platform Return Rate: **{summary.platform_return_rate_pct:.2f}%** (Refund ratio: {summary.refund_ratio_pct:.2f}% of gross sales).",
            f"High Risk Inventory: **{summary.high_risk_products_count} products** flagged in the elevated return risk tier."
        ]

        if summary.top_return_reasons:
            top_reason = summary.top_return_reasons[0]
            key_findings.append(
                f"Primary Return Reason: **'{top_reason.reason}'** accounted for **{top_reason.incident_count} incidents** (${top_reason.total_refund_amount:,.2f} refunded, {top_reason.percentage_of_all_returns:.2f}% of all returns)."
            )

        if high_risk_products:
            worst_p = high_risk_products[0]
            key_findings.append(
                f"Most Returned Product: **{worst_p.title}** ({worst_p.sku}) with an alarming **{worst_p.return_rate_pct:.2f}% return rate** (${worst_p.refund_amount:,.2f} refunded)."
            )

        insights = [
            f"Refunds totaling ${summary.total_refund_amount:,.2f} represent a direct impact on gross margins.",
            "High-risk products disproportionately drive refund costs; resolving defects in flagged SKUs will immediately improve net margins."
        ]

        recommendations = [
            "Audit supplier quality for products flagged in the high-risk return tier.",
            "Update product sizing charts and description pages to reduce buyer remorse and sizing mismatch returns."
        ]

        citations = [
            EvidenceCitation("Total Refunds", summary.total_refund_amount, f"${summary.total_refund_amount:,.2f}", "total_refund_amount"),
            EvidenceCitation("Units Returned", float(summary.total_units_returned), f"{summary.total_units_returned:,}", "total_units_returned"),
            EvidenceCitation("Return Rate", summary.platform_return_rate_pct, f"{summary.platform_return_rate_pct:.2f}%", "platform_return_rate_pct"),
            EvidenceCitation("High Risk Products", float(summary.high_risk_products_count), f"{summary.high_risk_products_count}", "high_risk_products_count"),
        ]

        interp = AnalyticalInterpretation(
            title="Returns & Financial Refund Analysis",
            summary=exec_summary,
            key_findings=key_findings,
            evidence_based_insights=insights,
            actionable_recommendations=recommendations,
            evidence_citations=citations,
            source_analytics_type="ReturnsOverallSummary"
        )

        is_grounded, unverified = self.verifier.verify(interp, [summary, high_risk_products])
        interp.is_grounded = is_grounded
        interp.unverified_claims = unverified
        return interp

    # --------------------------------------------------------------------------
    # 7. Diagnostic Report Interpretation ("Why did sales decrease?")
    # --------------------------------------------------------------------------
    def interpret_diagnostic(self, report: DiagnosticReport) -> AnalyticalInterpretation:
        """Explain multi-factor business performance decline diagnosis."""
        rev_change_str = (
            f"-${abs(report.net_revenue_change):,.2f}"
            if report.net_revenue_change < 0
            else f"+${report.net_revenue_change:,.2f}"
        )
        exec_summary = (
            f"Performance diagnosis for **{report.period_analyzed}** vs **{report.baseline_period}** classified as "
            f"**{report.severity} Severity**: Net revenue shifted by **{rev_change_str}** "
            f"(**{report.net_revenue_change_pct:+.2f}%**). {report.primary_finding}"
        )

        key_findings = []
        citations = [
            EvidenceCitation("Net Revenue Change", report.net_revenue_change, rev_change_str, "net_revenue_change"),
            EvidenceCitation("Net Revenue Change Pct", report.net_revenue_change_pct, f"{report.net_revenue_change_pct:+.2f}%", "net_revenue_change_pct"),
        ]

        for m in report.metric_evidences[:4]:
            sign = "+" if m.absolute_change > 0 else ""
            key_findings.append(
                f"**{m.metric_name}** ({m.significance}): {sign}{m.percentage_change:.2f}% ({sign}{m.absolute_change:,.2f} {m.unit}) "
                f"[Baseline: {m.baseline_value:,.2f} -> Current: {m.current_value:,.2f}]."
            )
            citations.append(
                EvidenceCitation(m.metric_name, m.current_value, f"{m.current_value:,.2f}", m.metric_name, f"Delta: {m.percentage_change:+.2f}%")
            )

        if report.top_declining_products:
            p = report.top_declining_products[0]
            key_findings.append(
                f"Primary Declining SKU: **{p.title}** ({p.sku}) lost **${p.revenue_loss:,.2f}** ({p.percentage_change:.2f}% drop), driving {p.primary_driver_type}."
            )
            citations.append(
                EvidenceCitation(f"{p.title} Revenue Loss", p.revenue_loss, f"${p.revenue_loss:,.2f}", "revenue_loss")
            )

        insights = report.contributing_factors.copy() if report.contributing_factors else [
            "Decline investigation isolated the primary quantitative drivers behind the revenue drop."
        ]

        recommendations = report.recommended_actions.copy() if report.recommended_actions else [
            "Address order volume contraction and audit inventory for top revenue-generating products."
        ]

        interp = AnalyticalInterpretation(
            title=f"Business Performance Diagnosis: {report.period_analyzed}",
            summary=exec_summary,
            key_findings=key_findings,
            evidence_based_insights=insights,
            actionable_recommendations=recommendations,
            evidence_citations=citations,
            source_analytics_type="DiagnosticReport"
        )

        is_grounded, unverified = self.verifier.verify(interp, report)
        interp.is_grounded = is_grounded
        interp.unverified_claims = unverified
        return interp

    # --------------------------------------------------------------------------
    # 8. Polymorphic Universal Dispatcher
    # --------------------------------------------------------------------------
    def interpret(self, data: Any, context: Optional[str] = None) -> AnalyticalInterpretation:
        """
        Universal interpretation dispatcher that inspects the type of analytical data
        and routes to the appropriate domain-specific interpretation engine.
        """
        if isinstance(data, KPISummary):
            return self.interpret_kpis(data)
        elif isinstance(data, DiagnosticReport):
            return self.interpret_diagnostic(data)
        elif isinstance(data, ReturnsOverallSummary):
            return self.interpret_returns(data)
        elif isinstance(data, ReviewSentimentSummary):
            return self.interpret_customer_reviews(data)
        elif isinstance(data, CustomerAggregateSummary):
            return self.interpret_customer_behavior(data)
        elif isinstance(data, list) and len(data) > 0:
            first_item = data[0]
            if isinstance(first_item, PeriodComparisonResult):
                label = context or "Period-over-Period"
                return self.interpret_period_comparison(data, period_label=label)
            elif isinstance(first_item, ProductPerformanceMetric):
                return self.interpret_product_performance(data)
            elif isinstance(first_item, ChurnRiskCustomer):
                return self.interpret_customer_behavior(
                    CustomerAggregateSummary(0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0),
                    churn_risks=data
                )
            elif isinstance(first_item, ProductReturnMetric):
                return self.interpret_returns(
                    ReturnsOverallSummary(0, 0, 0.0, 0.0, 0.0, len(data)),
                    high_risk_products=data
                )

        raise TypeError(f"Unsupported analytical data type for AI interpretation: {type(data)}")
