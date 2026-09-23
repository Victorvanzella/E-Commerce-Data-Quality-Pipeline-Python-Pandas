from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_contract(path: Path) -> dict[str, Any]:
    contract = yaml.safe_load(path.read_text(encoding="utf-8"))
    required_keys = {
        "version",
        "dataset",
        "primary_key",
        "required_columns",
        "domains",
        "thresholds",
    }
    missing = required_keys - set(contract)
    if missing:
        raise ValueError(f"Contrato incompleto; chaves ausentes: {sorted(missing)}")
    return contract
