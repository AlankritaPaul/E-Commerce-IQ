"""
Interactive Plotly Visualization Components.

Generates high-contrast, responsive financial charts, sales trends,
category distributions, and return rate visualizations for executive decision making.
"""

from typing import Any, Dict, List, Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Professional Slate / Corporate Color Palette
NAVY_PRIMARY = "#1E3A8A"
EMERALD_GREEN = "#059669"
ROSE_RED = "#E11D48"
AMBER_GOLD = "#D97706"
SLATE_GRAY = "#64748B"
LIGHT_BG = "#F8FAFC"
BORDER_COLOR = "#E2E8F0"


def render_revenue_trend_chart(monthly_data: List[Dict[str, Any]]) -> go.Figure:
    """
    Generate dual-axis time-series chart showing Net Revenue ($) and Completed Order Volume.
    """
    if not monthly_data:
        fig = go.Figure()
        fig.update_layout(title="No Monthly Revenue Data Available")
        return fig

    months = [d.get("month", "") for d in monthly_data]
    revenues = [float(d.get("total_revenue", 0.0)) for d in monthly_data]
    orders = [int(d.get("total_orders", 0)) for d in monthly_data]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Bar trace: Monthly Net Revenue
    fig.add_trace(
        go.Bar(
            x=months,
            y=revenues,
            name="Net Revenue ($)",
            marker_color=NAVY_PRIMARY,
            opacity=0.85,
            hovertemplate="<b>%{x}</b><br>Net Revenue: $%{y:,.2f}<extra></extra>"
        ),
        secondary_y=False
    )

    # Line trace: Completed Orders
    fig.add_trace(
        go.Scatter(
            x=months,
            y=orders,
            name="Completed Orders",
            mode="lines+markers",
            line=dict(color=AMBER_GOLD, width=3),
            marker=dict(size=7, color=AMBER_GOLD),
            hovertemplate="<b>%{x}</b><br>Orders: %{y:,}<extra></extra>"
        ),
        secondary_y=True
    )

    fig.update_layout(
        title=dict(text="<b>Monthly Revenue & Order Velocity</b>", font=dict(size=16, color="#0F172A")),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
        height=380
    )

    fig.update_yaxes(
        title_text="Net Revenue ($)",
        secondary_y=False,
        showgrid=True,
        gridcolor=BORDER_COLOR,
        tickformat="$,.0f"
    )
    fig.update_yaxes(
        title_text="Order Volume",
        secondary_y=True,
        showgrid=False,
        tickformat=",d"
    )
    fig.update_xaxes(showgrid=False, tickangle=-45)

    return fig


def render_category_donut_chart(category_data: List[Dict[str, Any]]) -> go.Figure:
    """
    Generate interactive category gross revenue contribution donut chart.
    """
    if not category_data:
        fig = go.Figure()
        fig.update_layout(title="No Category Data Available")
        return fig

    labels = [d.get("category_name", "Category") for d in category_data]
    values = [float(d.get("gross_revenue", 0.0)) for d in category_data]

    palette = ["#1E3A8A", "#2563EB", "#0284C7", "#059669", "#D97706", "#7C3AED", "#DB2777"]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.55,
                marker=dict(colors=palette),
                textinfo="percent+label",
                hovertemplate="<b>%{label}</b><br>Gross Revenue: $%{value:,.2f}<br>Share: %{percent}<extra></extra>"
            )
        ]
    )

    fig.update_layout(
        title=dict(text="<b>Revenue Share by Product Category</b>", font=dict(size=16, color="#0F172A")),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=50, b=20),
        showlegend=True,
        legend=dict(orientation="v", y=0.5),
        height=350
    )

    return fig


def render_returns_bar_chart(returns_data: List[Dict[str, Any]]) -> go.Figure:
    """
    Generate horizontal bar chart of customer return reasons and associated refund costs.
    """
    if not returns_data:
        fig = go.Figure()
        fig.update_layout(title="No Returns Data Available")
        return fig

    reasons = [d.get("reason", d.get("return_reason", "Reason")) for d in returns_data]
    counts = [int(d.get("incident_count", d.get("return_count", 0))) for d in returns_data]
    refunds = [float(d.get("total_refund_amount", d.get("total_refunds", 0.0))) for d in returns_data]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=reasons,
            x=refunds,
            orientation="h",
            marker_color=ROSE_RED,
            name="Refund Cost ($)",
            text=[f"${r:,.0f} ({c} items)" for r, c in zip(refunds, counts)],
            textposition="auto",
            hovertemplate="<b>%{y}</b><br>Total Refunded: $%{x:,.2f}<extra></extra>"
        )
    )

    fig.update_layout(
        title=dict(text="<b>Refund Capital Leakage by Return Reason</b>", font=dict(size=16, color="#0F172A")),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=150, r=40, t=50, b=40),
        xaxis=dict(title="Total Refund Amount ($)", showgrid=True, gridcolor=BORDER_COLOR, tickformat="$,.0f"),
        yaxis=dict(autorange="reversed"),
        height=320
    )

    return fig


def render_rating_distribution_chart(distribution_data: List[Dict[str, Any]]) -> go.Figure:
    """
    Generate 1 to 5 star rating distribution bar chart with sentiment coloring.
    """
    if not distribution_data:
        fig = go.Figure()
        fig.update_layout(title="No Review Rating Data Available")
        return fig

    ratings = [f"{d.get('rating', i)} Stars" for i, d in enumerate(distribution_data, 1)]
    counts = [int(d.get("review_count", 0)) for d in distribution_data]

    colors = [
        ROSE_RED if "1" in r or "2" in r else
        AMBER_GOLD if "3" in r else
        EMERALD_GREEN
        for r in ratings
    ]

    fig = go.Figure(
        data=[
            go.Bar(
                x=ratings,
                y=counts,
                marker_color=colors,
                text=counts,
                textposition="auto",
                hovertemplate="<b>%{x}</b>: %{y:,} reviews<extra></extra>"
            )
        ]
    )

    fig.update_layout(
        title=dict(text="<b>Customer Rating Distribution (CSAT)</b>", font=dict(size=16, color="#0F172A")),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=40, r=40, t=50, b=40),
        xaxis=dict(title="Rating Bracket"),
        yaxis=dict(title="Review Submissions", showgrid=True, gridcolor=BORDER_COLOR),
        height=320
    )

    return fig


def render_variance_bar_chart(variance_data: List[Dict[str, Any]]) -> go.Figure:
    """
    Generate diverging horizontal bar chart of period percentage changes.
    """
    if not variance_data:
        fig = go.Figure()
        fig.update_layout(title="No Variance Data Available")
        return fig

    metrics = [d.get("metric_name", "") for d in variance_data]
    pcts = [float(d.get("percentage_change", 0.0)) for d in variance_data]
    colors = [EMERALD_GREEN if p >= 0 else ROSE_RED for p in pcts]

    fig = go.Figure(
        data=[
            go.Bar(
                y=metrics,
                x=pcts,
                orientation="h",
                marker_color=colors,
                text=[f"{p:+.1f}%" for p in pcts],
                textposition="auto",
                hovertemplate="<b>%{y}</b>: %{x:+.2f}%<extra></extra>"
            )
        ]
    )

    fig.update_layout(
        title=dict(text="<b>Metric Variance Breakdown (%)</b>", font=dict(size=16, color="#0F172A")),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=150, r=40, t=50, b=40),
        xaxis=dict(title="Percentage Shift (%)", zeroline=True, zerolinecolor="#334155", zerolinewidth=2),
        yaxis=dict(autorange="reversed"),
        height=320
    )

    return fig
