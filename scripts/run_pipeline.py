from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"


def run_step(script_name: str) -> None:
    script_path = SCRIPTS_DIR / script_name
    command = [sys.executable, str(script_path)]
    print(f"\nRunning step: {script_name}")
    subprocess.run(command, check=True)


def main() -> None:
    steps = [
        "generate_data.py",
        "clean_data.py",
        "load_data.py",
        "run_analysis.py",
        "generate_dashboard.py",
    ]
    for step in steps:
        run_step(step)
    print("\nPipeline completed end-to-end.")


if __name__ == "__main__":
    main()