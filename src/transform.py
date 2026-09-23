from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.data_quality.engine import (
    RuleResult,
    build_rejection_reasons,
    evaluate_rules,
    prepare_types,
)


def split_valid_and_quarantine(
    raw: pd.DataFrame, contract: dict
) -> tuple[pd.DataFrame, pd.DataFrame, list[RuleResult]]:
    """Aplica as regras e separa dados aprovados de registros rejeitados."""
    typed = prepare_types(raw)
    rule_results, masks = evaluate_rules(typed, contract)
    rejection_reasons = build_rejection_reasons(masks)
    rejected_mask = rejection_reasons.ne("")

    clean = typed.loc[~rejected_mask].copy()
    clean["quantity"] = clean["quantity"].astype("int64")
    clean["unit_price"] = clean["unit_price"].astype("float64").round(2)
    clean["discount_pct"] = clean["discount_pct"].astype("float64").round(4)
    clean["total_amount"] = (
        clean["quantity"] * clean["unit_price"] * (1 - clean["discount_pct"])
    ).round(2)
    clean = clean.sort_values(["order_date", "order_id"]).reset_index(drop=True)

    quarantine = raw.loc[rejected_mask].copy()
    quarantine.insert(0, "rejection_reason", rejection_reasons.loc[rejected_mask].values)
    quarantine = quarantine.reset_index(drop=True)
    return clean, quarantine, rule_results


def write_data_layers(
    clean: pd.DataFrame,
    quarantine: pd.DataFrame,
    processed_path: Path,
    quarantine_path: Path,
) -> tuple[Path, Path]:
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    quarantine_path.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(processed_path, index=False, date_format="%Y-%m-%d")
    quarantine.to_csv(quarantine_path, index=False)
    return processed_path, quarantine_path
