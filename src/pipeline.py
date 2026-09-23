from __future__ import annotations

import argparse
import logging
import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from src.analytics import build_analytics, write_analytics
from src.config import Settings, settings
from src.contracts import load_contract
from src.data_quality.engine import evaluate_rules
from src.data_quality.reporting import build_quality_report, write_json_report
from src.data_quality.schema import validate_clean_schema
from src.extract import extract_csv
from src.generate_data import generate_dataset, write_dataset
from src.logging_config import configure_logging
from src.transform import split_valid_and_quarantine, write_data_layers

LOGGER = logging.getLogger(__name__)


def _build_pipeline_metrics(
    *,
    run_id: str,
    contract_version: str,
    requested_rows: int | None,
    raw_rows: int,
    accepted_rows: int,
    quarantined_rows: int,
    rules_evaluated: int,
    rules_passed: int,
    duration_seconds: float,
    clean,
    analytics_paths: list[Path],
) -> dict:
    recognized = clean.loc[clean["delivery_status"] != "Cancelled", "total_amount"]
    return {
        "run_id": run_id,
        "status": "SUCCESS",
        "finished_at_utc": datetime.now(UTC).isoformat(),
        "contract_version": contract_version,
        "requested_valid_source_rows": requested_rows,
        "raw_rows": raw_rows,
        "accepted_rows": accepted_rows,
        "quarantined_rows": quarantined_rows,
        "acceptance_rate_pct": round(100 * accepted_rows / raw_rows, 4),
        "clean_rules_evaluated": rules_evaluated,
        "clean_rules_passed": rules_passed,
        "unique_customers": int(clean["customer_id"].nunique()),
        "gross_order_value": round(float(clean["total_amount"].sum()), 2),
        "recognized_revenue": round(float(recognized.sum()), 2),
        "duration_seconds": round(duration_seconds, 3),
        "analytical_outputs": [path.name for path in analytics_paths],
    }


def run_pipeline(
    *,
    config: Settings = settings,
    row_count: int | None = None,
    seed: int | None = None,
    generate_source: bool = True,
) -> dict:
    started_at = time.perf_counter()
    run_id = uuid4().hex
    config.ensure_directories()
    configure_logging(config.log_file)
    contract = load_contract(config.contract_file)
    selected_rows = config.source_row_count if row_count is None else row_count
    selected_seed = config.source_seed if seed is None else seed

    LOGGER.info("run_id=%s pipeline iniciada", run_id)
    try:
        if generate_source:
            generated = generate_dataset(selected_rows, selected_seed, contract)
            write_dataset(generated, config.raw_file)
            LOGGER.info("camada raw gerada: %s linhas", len(generated))

        raw = extract_csv(config.raw_file, contract["required_columns"])
        clean, quarantine, raw_results = split_valid_and_quarantine(raw, contract)
        write_data_layers(clean, quarantine, config.processed_file, config.quarantine_file)
        LOGGER.info("qualidade aplicada: %s aceitas, %s em quarentena", len(clean), len(quarantine))

        validate_clean_schema(clean, contract)
        clean_results, _ = evaluate_rules(clean, contract)
        failed_clean_rules = [result.rule_name for result in clean_results if not result.passed]
        if failed_clean_rules:
            raise RuntimeError(f"Camada processada reprovada: {failed_clean_rules}")

        analytics_paths = write_analytics(build_analytics(clean), config.reports_dir)
        quality_report = build_quality_report(
            raw_rows=len(raw),
            clean_rows=len(clean),
            quarantine=quarantine,
            raw_results=raw_results,
            clean_results=clean_results,
            contract_version=str(contract["version"]),
            minimum_acceptance_rate=config.min_acceptance_rate,
        )
        write_json_report(quality_report, config.quality_report_file)
        if quality_report["quality_gate"]["status"] != "PASSED":
            raise RuntimeError(
                "Quality gate reprovado: taxa de aceitacao "
                f"{quality_report['quality_gate']['actual_acceptance_rate_pct']}%"
            )

        metrics = _build_pipeline_metrics(
            run_id=run_id,
            contract_version=str(contract["version"]),
            requested_rows=selected_rows if generate_source else None,
            raw_rows=len(raw),
            accepted_rows=len(clean),
            quarantined_rows=len(quarantine),
            rules_evaluated=len(clean_results),
            rules_passed=sum(result.passed for result in clean_results),
            duration_seconds=time.perf_counter() - started_at,
            clean=clean,
            analytics_paths=analytics_paths,
        )
        write_json_report(metrics, config.metrics_file)
        LOGGER.info("run_id=%s pipeline concluida com sucesso", run_id)
        return metrics
    except Exception as error:
        failure_metrics = {
            "run_id": run_id,
            "status": "FAILED",
            "finished_at_utc": datetime.now(UTC).isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "duration_seconds": round(time.perf_counter() - started_at, 3),
        }
        write_json_report(failure_metrics, config.metrics_file)
        LOGGER.exception("run_id=%s pipeline interrompida por erro", run_id)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Executa o pipeline de qualidade de e-commerce.")
    parser.add_argument("--rows", type=int, default=None, help="Quantidade de pedidos validos.")
    parser.add_argument("--seed", type=int, default=None, help="Seed da fonte sintetica.")
    parser.add_argument(
        "--skip-generate",
        action="store_true",
        help="Usa o CSV existente em data/raw em vez de gerar uma nova fonte.",
    )
    args = parser.parse_args()
    metrics = run_pipeline(
        row_count=args.rows,
        seed=args.seed,
        generate_source=not args.skip_generate,
    )
    print(
        "Pipeline concluida: "
        f"{metrics['accepted_rows']} aceitos, "
        f"{metrics['quarantined_rows']} em quarentena, "
        f"taxa de {metrics['acceptance_rate_pct']}%."
    )


if __name__ == "__main__":
    main()
