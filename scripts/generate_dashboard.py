from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLEAN_DATA_PATH = PROJECT_ROOT / "data" / "clean_campaign_data.csv"
DASHBOARD_DIR = PROJECT_ROOT / "dashboard"
BRAND_DARK = "#1B2A4A"
BRAND_BLUE = "#3B82F6"
CHANNEL_COLORS = {
    "Search": "#3B82F6",
    "Social": "#22C55E",
    "Display": "#F59E0B",
    "Email": "#A855F7",
}


def _prepare_data() -> pd.DataFrame:
    df = pd.read_csv(CLEAN_DATA_PATH)
    df["date"] = pd.to_datetime(df["date"])
    df["channel"] = df["campaign_id"].str.split("_").str[0]
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["week"] = df["date"].dt.to_period("W").astype(str)
    df["dow"] = df["date"].dt.day_name()
    return df


def _styled_html_page(title: str, subtitle: str, sections: list[str]) -> str:
    body = "\n".join(sections)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <style>
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
      background: #f5f7fb;
      color: #1f2937;
    }}
    .header {{
      background: {BRAND_DARK};
      color: white;
      padding: 22px 34px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
    }}
    .header h1 {{
      margin: 0;
      font-size: 28px;
    }}
    .header p {{
      margin: 6px 0 0;
      opacity: 0.9;
    }}
    .container {{
      padding: 24px;
      max-width: 1400px;
      margin: 0 auto;
    }}
    .section {{
      background: white;
      border-radius: 12px;
      margin-bottom: 20px;
      padding: 12px;
      box-shadow: 0 3px 14px rgba(27, 42, 74, 0.08);
    }}
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(170px, 1fr));
      gap: 14px;
      margin-bottom: 20px;
    }}
    .kpi-card {{
      background: white;
      border: 1px solid #e7edf5;
      border-left: 5px solid {BRAND_BLUE};
      border-radius: 10px;
      padding: 16px;
      box-shadow: 0 2px 8px rgba(59, 130, 246, 0.08);
    }}
    .kpi-label {{
      color: #6b7280;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    .kpi-value {{
      margin-top: 6px;
      font-size: 24px;
      font-weight: 700;
      color: {BRAND_DARK};
    }}
    .channel-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(240px, 1fr));
      gap: 14px;
      margin-bottom: 20px;
    }}
    .channel-card {{
      border: 1px solid #e6ecf6;
      border-radius: 10px;
      padding: 14px;
      background: #fbfdff;
    }}
    .channel-title {{
      margin: 0 0 8px;
      color: {BRAND_DARK};
      font-size: 18px;
      font-weight: 700;
    }}
    .channel-metrics {{
      font-size: 14px;
      line-height: 1.7;
      color: #374151;
    }}
    .hub-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
      gap: 18px;
      margin-top: 20px;
    }}
    .hub-card {{
      background: white;
      border: 1px solid #e4ebf5;
      border-radius: 12px;
      padding: 18px;
      box-shadow: 0 3px 12px rgba(27, 42, 74, 0.08);
    }}
    .hub-card h3 {{
      margin: 0 0 8px;
      color: {BRAND_DARK};
    }}
    .hub-card p {{
      margin: 0 0 14px;
      color: #4b5563;
      font-size: 14px;
      line-height: 1.5;
    }}
    .hub-card a {{
      display: inline-block;
      text-decoration: none;
      background: {BRAND_BLUE};
      color: white;
      padding: 8px 12px;
      border-radius: 8px;
      font-weight: 600;
      font-size: 14px;
    }}
  </style>
</head>
<body>
  <div class="header">
    <h1>{title}</h1>
    <p>{subtitle}</p>
  </div>
  <div class="container">
    {body}
  </div>
