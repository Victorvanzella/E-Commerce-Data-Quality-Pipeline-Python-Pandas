from __future__ import annotations

from pathlib import Path

import pytest

from src.contracts import load_contract


@pytest.fixture
def contract() -> dict:
    path = Path(__file__).resolve().parents[1] / "contracts" / "sales_orders.yml"
    return load_contract(path)
