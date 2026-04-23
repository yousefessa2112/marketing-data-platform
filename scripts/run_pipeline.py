from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml  # type: ignore[import-untyped]

from pipeline_logger import PipelineLogger

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
CONFIG_PATH = PROJECT_ROOT / "config" / "pipeline_config.yaml"


def load_config() -> dict[str, object]:
    if not CONFIG_PATH.exists():
        return {}
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_rows_from_clean_csv() -> int | None:
    clean_path = PROJECT_ROOT / "data" / "clean_campaign_data.csv"
    if not clean_path.exists():
        return None
    return int(len(pd.read_csv(clean_path)))


def get_rows_from_parquet() -> int | None:
    parquet_dir = PROJECT_ROOT / "data" / "output" / "campaign_daily_parquet"
    if not parquet_dir.exists():
        return None
    return None


def run_step(script_name: str, logger: PipelineLogger, row_counter: str | None = None) -> None:
    script_path = SCRIPTS_DIR / script_name
    command = [sys.executable, str(script_path)]
    print(f"\nRunning step: {script_name}")
    start_time = datetime.now(timezone.utc)
    try:
        subprocess.run(command, check=True)
        end_time = datetime.now(timezone.utc)
        rows_processed: int | None = None
        if row_counter == "clean_csv":
            rows_processed = get_rows_from_clean_csv()
        elif row_counter == "spark_parquet":
            rows_processed = get_rows_from_parquet()
        logger.log_step(
            step_name=script_name,
            status="SUCCESS",
            start_time=start_time,
            end_time=end_time,
            rows_processed=rows_processed,
        )
    except subprocess.CalledProcessError as exc:
        end_time = datetime.now(timezone.utc)
        logger.log_step(
            step_name=script_name,
            status="FAILED",
            start_time=start_time,
            end_time=end_time,
            error_message=str(exc),
        )
        raise


def main() -> None:
    config = load_config()
    pipeline_config: dict[str, object] = {}
    if isinstance(config, dict):
        maybe_pipeline = config.get("pipeline", {})
        if isinstance(maybe_pipeline, dict):
            pipeline_config = maybe_pipeline
    run_pyspark = bool(pipeline_config.get("run_pyspark_step", True))

    logger = PipelineLogger()
    steps: list[tuple[str, str | None]] = [
        ("generate_data.py", None),
        ("clean_data.py", "clean_csv"),
        ("data_quality.py", None),
        ("load_data.py", "clean_csv"),
        ("run_analysis.py", None),
    ]
    if run_pyspark:
        steps.append(("pyspark_processing.py", "spark_parquet"))
    steps.extend(
        [
            ("generate_dashboard.py", None),
            ("export_for_powerbi.py", "clean_csv"),
            ("generate_presentation.py", None),
        ]
    )

    for step, row_counter in steps:
        run_step(step, logger, row_counter=row_counter)
    print("\nPipeline completed end-to-end.")


if __name__ == "__main__":
    main()