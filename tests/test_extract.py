from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.extract import SchemaContractError, extract_csv


def test_extract_preserves_contract_column_order(tmp_path: Path, contract: dict) -> None:
    path = tmp_path / "source.csv"
    pd.DataFrame({column: ["value"] for column in reversed(contract["required_columns"])}).to_csv(
        path, index=False
    )

    extracted = extract_csv(path, contract["required_columns"])

    assert extracted.columns.tolist() == contract["required_columns"]


def test_extract_rejects_missing_column(tmp_path: Path, contract: dict) -> None:
    path = tmp_path / "source.csv"
    pd.DataFrame({"order_id": ["ORD1"]}).to_csv(path, index=False)

    with pytest.raises(SchemaContractError, match="Colunas obrigatorias ausentes"):
        extract_csv(path, contract["required_columns"])


def test_extract_rejects_missing_file(tmp_path: Path, contract: dict) -> None:
    with pytest.raises(FileNotFoundError):
        extract_csv(tmp_path / "missing.csv", contract["required_columns"])
