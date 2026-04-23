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
    export_dir.mkdir(parents=True, exist_ok=True)

    # Detail table for model relationships and drill-through.
    detail_path = export_dir / "campaign_daily_detail.csv"
    df.to_csv(detail_path, index=False)

    # Pre-aggregated summary table for faster visuals.
    summary = (
        df.groupby("campaign_id", as_index=False)
        .agg(
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            cost=("cost", "sum"),
            conversions=("conversions", "sum"),
        )
        .assign(
            ctr=lambda x: x["clicks"] / x["impressions"],
            cpc=lambda x: x["cost"] / x["clicks"],
            cpa=lambda x: x["cost"] / x["conversions"],
        )
        .round({"cost": 2, "ctr": 6, "cpc": 4, "cpa": 4})
        .sort_values("cost", ascending=False)
    )
    summary_path = export_dir / "campaign_summary.csv"
    summary.to_csv(summary_path, index=False)

    # Excel workbook with multiple tabs for Power BI import convenience.
    excel_path = export_dir / "powerbi_ready_tables.xlsx"
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="campaign_daily_detail", index=False)
        summary.to_excel(writer, sheet_name="campaign_summary", index=False)

    return {
        "detail_rows": int(len(df)),
        "summary_rows": int(len(summary)),
    }


def main() -> None:
    stats = export_powerbi_assets()
    print(f"Power BI exports created under: {EXPORT_DIR}")
    print(f"Rows exported - detail: {stats['detail_rows']}, summary: {stats['summary_rows']}")


if __name__ == "__main__":
    main()