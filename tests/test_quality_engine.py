from __future__ import annotations

import pytest

from src.data_quality.engine import build_rejection_reasons, evaluate_rules, prepare_types
from src.generate_data import generate_dataset, generate_valid_orders


def test_all_12_rules_pass_for_valid_source(contract: dict) -> None:
    valid = prepare_types(generate_valid_orders(100, 42, contract))
    results, _ = evaluate_rules(valid, contract)

    assert len(results) == 12
    assert all(result.passed for result in results)


def test_rules_detect_controlled_anomalies(contract: dict) -> None:
    raw = prepare_types(generate_dataset(100, 42, contract))
    results, masks = evaluate_rules(raw, contract)
    failures = {result.rule_name: result.failed_count for result in results}
    reasons = build_rejection_reasons(masks)

    assert failures["order_id_unique"] == 5
    assert failures["order_id_not_null"] == 5
    assert failures["customer_id_not_null"] == 5
    assert failures["order_date_valid"] == 5
    assert failures["total_amount_consistent"] == 25
    assert reasons.ne("").sum() == 55


def test_empty_dataset_is_rejected(contract: dict) -> None:
    empty = prepare_types(generate_valid_orders(100, 42, contract).head(0))

    with pytest.raises(ValueError, match="Dataset vazio"):
        evaluate_rules(empty, contract)
