from __future__ import annotations

import json

import pandas as pd

from src.config import settings


def verify() -> dict:
    required_files = (
        settings.raw_file,
        settings.processed_file,
        settings.quarantine_file,
        settings.quality_report_file,
        settings.metrics_file,
    )
    missing = [str(path) for path in required_files if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Saidas obrigatorias ausentes: {missing}")

    metrics = json.loads(settings.metrics_file.read_text(encoding="utf-8"))
    quality = json.loads(settings.quality_report_file.read_text(encoding="utf-8"))
    clean = pd.read_csv(settings.processed_file)
    quarantine = pd.read_csv(settings.quarantine_file)

    assertions = {
        "pipeline_success": metrics["status"] == "SUCCESS",
        "quality_gate_passed": quality["quality_gate"]["status"] == "PASSED",
        "processed_count_matches": len(clean) == metrics["accepted_rows"],
        "quarantine_count_matches": len(quarantine) == metrics["quarantined_rows"],
        "clean_order_ids_unique": clean["order_id"].is_unique,
        "quarantine_has_reasons": quarantine["rejection_reason"].notna().all(),
        "all_clean_rules_passed": (
            metrics["clean_rules_evaluated"] == metrics["clean_rules_passed"]
        ),
    }
    requested = metrics.get("requested_valid_source_rows")
    if requested is not None:
        assertions.update(
            {
                "generated_clean_count": metrics["accepted_rows"] == requested,
                "controlled_anomaly_count": metrics["quarantined_rows"] == 55,
                "generated_raw_count": metrics["raw_rows"] == requested + 55,
            }
        )
    failed = [name for name, passed in assertions.items() if not passed]
    if failed:
        raise AssertionError(f"Verificacao das saidas falhou: {failed}")
    return {"status": "PASSED", "checks": assertions}


def main() -> None:
    result = verify()
    print(f"Verificacao concluida: {len(result['checks'])} checks aprovados.")


if __name__ == "__main__":
    main()
