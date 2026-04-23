from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLEAN_DATA_PATH = PROJECT_ROOT / "data" / "clean_campaign_data.csv"
DB_PATH = PROJECT_ROOT / "data" / "marketing.db"
TABLE_NAME = "campaign_performance"


def initialize_table(connection: sqlite3.Connection) -> None:
    connection.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            date TEXT NOT NULL,
            campaign_id TEXT NOT NULL,
            impressions INTEGER NOT NULL,
            clicks INTEGER NOT NULL,
            cost REAL NOT NULL,
            conversions INTEGER NOT NULL,
            ctr REAL NOT NULL,
            cpc REAL NOT NULL,
            cpa REAL NOT NULL
        );
        """
    )
    connection.commit()


def load_data(csv_path: Path, db_path: Path) -> int:
    df = pd.read_csv(csv_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        initialize_table(conn)
        conn.execute(f"DELETE FROM {TABLE_NAME};")
        conn.commit()
        df.to_sql(TABLE_NAME, conn, if_exists="append", index=False)
        count = conn.execute(f"SELECT COUNT(*) FROM {TABLE_NAME};").fetchone()[0]
    return int(count)


def main() -> None:
    row_count = load_data(CLEAN_DATA_PATH, DB_PATH)
    print(f"Loaded rows into SQLite ({TABLE_NAME}): {row_count}")
    print(f"Database path: {DB_PATH}")


if __name__ == "__main__":
    main()