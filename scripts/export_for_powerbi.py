from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLEAN_DATA_PATH = PROJECT_ROOT / "data" / "clean_campaign_data.csv"
EXPORT_DIR = PROJECT_ROOT / "data" / "powerbi_export"


def export_powerbi_assets(
    clean_data_path: Path = CLEAN_DATA_PATH,
    export_dir: Path = EXPORT_DIR,
) -> dict[str, int]:
    df = pd.read_csv(clean_data_path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    if df["date"].isna().any():
        raise ValueError("Found invalid date values in clean_campaign_data.csv")
    export_dir.mkdir(parents=True, exist_ok=True)

    # Enriched detail table for model relationships and drill-through.
    df["channel_type"] = df["campaign_id"].astype(str).str.extract(r"^([A-Za-z]+)")[0].str.lower().map(
        {
            "social": "Social",
            "search": "Search",
            "display": "Display",
            "email": "Email",
        }
    ).fillna("Other")
    df["day_of_week"] = df["date"].dt.day_name()
    df["month_name"] = df["date"].dt.month_name()
    df["week_number"] = df["date"].dt.isocalendar().week.astype(int)
    df["quarter"] = "Q" + df["date"].dt.quarter.astype(str)
    df["ctr"] = df["clicks"] / df["impressions"]
    df["performance_tier"] = pd.cut(
        df["ctr"],
        bins=[-float("inf"), 0.01, 0.03, float("inf")],
        labels=["Low", "Medium", "High"],
        right=True,
    ).astype(str)

    detail_path = export_dir / "campaign_daily_detail.csv"
    df.to_csv(detail_path, index=False)

    # Pre-aggregated summary table for faster visuals.
    daily_perf = (
        df.groupby(["campaign_id", "date"], as_index=False)
        .agg(clicks=("clicks", "sum"), impressions=("impressions", "sum"))
        .assign(daily_ctr=lambda x: x["clicks"] / x["impressions"])
    )
    best_days = (
        daily_perf.sort_values(["campaign_id", "daily_ctr", "date"], ascending=[True, False, True])
        .groupby("campaign_id", as_index=False)
        .first()[["campaign_id", "date"]]
        .rename(columns={"date": "best_day"})
    )
    worst_days = (
        daily_perf.sort_values(["campaign_id", "daily_ctr", "date"], ascending=[True, True, True])
        .groupby("campaign_id", as_index=False)
        .first()[["campaign_id", "date"]]
        .rename(columns={"date": "worst_day"})
    )

    summary = (
        df.groupby("campaign_id", as_index=False)
        .agg(
            total_impressions=("impressions", "sum"),
            total_clicks=("clicks", "sum"),
            total_cost=("cost", "sum"),
            total_conversions=("conversions", "sum"),
        )
        .assign(
            avg_ctr=lambda x: x["total_clicks"] / x["total_impressions"],
            avg_cpc=lambda x: x["total_cost"] / x["total_clicks"],
            avg_cpa=lambda x: x["total_cost"] / x["total_conversions"],
        )
        .merge(best_days, on="campaign_id", how="left")
        .merge(worst_days, on="campaign_id", how="left")
        .assign(
            best_day=lambda x: pd.to_datetime(x["best_day"]).dt.day_name(),
            worst_day=lambda x: pd.to_datetime(x["worst_day"]).dt.day_name(),
        )
        .round({"total_cost": 2, "avg_ctr": 6, "avg_cpc": 4, "avg_cpa": 4})
        .sort_values("total_cost", ascending=False)
    )
    summary_path = export_dir / "campaign_summary.csv"
    summary.to_csv(summary_path, index=False)

    # Monthly trends with month-over-month click growth per campaign.
    monthly_trends = (
        df.assign(month=df["date"].dt.to_period("M").dt.to_timestamp())
        .groupby(["month", "campaign_id"], as_index=False)
        .agg(
            total_impressions=("impressions", "sum"),
            total_clicks=("clicks", "sum"),
            total_cost=("cost", "sum"),
            total_conversions=("conversions", "sum"),
        )
        .sort_values(["campaign_id", "month"])
        .assign(
            avg_ctr=lambda x: x["total_clicks"] / x["total_impressions"],
            avg_cpa=lambda x: x["total_cost"] / x["total_conversions"],
            mom_click_growth_pct=lambda x: x.groupby("campaign_id")["total_clicks"].pct_change() * 100,
        )
        .round({"total_cost": 2, "avg_ctr": 6, "avg_cpa": 4, "mom_click_growth_pct": 2})
    )
    monthly_trends_path = export_dir / "monthly_trends.csv"
    monthly_trends.to_csv(monthly_trends_path, index=False)

    # Excel workbook with multiple tabs for Power BI import convenience.
    excel_path = export_dir / "powerbi_ready_tables.xlsx"
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="campaign_daily_detail", index=False)
        summary.to_excel(writer, sheet_name="campaign_summary", index=False)
        monthly_trends.to_excel(writer, sheet_name="monthly_trends", index=False)

    return {
        "detail_rows": int(len(df)),
        "summary_rows": int(len(summary)),
        "monthly_rows": int(len(monthly_trends)),
    }


def main() -> None:
    stats = export_powerbi_assets()
    print(f"Power BI exports created under: {EXPORT_DIR}")
    print(
        "Rows exported - "
        f"detail: {stats['detail_rows']}, "
        f"summary: {stats['summary_rows']}, "
        f"monthly: {stats['monthly_rows']}"
    )


if __name__ == "__main__":
    main()