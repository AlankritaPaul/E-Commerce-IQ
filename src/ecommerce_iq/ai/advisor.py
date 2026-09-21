"""
Executive Business Advisor and Narrative Synthesizer.

Transforms raw SQL query result sets and analytical metrics into natural,
concise executive insights with actionable explanations for business owners.
"""

from typing import Any, Dict, List, Optional


class BusinessAdvisor:
    """
    Synthesizes analytical database records into clear, data-grounded executive answers.
    """

    def __init__(self, llm_client: Optional[Any] = None) -> None:
        self.llm = llm_client

    def synthesize_answer(
        self,
        question: str,
        sql_query: str,
        query_results: List[Dict[str, Any]],
        intent_category: str = "general"
    ) -> str:
        """
        Produce a clear, executive, data-grounded narrative answering the user's question.
        """
        if not query_results:
            return f"No records found in the database matching your query: '{question}'."

        first_row = query_results[0]

        # ----------------------------------------------------------------------
        # 1. Revenue & Sales Inquiries
        # ----------------------------------------------------------------------
        if intent_category == "revenue":
            total_rev = first_row.get("total_revenue", 0.0)
            orders = first_row.get("total_orders", 0)
            aov = first_row.get("average_order_value", 0.0)

            month = first_row.get("month")
            if month:
                lines = [f"**Monthly Revenue Breakdown** ({len(query_results)} periods):"]
                for r in query_results[:6]:
                    lines.append(f"- **{r['month']}**: ${float(r.get('total_revenue', 0.0)):,.2f} ({int(r.get('total_orders', 0))} orders)")
                return "\n".join(lines)

            return (
                f"Our total net revenue is **${float(total_rev):,.2f}** generated across "
                f"**{int(orders):,} completed orders**, with an Average Order Value (AOV) of **${float(aov):,.2f}**.\n\n"
                f"**Key Takeaway**: Overall revenue performance demonstrates healthy order density and strong transaction value."
            )

        # ----------------------------------------------------------------------
        # 2. Top / Bestselling Products
        # ----------------------------------------------------------------------
        if intent_category == "top_products":
            top_item = first_row.get("title", "Product")
            top_rev = first_row.get("total_revenue", 0.0)
            top_units = first_row.get("units_sold", 0)

            lines = [
                f"Our top-performing product is **{top_item}**, generating **${float(top_rev):,.2f}** "
                f"across **{int(top_units):,} units sold**.",
                "\n**Top Products Ranking**:"
            ]
            for idx, r in enumerate(query_results[:5], 1):
                t = r.get("title", f"Product {idx}")
                rev = float(r.get("total_revenue", 0.0))
                u = int(r.get("units_sold", 0))
                lines.append(f"{idx}. **{t}**: ${rev:,.2f} ({u:,} units)")

            lines.append("\n**Actionable Advice**: Ensure high inventory buffers on these bestsellers to avoid stockouts during demand spikes.")
            return "\n".join(lines)

        # ----------------------------------------------------------------------
        # 3. Underperforming / Dead Stock Products
        # ----------------------------------------------------------------------
        if intent_category == "underperforming":
            lines = [
                f"Identified **{len(query_results)} products** with low sales velocity and revenue contribution:",
                ""
            ]
            for idx, r in enumerate(query_results[:5], 1):
                t = r.get("title", "Product")
                rev = float(r.get("total_revenue", 0.0))
                u = int(r.get("units_sold", 0))
                lines.append(f"{idx}. **{t}**: ${rev:,.2f} total revenue ({u} units sold)")

            lines.append("\n**Actionable Advice**: Consider discounting, bundling with top-selling products, or phasing out slow-moving inventory to free up working capital.")
            return "\n".join(lines)

        # ----------------------------------------------------------------------
        # 4. Returns & Refunds
        # ----------------------------------------------------------------------
        if intent_category == "returns":
            if "return_rate_pct" in first_row:
                top_sku = first_row.get("sku", "")
                top_title = first_row.get("title", "Product")
                top_rate = first_row.get("return_rate_pct", 0.0)
                top_refunds = first_row.get("total_refunds", 0.0)

                lines = [
                    f"The product with the highest return rate is **{top_title}** ({top_sku}) with an alarming **{top_rate}% return rate** (${float(top_refunds):,.2f} refunded).",
                    "\n**Highest Return Products**:"
                ]
                for idx, r in enumerate(query_results[:5], 1):
                    lines.append(f"{idx}. **{r.get('title')}**: {r.get('return_rate_pct')}% return rate (${float(r.get('total_refunds', 0.0)):,.2f} refunded)")

                lines.append("\n**Actionable Advice**: Audit supplier batch quality and review customer RMA notes to address root-cause defects.")
                return "\n".join(lines)
            elif "return_reason" in first_row:
                lines = ["**Customer Return Reasons Breakdown**:"]
                for r in query_results:
                    lines.append(f"- **{r.get('return_reason')}**: {r.get('return_count')} returns (${float(r.get('total_refunds', 0.0)):,.2f} refunded)")
                return "\n".join(lines)
            else:
                events = first_row.get("total_return_events", 0)
                units = first_row.get("total_units_returned", 0)
                amt = first_row.get("total_refund_amount", 0.0)
                return f"Platform-wide, we have processed **{events} return events** ({units} units returned), resulting in **${float(amt):,.2f}** in refunds."

        # ----------------------------------------------------------------------
        # 5. Customer Reviews & Feedback
        # ----------------------------------------------------------------------
        if intent_category == "reviews":
            if "complaint" in first_row:
                top_comp = first_row.get("complaint", "Issue")
                top_cnt = first_row.get("complaint_count", 0)
                lines = [
                    f"The most prevalent customer complaint is **'{top_comp}'** with **{top_cnt} documented instances**.",
                    "\n**Top Customer Issues**:"
                ]
                for idx, r in enumerate(query_results[:5], 1):
                    lines.append(f"{idx}. **{r.get('complaint')}**: {r.get('complaint_count')} complaints (Avg rating: {r.get('avg_rating', 0.0)} stars)")
                lines.append("\n**Actionable Advice**: Prioritize packaging reinforcement and manufacturer quality controls for affected product lines.")
                return "\n".join(lines)
            elif "sentiment_label" in first_row:
                lines = ["**Customer Review Sentiment Breakdown**:"]
                for r in query_results:
                    lines.append(f"- **{r.get('sentiment_label').title()}**: {r.get('count')} reviews (Avg rating: {r.get('average_rating')} stars)")
                return "\n".join(lines)
            else:
                tot = first_row.get("total_reviews", 0)
                avg_rat = first_row.get("average_rating", 0.0)
                pos = first_row.get("positive_reviews", 0)
                neg = first_row.get("negative_reviews", 0)
                return (
                    f"Our overall customer satisfaction score is **{avg_rat} / 5.0 stars** across **{tot:,} verified reviews**.\n\n"
                    f"- **Positive Reviews (4-5 stars)**: {pos:,} ({round(pos * 100.0 / max(1, tot), 1)}%)\n"
                    f"- **Negative Reviews (1-2 stars)**: {neg:,} ({round(neg * 100.0 / max(1, tot), 1)}%)\n\n"
                    f"**Summary**: Customer sentiment is predominantly positive, with high praise for product craftsmanship and fast shipping."
                )

        # ----------------------------------------------------------------------
        # 6. Customer Demographics & Repeat Buyers
        # ----------------------------------------------------------------------
        if intent_category == "customers":
            if "repeat_rate_pct" in first_row:
                tot_p = first_row.get("total_purchasers", 0)
                rep_b = first_row.get("repeat_buyers", 0)
                rate = first_row.get("repeat_rate_pct", 0.0)
                return (
                    f"We have **{rep_b:,} repeat customers** out of **{tot_p:,} active buyers**, "
                    f"representing an exceptional **{rate}% repeat purchase rate**.\n\n"
                    f"**Actionable Advice**: Reward high-frequency buyers with exclusive VIP loyalty perks to maximize customer lifetime value."
                )
            elif "customer_segment" in first_row:
                lines = ["**Customer Segment Breakdown**:"]
                for r in query_results:
                    lines.append(f"- **{r.get('customer_segment')}**: {r.get('customer_count')} customers")
                return "\n".join(lines)
            else:
                tot_reg = first_row.get("total_registered", 0)
                ltv = first_row.get("avg_customer_ltv", 0.0)
                freq = first_row.get("avg_orders_per_customer", 0.0)
                return f"We have **{tot_reg:,} registered customers** with an average Lifetime Value (LTV) of **${float(ltv):,.2f}** and order frequency of **{freq} orders**."

        # ----------------------------------------------------------------------
        # 7. Category Performance
        # ----------------------------------------------------------------------
        if intent_category == "categories":
            top_cat = first_row.get("category_name", "Category")
            top_rev = first_row.get("gross_revenue", 0.0)
            lines = [
                f"Our leading category is **{top_cat}**, generating **${float(top_rev):,.2f}** in gross sales.",
                "\n**Revenue by Category**:"
            ]
            for idx, r in enumerate(query_results, 1):
                lines.append(f"{idx}. **{r.get('category_name')}**: ${float(r.get('gross_revenue', 0.0)):,.2f} ({int(r.get('units_sold', 0)):,} units)")
            return "\n".join(lines)

        # ----------------------------------------------------------------------
        # 8. Specific Product Lookup
        # ----------------------------------------------------------------------
        if intent_category == "product_lookup":
            t = first_row.get("title", "Product")
            sku = first_row.get("sku", "")
            cat = first_row.get("category", "")
            rev = float(first_row.get("total_revenue", 0.0))
            units = int(first_row.get("units_sold", 0))
            rating = float(first_row.get("avg_rating", 0.0))
            return (
                f"**{t}** ({sku} - {cat}):\n"
                f"- **Net Revenue**: ${rev:,.2f}\n"
                f"- **Units Sold**: {units:,} units\n"
                f"- **Customer CSAT**: {rating} / 5.0 stars\n"
            )

        # ----------------------------------------------------------------------
        # General Default Summary
        # ----------------------------------------------------------------------
        metrics_str = ", ".join(f"**{k}**: {v}" for k, v in first_row.items())
        return f"Query returned {len(query_results)} records. Primary metrics: {metrics_str}."
