from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    project_root: Path = PROJECT_ROOT
    source_row_count: int = int(os.getenv("SOURCE_ROW_COUNT", "10000"))
    source_seed: int = int(os.getenv("SOURCE_SEED", "42"))
    min_acceptance_rate: float = float(os.getenv("QUALITY_MIN_ACCEPTANCE_RATE", "99.0"))

    @property
    def contract_file(self) -> Path:
        return self.project_root / "contracts" / "sales_orders.yml"

    @property
    def raw_file(self) -> Path:
        return self.project_root / "data" / "raw" / "sales_orders_raw.csv"

    @property
    def processed_file(self) -> Path:
        return self.project_root / "data" / "processed" / "sales_orders_clean.csv"

    @property
    def quarantine_file(self) -> Path:
        return self.project_root / "data" / "quarantine" / "sales_orders_quarantine.csv"

    @property
    def quality_report_file(self) -> Path:
        return self.project_root / "reports" / "data_quality_report.json"

    @property
    def metrics_file(self) -> Path:
        return self.project_root / "reports" / "pipeline_metrics.json"

    @property
    def log_file(self) -> Path:
        return self.project_root / "logs" / "pipeline.log"

    @property
    def reports_dir(self) -> Path:
        return self.project_root / "reports"

    def ensure_directories(self) -> None:
        for directory in (
            self.raw_file.parent,
            self.processed_file.parent,
            self.quarantine_file.parent,
            self.reports_dir,
            self.log_file.parent,
        ):
            directory.mkdir(parents=True, exist_ok=True)


settings = Settings()
