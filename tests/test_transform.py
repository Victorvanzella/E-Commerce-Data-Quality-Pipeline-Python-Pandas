from __future__ import annotations

from src.data_quality.engine import evaluate_rules
from src.generate_data import generate_dataset
from src.transform import split_valid_and_quarantine


def test_transform_routes_bad_rows_to_quarantine(contract: dict) -> None:
    raw = generate_dataset(100, 42, contract)

    clean, quarantine, _ = split_valid_and_quarantine(raw, contract)

    assert len(clean) == 100
    assert len(quarantine) == 55
    assert clean["order_id"].is_unique
    assert quarantine["rejection_reason"].ne("").all()
    assert "order_id_unique" in set(quarantine["rejection_reason"])


def test_clean_layer_passes_every_rule(contract: dict) -> None:
    raw = generate_dataset(100, 42, contract)
    clean, _, _ = split_valid_and_quarantine(raw, contract)

    results, _ = evaluate_rules(clean, contract)

    assert all(result.passed for result in results)
    assert str(clean["quantity"].dtype) == "int64"
    assert str(clean["order_date"].dtype) == "datetime64[ns]"
