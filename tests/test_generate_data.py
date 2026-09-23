from __future__ import annotations

import pandas as pd
import pytest

from src.generate_data import generate_dataset, generate_valid_orders


def test_generation_is_deterministic(contract: dict) -> None:
    first = generate_valid_orders(100, 42, contract)
    second = generate_valid_orders(100, 42, contract)
    pd.testing.assert_frame_equal(first, second)


def test_valid_source_respects_core_domains(contract: dict) -> None:
    dataframe = generate_valid_orders(200, 7, contract)

    assert len(dataframe) == 200
    assert dataframe["order_id"].is_unique
    assert set(dataframe["category"]).issubset(contract["domains"]["category"])
    assert dataframe["quantity"].between(1, 6).all()
    assert dataframe["total_amount"].gt(0).all()


def test_controlled_anomalies_add_55_rows(contract: dict) -> None:
    dataframe = generate_dataset(100, 42, contract)

    assert len(dataframe) == 155
    assert dataframe["order_id"].isna().sum() == 5
    assert (dataframe["delivery_status"] == "Lost").sum() == 5
    assert (dataframe["category"] == "Unknown").sum() == 5


def test_generation_rejects_too_few_rows(contract: dict) -> None:
    with pytest.raises(ValueError, match="pelo menos 100"):
        generate_valid_orders(99, 42, contract)
