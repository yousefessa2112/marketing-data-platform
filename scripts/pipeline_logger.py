from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_PATH = PROJECT_ROOT / "data" / "pipeline_log.csv"


class PipelineLogger:
    def __init__(self, log_path: Path = LOG_PATH) -> None:
        self.log_path = log_path
        self.run_id = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        self.pipeline_start = datetime.now(timezone.utc)
        self._ensure_header()

    def _ensure_header(self) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_path.exists():
            with self.log_path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "run_id",
                        "step_name",
                        "status",
                        "start_time_utc",
                        "end_time_utc",
                        "duration_seconds",
                        "rows_processed",
                        "error_message",
                    ]
                )

    def log_step(
        self,
        step_name: str,
        status: str,
        start_time: datetime,
        end_time: datetime,
        rows_processed: int | None = None,
        error_message: str | None = None,
    ) -> None:
        duration_seconds = round((end_time - start_time).total_seconds(), 3)
        with self.log_path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    self.run_id,
                    step_name,
                    status,
                    start_time.isoformat(),
                    end_time.isoformat(),
                    duration_seconds,
                    rows_processed if rows_processed is not None else "",
                    error_message or "",
                ]
            )
