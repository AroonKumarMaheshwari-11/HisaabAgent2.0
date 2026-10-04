"""
Plotly figure builders. All charts share a common light-theme layout so
they look consistent across pages.
"""

import plotly.graph_objects as go

from config import COLORS


def _base_layout(title: str = None, height: int = 320) -> dict:
    return dict(
        title=dict(text=title, font=dict(size=15, color=COLORS["text_primary"],
                                          family="Inter, sans-serif")) if title else None,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=COLORS["text_muted"], size=12),
        margin=dict(l=10, r=10, t=45 if title else 15, b=10),
        height=height,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(color=COLORS["text_primary"])),
        xaxis=dict(gridcolor=COLORS["border"], showgrid=False,
                   color=COLORS["text_muted"], linecolor=COLORS["border"]),
        yaxis=dict(gridcolor=COLORS["border"], showgrid=True,
                   color=COLORS["text_muted"], zeroline=False),
        hoverlabel=dict(bgcolor=COLORS["bg_card"], bordercolor=COLORS["border"],
                        font=dict(color=COLORS["text_primary"], family="Inter, sans-serif")),
    )


def revenue_expense_trend(days: list, revenue: list, expenses: list) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=days, y=revenue, mode="lines+markers", name="Revenue",
        line=dict(color=COLORS["accent_primary"], width=3),
        marker=dict(size=6),
        hovertemplate="%{x}<br>Revenue: \u20a8%{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=days, y=expenses, mode="lines+markers", name="Expenses",
        line=dict(color=COLORS["accent_red"], width=3),
        marker=dict(size=6),
        hovertemplate="%{x}<br>Expenses: \u20a8%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(**_base_layout("Revenue vs Expenses"))
    return fig


def top_products_bar(products: list) -> go.Figure:
    names = [p["product"] for p in products]
    revenue = [p["revenue"] for p in products]
    fig = go.Figure(go.Bar(
        x=revenue, y=names, orientation="h",
        marker=dict(color=COLORS["accent_primary"]),
        hovertemplate="%{y}<br>Revenue: \u20a8%{x:,.0f}<extra></extra>",
    ))
    fig.update_layout(**_base_layout("Top Products by Revenue"))
    fig.update_yaxes(autorange="reversed")
    return fig


def expense_breakdown_pie(breakdown: list) -> go.Figure:
    labels = [b["category"] for b in breakdown]
    values = [b["amount"] for b in breakdown]
    palette = [COLORS["accent_primary"], COLORS["accent_gold"], COLORS["accent_blue"],
               COLORS["accent_amber"], COLORS["accent_red"], "#2E9E6B", "#5B7FBF"]
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.55,
        marker=dict(colors=palette[:len(labels)], line=dict(color=COLORS["bg_card"], width=2)),
        textfont=dict(color="#FFFFFF"),
        hovertemplate="%{label}<br>\u20a8%{value:,.0f} (%{percent})<extra></extra>",
    ))
    fig.update_layout(**_base_layout("Expense Breakdown"))
    return fig


def receivables_vs_payables_bar(total_receivables: int, total_payables: int) -> go.Figure:
    fig = go.Figure(go.Bar(
        x=["Receivables", "Payables"], y=[total_receivables, total_payables],
        marker=dict(color=[COLORS["accent_primary"], COLORS["accent_red"]]),
        hovertemplate="%{x}: \u20a8%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(**_base_layout("Receivables vs Payables"))
    return fig


def cash_flow_trend(days: list, revenue: list, expenses: list) -> go.Figure:
    net = [r - e for r, e in zip(revenue, expenses)]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=days, y=net, name="Net Cash Flow",
        marker=dict(color=[COLORS["accent_primary"] if v >= 0 else COLORS["accent_red"] for v in net]),
        hovertemplate="%{x}<br>Net: \u20a8%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(**_base_layout("Daily Net Cash Flow"))
    return fig