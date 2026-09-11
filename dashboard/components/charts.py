"""
Nova Chart Engine — High-fidelity Altair visualizations for ECDAT.
"""
import math
from typing import Any

import altair as alt
import pandas as pd

from .theme import RISK_COLORS, THEME


def configure_nova_chart(chart: alt.Chart, height: int = 300) -> alt.Chart:
    """Apply Nova deep-space chart configuration."""
    return chart.configure(
        background="transparent",
        axis=alt.AxisConfig(
            labelFont="Plus Jakarta Sans",
            titleFont="Plus Jakarta Sans",
            labelColor=THEME["text_muted"],
            titleColor=THEME["text_dim"],
            gridColor="rgba(255, 255, 255, 0.05)",
            domainColor="rgba(255, 255, 255, 0.1)",
            tickColor="rgba(255, 255, 255, 0.1)",
            labelFontSize=10,
            titleFontSize=11,
        ),
        legend=alt.LegendConfig(
            labelFont="Plus Jakarta Sans",
            titleFont="Plus Jakarta Sans",
            labelColor=THEME["text_muted"],
            titleColor=THEME["text_dim"],
            orient="bottom",
            labelFontSize=10,
        ),
        view=alt.ViewConfig(stroke=None),
    ).properties(height=height)

def donut_chart(data: dict[str, int], height: int = 240) -> alt.Chart:
    """Nova-styled donut chart (aliased for compatibility)."""
    rows = [
        ("Safe", data.get("Safe", 0), RISK_COLORS["safe"]),
        ("Partial", data.get("Partial", 0), RISK_COLORS["partial"]),
        ("Vulnerable", data.get("Vulnerable", 0), RISK_COLORS["vulnerable"]),
        ("Critical", data.get("Critical", 0), RISK_COLORS["critical"]),
    ]
    rows = [r for r in rows if r[1] > 0] or [("No data", 1, THEME["text_dim"])]
    total = sum(r[1] for r in rows)

    # Angles are precomputed because Vega-Lite's implicit theta stack derives
    # value_start/value_end fields that multiply its console warnings per render.
    records = []
    acc = 0.0
    for label, value, color in rows:
        start = acc / total * 2 * math.pi
        acc += value
        # A full-circle arc renders as a degenerate zero-area path, so stop short.
        end = min(acc / total * 2 * math.pi, 2 * math.pi - 1e-3)
        records.append({
            "label": label,
            "value": value,
            "color": color,
            "start": start,
            "end": end,
        })
    df = pd.DataFrame(records)

    chart = alt.Chart(df).mark_arc(
        innerRadius=70,
        outerRadius=100,
        cornerRadius=10,
        stroke=THEME["bg_card"],
        strokeWidth=2,
    ).encode(
        theta=alt.Theta("start:Q", stack=None, scale=alt.Scale(domain=[0, 2 * math.pi])),
        theta2=alt.Theta2("end:Q"),
        color=alt.Color("label:N", scale=alt.Scale(domain=df["label"].tolist(), range=df["color"].tolist()), legend=None),
        tooltip=["label:N", "value:Q"]
    )

    return configure_nova_chart(chart, height)

def horizontal_bar_chart(data: list[dict[str, Any]], x_field: str, y_field: str, color: str | None = None, height: int = 280, x_title: str | None = None) -> alt.Chart:
    """Nova-styled horizontal bar chart (aliased for compatibility)."""
    df = pd.DataFrame(data)
    bar_color = color or THEME["neon_blue"]
    
    chart = alt.Chart(df).mark_bar(
        cornerRadiusEnd=8,
        height=20,
        color=bar_color,
        opacity=0.8
    ).encode(
        y=alt.Y(f"{y_field}:N", sort="-x", title=None),
        x=alt.X(f"{x_field}:Q", stack=None, title=x_title),
        tooltip=[y_field, x_field]
    )
    
    return configure_nova_chart(chart, height)

# Aliases for newer code if any
nova_donut = donut_chart
nova_bar = horizontal_bar_chart
