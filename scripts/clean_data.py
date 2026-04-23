from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw_campaign_data.csv"
CLEAN_DATA_PATH = PROJECT_ROOT / "data" / "clean_campaign_data.csv"


def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    result = np.where(denominator > 0, numerator / denominator, 0.0)
    return pd.Series(result)


def clean_data(input_path: Path, output_path: Path) -> pd.DataFrame:
    df = pd.read_csv(input_path)

    df = df.dropna().drop_duplicates()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    numeric_cols = ["impressions", "clicks", "cost", "conversions"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=numeric_cols)

    df["impressions"] = df["impressions"].astype(int)
    df["clicks"] = df["clicks"].astype(int)
    df["cost"] = df["cost"].astype(float)
    df["conversions"] = df["conversions"].astype(int)

    df["ctr"] = safe_divide(df["clicks"], df["impressions"]).round(6)
    df["cpc"] = safe_divide(df["cost"], df["clicks"]).round(4)
    df["cpa"] = safe_divide(df["cost"], df["conversions"]).round(4)

    df["date"] = df["date"].dt.date.astype(str)
    df = df.sort_values(["date", "campaign_id"]).reset_index(drop=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return df


def main() -> None:
    cleaned = clean_data(RAW_DATA_PATH, CLEAN_DATA_PATH)
    print(f"Cleaned data rows: {len(cleaned)}")
    print(f"Saved cleaned dataset to: {CLEAN_DATA_PATH}")


if __name__ == "__main__":
    main()