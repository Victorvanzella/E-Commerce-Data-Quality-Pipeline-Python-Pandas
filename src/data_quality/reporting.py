from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from src.data_quality.engine import RuleResult


def _dimension_scores(results: list[RuleResult], row_count: int) -> dict[str, float]:
    dimensions: dict[str, list[float]] = {}
    denominator = max(row_count, 1)
    for result in results:
        score = max(0.0, 100 * (1 - result.failed_count / denominator))
        dimensions.setdefault(result.dimension, []).append(score)
    return {
        dimension: round(sum(scores) / len(scores), 2)
        for dimension, scores in sorted(dimensions.items())
    }


def _reason_counts(quarantine: pd.DataFrame) -> dict[str, int]:
    counts: Counter[str] = Counter()
    if "rejection_reason" not in quarantine:
        return {}
    for reasons in quarantine["rejection_reason"].dropna():
        counts.update(reason for reason in str(reasons).split(";") if reason)
    return dict(sorted(counts.items()))


def build_quality_report(
    raw_rows: int,
    clean_rows: int,
    quarantine: pd.DataFrame,
    raw_results: list[RuleResult],
    clean_results: list[RuleResult],
    contract_version: str,
    minimum_acceptance_rate: float,
) -> dict:
    acceptance_rate = 100 * clean_rows / raw_rows if raw_rows else 0.0
    clean_rules_passed = sum(result.passed for result in clean_results)
    gate_passed = acceptance_rate >= minimum_acceptance_rate and clean_rules_passed == len(
        clean_results
    )
    return {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "dataset": "sales_orders",
        "contract_version": contract_version,
        "quality_gate": {
            "status": "PASSED" if gate_passed else "FAILED",
            "minimum_acceptance_rate_pct": minimum_acceptance_rate,
            "actual_acceptance_rate_pct": round(acceptance_rate, 4),
        },
        "record_summary": {
            "raw_rows": raw_rows,
            "accepted_rows": clean_rows,
            "quarantined_rows": len(quarantine),
        },
        "raw_dimension_scores_pct": _dimension_scores(raw_results, raw_rows),
        "raw_rule_results": [result.to_dict() for result in raw_results],
        "quarantine_reason_counts": _reason_counts(quarantine),
        "clean_rule_summary": {
            "rules_evaluated": len(clean_results),
            "rules_passed": clean_rules_passed,
            "rules_failed": len(clean_results) - clean_rules_passed,
        },
        "clean_rule_results": [result.to_dict() for result in clean_results],
    }


def write_json_report(payload: dict, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(f"{path.suffix}.tmp")
    temporary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary_path.replace(path)
    return path
