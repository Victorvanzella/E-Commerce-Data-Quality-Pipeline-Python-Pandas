from __future__ import annotations

import pandera as pa
import pytest

from src.data_quality.schema import validate_clean_schema
from src.generate_data import generate_dataset
from src.transform import split_valid_and_quarantine


def test_pandera_schema_accepts_clean_layer(contract: dict) -> None:
    clean, _, _ = split_valid_and_quarantine(generate_dataset(100, 42, contract), contract)

    validated = validate_clean_schema(clean, contract)

    assert len(validated) == 100


def test_pandera_schema_rejects_invalid_quantity(contract: dict) -> None:
    clean, _, _ = split_valid_and_quarantine(generate_dataset(100, 42, contract), contract)
    clean.loc[0, "quantity"] = 0

    with pytest.raises(pa.errors.SchemaErrors):
        validate_clean_schema(clean, contract)
