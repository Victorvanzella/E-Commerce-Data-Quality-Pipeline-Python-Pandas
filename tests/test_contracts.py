from __future__ import annotations

from pathlib import Path

import pytest

from src.contracts import load_contract


def test_incomplete_contract_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "contract.yml"
    path.write_text("version: '1.0'\ndataset: test\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Contrato incompleto"):
        load_contract(path)
