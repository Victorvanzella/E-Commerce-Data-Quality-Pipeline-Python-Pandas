from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class RuleResult:
    rule_name: str
    dimension: str
    passed: bool
    failed_count: int
    description: str

    def to_dict(self) -> dict[str, str | bool | int]:
        return asdict(self)


def _clean_text(series: pd.Series) -> pd.Series:
    cleaned = series.map(lambda value: None if value is None else str(value).strip())
    return cleaned.replace({"": None})


def prepare_types(dataframe: pd.DataFrame) -> pd.DataFrame:
    typed = dataframe.copy()
    for column in (
        "order_id",
        "customer_id",
        "product_id",
        "product_name",
        "category",
        "payment_method",
        "delivery_status",
        "country",
    ):
        typed[column] = _clean_text(typed[column])
    typed["order_date"] = pd.to_datetime(typed["order_date"], errors="coerce")
    for column in ("quantity", "unit_price", "discount_pct", "total_amount"):
        typed[column] = pd.to_numeric(typed[column], errors="coerce")
    return typed


def evaluate_rules(
    dataframe: pd.DataFrame, contract: dict
) -> tuple[list[RuleResult], dict[str, pd.Series]]:
    thresholds = contract["thresholds"]
    domains = contract["domains"]
    row_count = len(dataframe)
    masks: dict[str, pd.Series] = {}

    required_missing = set(contract["required_columns"]) - set(dataframe.columns)
    masks["required_columns_present"] = pd.Series(False, index=dataframe.index)
    masks["order_id_not_null"] = dataframe["order_id"].isna()
    masks["order_id_unique"] = dataframe["order_id"].notna() & dataframe["order_id"].duplicated(
        keep="first"
    )
    masks["customer_id_not_null"] = dataframe["customer_id"].isna()
    masks["order_date_valid"] = dataframe["order_date"].isna()
    masks["quantity_positive"] = dataframe["quantity"].isna() | dataframe["quantity"].lt(
        thresholds["quantity_min"]
    )
    masks["quantity_within_limit"] = dataframe["quantity"].isna() | dataframe["quantity"].gt(
        thresholds["quantity_max"]
    )
    masks["unit_price_positive"] = dataframe["unit_price"].isna() | dataframe["unit_price"].le(
        thresholds["unit_price_min_exclusive"]
    )
    masks["discount_valid_range"] = dataframe["discount_pct"].isna() | ~dataframe[
        "discount_pct"
    ].between(thresholds["discount_min"], thresholds["discount_max"])
    masks["delivery_status_domain"] = ~dataframe["delivery_status"].isin(domains["delivery_status"])
    masks["category_domain"] = ~dataframe["category"].isin(domains["category"])
    expected_total = (
        dataframe["quantity"] * dataframe["unit_price"] * (1 - dataframe["discount_pct"])
    ).round(2)
    mismatch = ~np.isclose(
        dataframe["total_amount"],
        expected_total,
        atol=thresholds["total_amount_tolerance"],
        equal_nan=False,
    )
    masks["total_amount_consistent"] = pd.Series(mismatch, index=dataframe.index)

    definitions = (
        ("required_columns_present", "schema", "Todas as colunas obrigatorias devem existir"),
        ("order_id_not_null", "completeness", "order_id deve estar preenchido"),
        ("order_id_unique", "uniqueness", "order_id deve ser unico"),
        ("customer_id_not_null", "completeness", "customer_id deve estar preenchido"),
        ("order_date_valid", "validity", "order_date deve ser uma data valida"),
        ("quantity_positive", "validity", "quantity deve ser positiva"),
        ("quantity_within_limit", "validity", "quantity nao pode ultrapassar o limite"),
        ("unit_price_positive", "validity", "unit_price deve ser positivo"),
        ("discount_valid_range", "validity", "discount_pct deve estar no intervalo permitido"),
        ("delivery_status_domain", "validity", "delivery_status deve pertencer ao dominio"),
        ("category_domain", "validity", "category deve pertencer ao dominio"),
        ("total_amount_consistent", "consistency", "total_amount deve corresponder ao calculo"),
    )

    results: list[RuleResult] = []
    for rule_name, dimension, description in definitions:
        failed_count = (
            len(required_missing)
            if rule_name == "required_columns_present"
            else int(masks[rule_name].sum())
        )
        results.append(
            RuleResult(
                rule_name=rule_name,
                dimension=dimension,
                passed=failed_count == 0,
                failed_count=failed_count,
                description=description,
            )
        )
    if row_count == 0:
        raise ValueError("Dataset vazio nao pode ser validado")
    return results, masks


def build_rejection_reasons(masks: dict[str, pd.Series]) -> pd.Series:
    row_rules = [rule for rule in masks if rule != "required_columns_present"]
    reasons = []
    for index in next(iter(masks.values())).index:
        failed = [rule for rule in row_rules if bool(masks[rule].loc[index])]
        reasons.append(";".join(failed))
    return pd.Series(reasons, index=next(iter(masks.values())).index, dtype="object")