</body>
</html>
"""

def _to_html_fragment(fig: go.Figure) -> str:
    fig.update_layout(template="plotly_white")
    return fig.to_html(full_html=False, include_plotlyjs="cdn")


def build_marketing_dashboard(df: pd.DataFrame) -> str:
    kpis = {
        "Total Spend": f"${df['cost'].sum():,.0f}",
        "Total Conversions": f"{int(df['conversions'].sum()):,}",
        "Avg CTR": f"{df['ctr'].mean() * 100:.2f}%",
        "Avg CPA": f"${df['cpa'].replace([float('inf')], 0).mean():.2f}",
    }
    kpi_html = "".join(
        f'<div class="kpi-card"><div class="kpi-label">{k}</div><div class="kpi-value">{v}</div></div>' for k, v in kpis.items()
    )

    daily = df.groupby(["date", "channel"], as_index=False)["clicks"].sum()
    fig_daily = px.line(
        daily,
        x="date",
        y="clicks",
        color="channel",
        title="Daily Clicks Trend by Channel",
        labels={"date": "Date", "clicks": "Clicks", "channel": "Channel"},
        color_discrete_map=CHANNEL_COLORS,
    )

    spend_campaign = df.groupby("campaign_id", as_index=False)["cost"].sum().sort_values("cost", ascending=False)
    fig_spend_campaign = px.bar(
        spend_campaign,
        x="campaign_id",
        y="cost",
        title="Total Spend by Campaign",
        labels={"campaign_id": "Campaign", "cost": "Spend ($)"},
        color="campaign_id",
    )
    fig_spend_campaign.update_layout(showlegend=False)

    return _styled_html_page(
        "Marketing Dashboard - Executive Overview",
        "Executive KPIs and channel/campaign performance trends",
        [
            f'<div class="kpi-grid">{kpi_html}</div>',
            f'<div class="section">{_to_html_fragment(fig_daily)}</div>',
            f'<div class="section">{_to_html_fragment(fig_spend_campaign)}</div>',
        ],
    )


def build_channel_performance_dashboard(df: pd.DataFrame) -> str:
    channel_stats = df.groupby("channel", as_index=False).agg(
        spend=("cost", "sum"),
        clicks=("clicks", "sum"),
        conversions=("conversions", "sum"),
    )
    channel_stats["ctr"] = channel_stats["clicks"] / df.groupby("channel")["impressions"].sum().values
    channel_stats["cpa"] = channel_stats["spend"] / channel_stats["conversions"]
    cards = []
    for row in channel_stats.sort_values("spend", ascending=False).itertuples(index=False):
        cards.append(
            f"""<div class="channel-card">
