"""Plotly chart builders for the SpamShield AI dashboard."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .helpers import CATEGORY_COLOR


def confidence_bar(scores: dict[str, float]) -> go.Figure:
    cats = list(scores.keys())
    vals = [scores[c] for c in cats]
    colors = [CATEGORY_COLOR.get(c, "#888") for c in cats]
    fig = go.Figure(
        go.Bar(x=vals, y=cats, orientation="h", marker_color=colors,
               text=[f"{v:.0f}%" for v in vals], textposition="outside")
    )
    fig.update_layout(
        template="plotly_dark", height=260, margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(range=[0, 100], showgrid=False),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def category_pie(history: list[dict]) -> go.Figure:
    if not history:
        return go.Figure()
    df = pd.DataFrame(history)
    counts = df["category"].value_counts().reset_index()
    counts.columns = ["category", "count"]
    fig = px.pie(
        counts, names="category", values="count", hole=0.55,
        color="category", color_discrete_map=CATEGORY_COLOR,
    )
    fig.update_layout(
        template="plotly_dark", height=320, margin=dict(l=0, r=0, t=10, b=10),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def keyword_bar(history: list[dict]) -> go.Figure:
    words: dict[str, int] = {}
    for h in history:
        for k in h.get("suspicious_keywords", []):
            words[k] = words.get(k, 0) + 1
    if not words:
        return go.Figure()
    df = pd.DataFrame(sorted(words.items(), key=lambda x: x[1], reverse=True)[:10],
                      columns=["keyword", "count"])
    fig = px.bar(df, x="count", y="keyword", orientation="h",
                 color_discrete_sequence=["#FF5A6E"])
    fig.update_layout(
        template="plotly_dark", height=320, margin=dict(l=10, r=10, t=10, b=10),
        yaxis=dict(autorange="reversed"),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def timeline(history: list[dict]) -> go.Figure:
    if not history:
        return go.Figure()
    df = pd.DataFrame(history)
    df["date"] = pd.to_datetime(df["timestamp"]).dt.date
    df["is_threat"] = df["category"].isin(["Spam", "Scam"])
    grouped = df.groupby("date").agg(
        threats=("is_threat", "sum"),
        safe=("is_threat", lambda s: (~s).sum()),
    ).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=grouped["date"], y=grouped["threats"], name="Threats",
                             mode="lines+markers", line=dict(color="#FF5A6E", width=3)))
    fig.add_trace(go.Scatter(x=grouped["date"], y=grouped["safe"], name="Safe",
                             mode="lines+markers", line=dict(color="#39E6A0", width=3)))
    fig.update_layout(
        template="plotly_dark", height=300, margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig
