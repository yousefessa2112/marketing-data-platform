from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLEAN_DATA_PATH = PROJECT_ROOT / "data" / "clean_campaign_data.csv"
DASHBOARD_PATH = PROJECT_ROOT / "dashboard" / "marketing_dashboard.html"


def build_dashboard(df: pd.DataFrame) -> go.Figure:
    avg_ctr = float(df["ctr"].mean())
    avg_cpa = float(df["cpa"].replace([float("inf")], 0).mean())

    clicks_by_date = df.groupby("date", as_index=False)["clicks"].sum()
    cost_by_campaign = df.groupby("campaign_id", as_index=False)["cost"].sum().sort_values("cost", ascending=False)

    fig = make_subplots(
        rows=2,
        cols=2,
        specs=[[{"type": "indicator"}, {"type": "indicator"}], [{"type": "xy"}, {"type": "xy"}]],
        subplot_titles=("Average CTR", "Average CPA", "Clicks Trend Over Time", "Campaign Cost"),
        vertical_spacing=0.16,
    )

    fig.add_trace(
        go.Indicator(mode="number", value=avg_ctr, number={"valueformat": ".2%"}, title={"text": "Avg CTR"}),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Indicator(mode="number", value=avg_cpa, number={"prefix": "$", "valueformat": ".2f"}, title={"text": "Avg CPA"}),
        row=1,
        col=2,
    )
    fig.add_trace(
        go.Scatter(x=clicks_by_date["date"], y=clicks_by_date["clicks"], mode="lines", name="Clicks"),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Bar(x=cost_by_campaign["campaign_id"], y=cost_by_campaign["cost"], name="Campaign Cost"),
        row=2,
        col=2,
    )

    fig.update_layout(
        title="Multi-Channel Marketing Performance Dashboard",
        template="plotly_white",
        height=800,
        legend={"orientation": "h", "yanchor": "bottom", "y": -0.15, "xanchor": "center", "x": 0.5},
    )
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Clicks", row=2, col=1)
    fig.update_xaxes(title_text="Campaign", row=2, col=2)
    fig.update_yaxes(title_text="Cost ($)", row=2, col=2)
    return fig


def main() -> None:
    df = pd.read_csv(CLEAN_DATA_PATH)
    DASHBOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    figure = build_dashboard(df)
    figure.write_html(str(DASHBOARD_PATH), include_plotlyjs="cdn")
    print(f"Dashboard generated at: {DASHBOARD_PATH}")


if __name__ == "__main__":
    main()