<h3 class="channel-title">{row.channel}</h3>
<div class="channel-metrics">
Spend: ${row.spend:,.0f}<br/>Clicks: {int(row.clicks):,}<br/>Conversions: {int(row.conversions):,}<br/>
CTR: {row.ctr * 100:.2f}%<br/>CPA: ${row.cpa:.2f}
</div></div>"""
        )

    monthly = df.groupby(["month", "channel"], as_index=False).agg(
        spend=("cost", "sum"), clicks=("clicks", "sum"), impressions=("impressions", "sum"), conversions=("conversions", "sum")
    )
    monthly["ctr"] = monthly["clicks"] / monthly["impressions"]
    conv_share = df.groupby("channel", as_index=False)["conversions"].sum()

    fig_stacked = px.bar(
        monthly,
        x="month",
        y="spend",
        color="channel",
        barmode="stack",
        title="Monthly Spend Breakdown by Channel",
        labels={"month": "Month", "spend": "Spend ($)", "channel": "Channel"},
        color_discrete_map=CHANNEL_COLORS,
    )
    fig_grouped_ctr = px.bar(
        monthly,
        x="month",
        y="ctr",
        color="channel",
        barmode="group",
        title="CTR Comparison by Channel per Month",
        labels={"month": "Month", "ctr": "CTR", "channel": "Channel"},
        color_discrete_map=CHANNEL_COLORS,
    )
    fig_grouped_ctr.update_yaxes(tickformat=".1%")
    fig_pie = px.pie(
        conv_share,
        names="channel",
        values="conversions",
        title="Share of Total Conversions by Channel",
        color="channel",
        color_discrete_map=CHANNEL_COLORS,
    )

    return _styled_html_page(
        "Channel Performance - Deep Dive",
        "Granular KPI views and monthly behavior by marketing channel",
        [
            f'<div class="channel-grid">{"".join(cards)}</div>',
            f'<div class="section">{_to_html_fragment(fig_stacked)}</div>',
            f'<div class="section">{_to_html_fragment(fig_grouped_ctr)}</div>',
            f'<div class="section">{_to_html_fragment(fig_pie)}</div>',
        ],
    )


def build_trends_dashboard(df: pd.DataFrame) -> str:
    weekly = df.groupby(["week", "channel"], as_index=False)["clicks"].sum()
    fig_weekly = px.line(
        weekly,
        x="week",
        y="clicks",
        color="channel",
        title="Weekly Clicks Trend per Channel",
        labels={"week": "Week", "clicks": "Clicks", "channel": "Channel"},
        color_discrete_map=CHANNEL_COLORS,
    )

    heat = df.groupby(["dow", "channel"], as_index=False)["clicks"].mean()
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    heat["dow"] = pd.Categorical(heat["dow"], categories=dow_order, ordered=True)
    heat = heat.sort_values("dow")
    fig_heat = px.density_heatmap(
        heat,
        x="channel",
        y="dow",
        z="clicks",
        histfunc="avg",
        title="Average Clicks by Day of Week and Channel",
        labels={"channel": "Channel", "dow": "Day of Week", "clicks": "Avg Clicks"},
        color_continuous_scale="Blues",
    )

    daily_channel = df.groupby(["date", "channel"], as_index=False).agg(clicks=("clicks", "sum"), impressions=("impressions", "sum"))
    daily_channel["ctr"] = daily_channel["clicks"] / daily_channel["impressions"]
    daily_channel = daily_channel.sort_values("date")
    daily_channel["ctr_rolling_7d"] = daily_channel.groupby("channel")["ctr"].transform(lambda s: s.rolling(7, min_periods=1).mean())
    fig_rolling_ctr = px.line(
        daily_channel,
        x="date",
        y="ctr_rolling_7d",
        color="channel",
        title="Rolling 7-Day Average CTR by Channel",
        labels={"date": "Date", "ctr_rolling_7d": "7D Avg CTR", "channel": "Channel"},
        color_discrete_map=CHANNEL_COLORS,
    )
    fig_rolling_ctr.update_yaxes(tickformat=".2%")

    spend_daily = df.groupby(["date", "channel"], as_index=False)["cost"].sum().sort_values("date")
    spend_daily["cumulative_spend"] = spend_daily.groupby("channel")["cost"].cumsum()
    fig_cumulative = px.area(
        spend_daily,
        x="date",
        y="cumulative_spend",
        color="channel",
        title="Cumulative Spend Over Time by Channel",
        labels={"date": "Date", "cumulative_spend": "Cumulative Spend ($)", "channel": "Channel"},
        color_discrete_map=CHANNEL_COLORS,
    )

    return _styled_html_page(
        "Trends & Patterns Analysis",
        "Temporal trends, seasonality, and momentum indicators",
        [
            f'<div class="section">{_to_html_fragment(fig_weekly)}</div>',
            f'<div class="section">{_to_html_fragment(fig_heat)}</div>',
            f'<div class="section">{_to_html_fragment(fig_rolling_ctr)}</div>',
            f'<div class="section">{_to_html_fragment(fig_cumulative)}</div>',
        ],
    )


def build_efficiency_dashboard(df: pd.DataFrame) -> str:
    campaign = df.groupby(["campaign_id", "channel"], as_index=False).agg(
        spend=("cost", "sum"), clicks=("clicks", "sum"), conversions=("conversions", "sum"), impressions=("impressions", "sum")
    )
    campaign["ctr"] = campaign["clicks"] / campaign["impressions"]
    campaign["cpa"] = campaign["spend"] / campaign["conversions"]
    fig_scatter = px.scatter(
        campaign,
        x="ctr",
        y="cpa",
        size="spend",
        color="channel",
        hover_name="campaign_id",
        title="CPA vs CTR by Campaign (Bubble Size = Total Spend)",
        labels={"ctr": "CTR", "cpa": "CPA ($)", "channel": "Channel"},
        color_discrete_map=CHANNEL_COLORS,
        size_max=60,
    )
    fig_scatter.update_xaxes(tickformat=".2%")

    channel_rank = df.groupby("channel", as_index=False).agg(spend=("cost", "sum"), conversions=("conversions", "sum"))
    channel_rank["cpa"] = channel_rank["spend"] / channel_rank["conversions"]
    channel_rank = channel_rank.sort_values("cpa")
    fig_rank = px.bar(
        channel_rank,
        x="channel",
        y="cpa",
        color="channel",
        title="CPA by Channel (Best to Worst)",
        labels={"channel": "Channel", "cpa": "CPA ($)"},
        color_discrete_map=CHANNEL_COLORS,
    )
    fig_rank.update_layout(showlegend=False)

    daily = df.groupby("date", as_index=False).agg(spend=("cost", "sum"), conversions=("conversions", "sum"))
    daily["cpa"] = daily["spend"] / daily["conversions"]
    top_days = daily.sort_values(["conversions", "cpa"], ascending=[False, True]).head(10)
    table = go.Figure(
        data=[
            go.Table(
                header=dict(values=["Date", "Conversions", "CPA ($)"], fill_color=BRAND_DARK, font=dict(color="white"), align="left"),
                cells=dict(
                    values=[top_days["date"].dt.strftime("%Y-%m-%d"), top_days["conversions"], top_days["cpa"].round(2)],
                    fill_color="#f8fbff",
                    align="left",
                ),
            )
        ]
    )
    table.update_layout(title="Top 10 Best Performing Days")

    monthly = df.groupby(["month", "channel"], as_index=False).agg(spend=("cost", "sum"), conversions=("conversions", "sum"))
    monthly["cpa"] = monthly["spend"] / monthly["conversions"]
    fig_mom = px.line(
        monthly.sort_values("month"),
        x="month",
        y="cpa",
        color="channel",
        markers=True,
        title="Month-over-Month CPA Trend by Channel",
        labels={"month": "Month", "cpa": "CPA ($)", "channel": "Channel"},
        color_discrete_map=CHANNEL_COLORS,
    )

    return _styled_html_page(
        "Cost Efficiency Report",
        "Acquisition efficiency, channel ranking, and CPA trend diagnostics",
        [
            f'<div class="section">{_to_html_fragment(fig_scatter)}</div>',
            f'<div class="section">{_to_html_fragment(fig_rank)}</div>',
            f'<div class="section">{_to_html_fragment(table)}</div>',
            f'<div class="section">{_to_html_fragment(fig_mom)}</div>',
        ],
    )


def build_index_dashboard() -> str:
    cards = [
        ("Executive Overview", "marketing_dashboard.html", "High-level KPIs, clicks trend by channel, and campaign spend comparison."),
        ("Channel Deep Dive", "channel_performance.html", "Channel-level KPI cards, monthly spend stacks, CTR comparisons, and conversion share."),
        ("Trends & Patterns", "trends_analysis.html", "Weekly trends, day-of-week heatmap, rolling CTR, and cumulative spend trajectories."),
        ("Cost Efficiency", "efficiency_report.html", "CPA/CTR campaign scatter, channel ranking, top days table, and MoM CPA trends."),
    ]
    card_html = "".join(
        f"""<div class="hub-card"><h3>{name}</h3><p>{desc}</p><a href="{path}">Open Dashboard</a></div>"""
        for name, path, desc in cards
    )
    return _styled_html_page(
        "Marketing Data Platform - Dashboard Hub",
        "Navigate all interactive performance dashboards from one place",
        [f'<div class="hub-grid">{card_html}</div>'],
    )


def main() -> None:
    df = _prepare_data()
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)

    outputs = {
        "marketing_dashboard.html": build_marketing_dashboard(df),
        "channel_performance.html": build_channel_performance_dashboard(df),
        "trends_analysis.html": build_trends_dashboard(df),
        "efficiency_report.html": build_efficiency_dashboard(df),
        "index.html": build_index_dashboard(),
    }
    for filename, html in outputs.items():
        out_path = DASHBOARD_DIR / filename
        out_path.write_text(html, encoding="utf-8")
        print(f"Dashboard generated at: {out_path}")


if __name__ == "__main__":
    main()