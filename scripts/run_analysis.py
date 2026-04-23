from __future__ import annotations

import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "marketing.db"
SQL_PATH = PROJECT_ROOT / "sql" / "analysis.sql"
ADVANCED_SQL_PATH = PROJECT_ROOT / "sql" / "advanced_analysis.sql"
DATA_MODELS_SQL_PATH = PROJECT_ROOT / "sql" / "data_models.sql"


def run_analysis_queries(db_path: Path, sql_path: Path) -> None:
    sql_text = sql_path.read_text(encoding="utf-8")
    blocks = [block.strip() for block in sql_text.split(";") if block.strip()]

    with sqlite3.connect(db_path) as conn:
        for i, query in enumerate(blocks, start=1):
            title = query.splitlines()[0].strip().lstrip("- ").strip()
            cursor = conn.execute(query)
            rows = cursor.fetchmany(5)
            print(f"\nQuery {i}: {title}")
            print(f"Sample rows (up to 5): {rows}")


def run_sql_script(db_path: Path, sql_path: Path, label: str) -> None:
    script = sql_path.read_text(encoding="utf-8")
    with sqlite3.connect(db_path) as conn:
        conn.executescript(script)
    print(f"{label} executed: {sql_path}")


def main() -> None:
    run_sql_script(DB_PATH, DATA_MODELS_SQL_PATH, "Data model SQL")
    run_analysis_queries(DB_PATH, SQL_PATH)
    run_analysis_queries(DB_PATH, ADVANCED_SQL_PATH)
    print("\nAnalysis completed successfully.")


if __name__ == "__main__":
    main()