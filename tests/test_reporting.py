from __future__ import annotations

from src.data_quality.engine import evaluate_rules
from src.data_quality.reporting import build_quality_report
from src.generate_data import generate_dataset
from src.transform import split_valid_and_quarantine


def test_quality_report_passes_expected_gate(contract: dict) -> None:
    raw = generate_dataset(100, 42, contract)
    clean, quarantine, raw_results = split_valid_and_quarantine(raw, contract)
    clean_results, _ = evaluate_rules(clean, contract)

    report = build_quality_report(
        len(raw), len(clean), quarantine, raw_results, clean_results, "1.0", 60.0
    )

    assert report["quality_gate"]["status"] == "PASSED"
    assert report["record_summary"]["quarantined_rows"] == 55
    assert report["clean_rule_summary"]["rules_passed"] == 12
    assert report["quarantine_reason_counts"]["total_amount_consistent"] == 25


def test_quality_report_fails_strict_acceptance_gate(contract: dict) -> None:
    raw = generate_dataset(100, 42, contract)
    clean, quarantine, raw_results = split_valid_and_quarantine(raw, contract)
    clean_results, _ = evaluate_rules(clean, contract)

    report = build_quality_report(
        len(raw), len(clean), quarantine, raw_results, clean_results, "1.0", 99.0
    )

    assert report["quality_gate"]["status"] == "FAILED"
