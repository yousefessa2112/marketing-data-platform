from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from scripts.clean_data import clean_data, safe_divide
from scripts.data_quality import run_data_quality_checks
from scripts.export_for_powerbi import export_powerbi_assets
from scripts.generate_data import build_synthetic_dataset
from scripts.load_data import TABLE_NAME, load_data


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SQL_ANALYSIS_PATH = PROJECT_ROOT / "sql" / "analysis.sql"
SQL_ADVANCED_PATH = PROJECT_ROOT / "sql" / "advanced_analysis.sql"
SQL_MODELS_PATH = PROJECT_ROOT / "sql" / "data_models.sql"


def _write_raw_csv(tmp_path: Path) -> Path:
    raw_path = tmp_path / "raw_campaign_data.csv"
    df = build_synthetic_dataset()
    df.to_csv(raw_path, index=False)
    return raw_path


def test_safe_divide_handles_zero_denominator() -> None:
    numerator = pd.Series([10, 5, 0])
    denominator = pd.Series([2, 0, 0])
    result = safe_divide(numerator, denominator)
    assert result.tolist() == [5.0, 0.0, 0.0]


def test_clean_data_creates_expected_columns(tmp_path: Path) -> None:
    raw_path = _write_raw_csv(tmp_path)
    clean_path = tmp_path / "clean_campaign_data.csv"
    cleaned = clean_data(raw_path, clean_path)
    expected_cols = {"campaign_id", "date", "impressions", "clicks", "cost", "conversions", "ctr", "cpc", "cpa"}
    assert expected_cols.issubset(set(cleaned.columns))
    assert len(cleaned) > 0
    assert clean_path.exists()


def test_clean_data_enforces_metric_ranges(tmp_path: Path) -> None:
    raw_path = _write_raw_csv(tmp_path)
    clean_path = tmp_path / "clean_campaign_data.csv"
    cleaned = clean_data(raw_path, clean_path)
    assert ((cleaned["ctr"] >= 0) & (cleaned["ctr"] <= 1)).all()
    assert (cleaned["cpc"] >= 0).all()
    assert (cleaned["cpa"] >= 0).all()


def test_load_data_writes_rows_to_sqlite(tmp_path: Path) -> None:
    raw_path = _write_raw_csv(tmp_path)
    clean_path = tmp_path / "clean_campaign_data.csv"
    db_path = tmp_path / "marketing.db"
    cleaned = clean_data(raw_path, clean_path)
    row_count = load_data(clean_path, db_path)
    assert row_count == len(cleaned)
    with sqlite3.connect(db_path) as conn:
        db_rows = conn.execute(f"SELECT COUNT(*) FROM {TABLE_NAME};").fetchone()[0]
    assert db_rows == row_count


def test_data_quality_checks_pass_on_clean_dataset(tmp_path: Path) -> None:
    raw_path = _write_raw_csv(tmp_path)
    clean_path = tmp_path / "clean_campaign_data.csv"
    report_path = tmp_path / "quality_report.txt"
    clean_data(raw_path, clean_path)
    passed, checks = run_data_quality_checks(clean_path, report_path, raw_path)
    assert passed is True
    assert len(checks) >= 6
    assert report_path.exists()


def test_sql_queries_return_expected_structure(tmp_path: Path) -> None:
    raw_path = _write_raw_csv(tmp_path)
    clean_path = tmp_path / "clean_campaign_data.csv"
    db_path = tmp_path / "marketing.db"
    clean_data(raw_path, clean_path)
    load_data(clean_path, db_path)

    with sqlite3.connect(db_path) as conn:
        basic_sql = SQL_ANALYSIS_PATH.read_text(encoding="utf-8")
        first_query = [q.strip() for q in basic_sql.split(";") if q.strip()][0]
        first_row = conn.execute(first_query).fetchone()
        assert first_row is not None
        assert len(first_row) == 4

        advanced_sql = SQL_ADVANCED_PATH.read_text(encoding="utf-8")
        adv_query = [q.strip() for q in advanced_sql.split(";") if q.strip()][0]
        adv_row = conn.execute(adv_query).fetchone()
        assert adv_row is not None
        assert len(adv_row) == 6


def test_data_model_sql_creates_star_schema_tables(tmp_path: Path) -> None:
    raw_path = _write_raw_csv(tmp_path)
    clean_path = tmp_path / "clean_campaign_data.csv"
    db_path = tmp_path / "marketing.db"
    clean_data(raw_path, clean_path)
    load_data(clean_path, db_path)

    with sqlite3.connect(db_path) as conn:
        conn.executescript(SQL_MODELS_PATH.read_text(encoding="utf-8"))
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('fact_campaign_daily','dim_campaign','dim_channel','dim_date');"
            ).fetchall()
        }
        assert tables == {"fact_campaign_daily", "dim_campaign", "dim_channel", "dim_date"}
        fact_rows = conn.execute("SELECT COUNT(*) FROM fact_campaign_daily;").fetchone()[0]
        assert fact_rows > 0


def test_powerbi_export_creates_files(tmp_path: Path) -> None:
    raw_path = _write_raw_csv(tmp_path)
    clean_path = tmp_path / "clean_campaign_data.csv"
    export_dir = tmp_path / "powerbi_export"
    clean_data(raw_path, clean_path)
    stats = export_powerbi_assets(clean_path, export_dir)
    assert stats["detail_rows"] > 0
    assert stats["summary_rows"] > 0
    assert (export_dir / "campaign_daily_detail.csv").exists()
    assert (export_dir / "campaign_summary.csv").exists()
    assert (export_dir / "powerbi_ready_tables.xlsx").exists()