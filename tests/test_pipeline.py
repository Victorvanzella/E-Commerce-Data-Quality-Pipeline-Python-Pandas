from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

import src.clean_outputs as clean_outputs_module
import src.verify_outputs as verify_outputs_module
from src.config import Settings
from src.pipeline import run_pipeline


def _temporary_config(tmp_path: Path) -> Settings:
    source_contract = Path(__file__).resolve().parents[1] / "contracts" / "sales_orders.yml"
    contract_dir = tmp_path / "contracts"
    contract_dir.mkdir()
    shutil.copy2(source_contract, contract_dir / "sales_orders.yml")
    return Settings(
        project_root=tmp_path,
        source_row_count=100,
        source_seed=42,
        min_acceptance_rate=60.0,
    )


def test_pipeline_runs_end_to_end(tmp_path: Path) -> None:
    config = _temporary_config(tmp_path)

    metrics = run_pipeline(config=config)

    assert metrics["status"] == "SUCCESS"
    assert metrics["raw_rows"] == 155
    assert metrics["accepted_rows"] == 100
    assert metrics["quarantined_rows"] == 55
    assert config.processed_file.exists()
    assert config.quarantine_file.exists()
    assert len(list(config.reports_dir.glob("*.csv"))) == 5
    quality = json.loads(config.quality_report_file.read_text(encoding="utf-8"))
    assert quality["quality_gate"]["status"] == "PASSED"


def test_output_verifier_checks_generated_evidence(tmp_path: Path, monkeypatch) -> None:
    config = _temporary_config(tmp_path)
    run_pipeline(config=config)
    monkeypatch.setattr(verify_outputs_module, "settings", config)

    result = verify_outputs_module.verify()

    assert result["status"] == "PASSED"
    assert all(result["checks"].values())


def test_clean_outputs_removes_only_generated_files(tmp_path: Path, monkeypatch) -> None:
    config = _temporary_config(tmp_path)
    run_pipeline(config=config)
    keep = tmp_path / "reports" / "keep.txt"
    keep.write_text("nao remover", encoding="utf-8")
    monkeypatch.setattr(clean_outputs_module, "settings", config)

    removed = clean_outputs_module.clean_generated_outputs()

    assert len(removed) == 11
    assert keep.exists()
    assert not config.processed_file.exists()


def test_failed_quality_gate_records_failure_metrics(tmp_path: Path) -> None:
    config = _temporary_config(tmp_path)
    strict_config = Settings(
        project_root=config.project_root,
        source_row_count=100,
        source_seed=42,
        min_acceptance_rate=99.0,
    )

    with pytest.raises(RuntimeError, match="Quality gate reprovado"):
        run_pipeline(config=strict_config)

    metrics = json.loads(strict_config.metrics_file.read_text(encoding="utf-8"))
    assert metrics["status"] == "FAILED"
    assert metrics["error_type"] == "RuntimeError"
