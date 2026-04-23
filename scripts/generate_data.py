from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from typing import TypedDict


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw_campaign_data.csv"


class CampaignConfig(TypedDict):
    impressions: tuple[int, int]
    ctr: tuple[float, float]
    conv_rate: tuple[float, float]
    cpc: tuple[float, float]


def build_synthetic_dataset() -> pd.DataFrame:
    np.random.seed(42)

    campaigns: dict[str, CampaignConfig] = {
        "Social_FB": {"impressions": (9000, 26000), "ctr": (0.010, 0.028), "conv_rate": (0.018, 0.050), "cpc": (0.60, 1.60)},
        "Social_IG": {"impressions": (7000, 22000), "ctr": (0.008, 0.022), "conv_rate": (0.015, 0.042), "cpc": (0.55, 1.40)},
        "Search_Google": {"impressions": (4500, 14000), "ctr": (0.020, 0.060), "conv_rate": (0.035, 0.090), "cpc": (1.20, 3.80)},
        "Display_Programmatic": {
            "impressions": (12000, 40000),
            "ctr": (0.003, 0.012),
            "conv_rate": (0.006, 0.020),
            "cpc": (0.35, 1.10),
        },
        "Email_Newsletter": {"impressions": (2500, 9000), "ctr": (0.020, 0.055), "conv_rate": (0.045, 0.120), "cpc": (0.25, 0.90)},
    }

    start_date = datetime.today().date() - timedelta(days=179)
    dates = [start_date + timedelta(days=i) for i in range(180)]

    rows: list[dict[str, float | int | str]] = []
    for date in dates:
        seasonality = 1.0 + 0.10 * np.sin((date.timetuple().tm_yday / 365.0) * 2 * np.pi)
        day_noise = np.random.normal(1.0, 0.06)

        for campaign_id, params in campaigns.items():
            impressions = int(np.random.randint(*params["impressions"]) * seasonality * day_noise)
            ctr = float(np.random.uniform(*params["ctr"]))
            clicks = int(max(0, round(impressions * ctr)))

            conv_rate = float(np.random.uniform(*params["conv_rate"]))
            conversions = int(max(0, round(clicks * conv_rate)))

            cpc = float(np.random.uniform(*params["cpc"]))
            cost = round(clicks * cpc * np.random.uniform(0.93, 1.08), 2)

            rows.append(
                {
                    "campaign_id": campaign_id,
                    "date": date.isoformat(),
                    "impressions": impressions,
                    "clicks": clicks,
                    "cost": cost,
                    "conversions": conversions,
                }
            )

    return pd.DataFrame(rows)


def main() -> None:
    df = build_synthetic_dataset()
    RAW_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(RAW_DATA_PATH, index=False)
    print(f"Generated {len(df)} rows at {RAW_DATA_PATH}")


if __name__ == "__main__":
    main()