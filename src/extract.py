from __future__ import annotations

from pathlib import Path

import pandas as pd


class SchemaContractError(ValueError):
    pass


def extract_csv(path: Path, required_columns: list[str]) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Arquivo de origem nao encontrado: {path}")
    dataframe = pd.read_csv(path, dtype=str, keep_default_na=False).replace({"": None})
    missing_columns = sorted(set(required_columns) - set(dataframe.columns))
    if missing_columns:
        raise SchemaContractError(f"Colunas obrigatorias ausentes: {missing_columns}")
    return dataframe.loc[:, required_columns].copy()
