from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLEAN_DATA_PATH = PROJECT_ROOT / "data" / "clean_campaign_data.csv"
QUALITY_REPORT_PATH = PROJECT_ROOT / "data" / "quality_report.txt"
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw_campaign_data.csv"


def run_data_quality_checks(
    clean_data_path: Path = CLEAN_DATA_PATH,
    report_path: Path = QUALITY_REPORT_PATH,
    raw_data_path: Path = RAW_DATA_PATH,
) -> tuple[bool, list[dict[str, str]]]:
    clean_df = pd.read_csv(clean_data_path)
    raw_df = pd.read_csv(raw_data_path)

    checks: list[dict[str, str]] = []

    def add_check(name: str, passed: bool, details: str) -> None:
        checks.append(
            {
                "check": name,
                "status": "PASS" if passed else "FAIL",
                "details": details,
            }
        )

    null_total = int(clean_df.isnull().sum().sum())
    add_check("Null checks", null_total == 0, f"null_cells={null_total}")

    ctr_valid = bool(((clean_df["ctr"] >= 0) & (clean_df["ctr"] <= 1)).all())
    add_check("CTR range validation", ctr_valid, "expected 0 <= ctr <= 1")

    cpc_valid = bool((clean_df["cpc"] > 0).all())
    add_check("CPC positive validation", cpc_valid, "expected cpc > 0")

    duplicate_count = int(clean_df.duplicated(subset=["date", "campaign_id"]).sum())
    add_check("Duplicate detection", duplicate_count == 0, f"duplicates={duplicate_count}")

    required_columns = ["date", "campaign_id", "impressions", "clicks", "cost", "conversions", "ctr", "cpc", "cpa"]
    completeness_ok = bool(clean_df[required_columns].notnull().all().all())
    add_check("Completeness checks", completeness_ok, "all required columns present and non-null")

    row_count_ok = len(clean_df) <= len(raw_df) and len(clean_df) > 0
    add_check(
        "Row count validation",
        row_count_ok,
        f"clean_rows={len(clean_df)}, raw_rows={len(raw_df)}",
    )

    all_passed = all(c["status"] == "PASS" for c in checks)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8") as f:
        f.write("Marketing Data Platform - Data Quality Report\n")
        f.write("=" * 52 + "\n")
        for c in checks:
            f.write(f"{c['status']}: {c['check']} | {c['details']}\n")
        f.write("-" * 52 + "\n")
        f.write(f"OVERALL STATUS: {'PASS' if all_passed else 'FAIL'}\n")

    return all_passed, checks


def main() -> None:
    passed, checks = run_data_quality_checks()
    print(f"Data quality overall status: {'PASS' if passed else 'FAIL'}")
    print(f"Checks executed: {len(checks)}")
    print(f"Report path: {QUALITY_REPORT_PATH}")


if __name__ == "__main__":
    main()