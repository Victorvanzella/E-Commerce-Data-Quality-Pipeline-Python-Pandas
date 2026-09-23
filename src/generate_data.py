from __future__ import annotations

import argparse
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import settings
from src.contracts import load_contract
from src.logging_config import configure_logging

LOGGER = logging.getLogger(__name__)

PRODUCTS = (
    ("P001", "Wireless Headphones", "Electronics", 249.90),
    ("P002", "Mechanical Keyboard", "Electronics", 399.90),
    ("P003", "Coffee Maker", "Home", 319.90),
    ("P004", "Desk Lamp", "Home", 129.90),
    ("P005", "Running Shoes", "Sports", 289.90),
    ("P006", "Yoga Mat", "Sports", 89.90),
    ("P007", "Data Engineering Book", "Books", 119.90),
    ("P008", "SQL Pocket Guide", "Books", 79.90),
    ("P009", "Skin Care Kit", "Beauty", 159.90),
    ("P010", "Hair Dryer", "Beauty", 219.90),
)


def generate_valid_orders(row_count: int, seed: int, contract: dict) -> pd.DataFrame:
    if row_count < 100:
        raise ValueError("row_count deve ser pelo menos 100")

    rng = np.random.default_rng(seed)
    product_indexes = rng.integers(0, len(PRODUCTS), size=row_count)
    products = [PRODUCTS[index] for index in product_indexes]
    quantities = rng.integers(1, 7, size=row_count)
    prices = np.array(
        [max(5.0, product[3] * rng.uniform(0.92, 1.08)) for product in products]
    ).round(2)
    discounts = rng.choice(
        [0.0, 0.05, 0.10, 0.15, 0.20, 0.30],
        size=row_count,
        p=[0.35, 0.15, 0.20, 0.12, 0.13, 0.05],
    )
    total_amounts = np.round(quantities * prices * (1 - discounts), 2)
    start_date = np.datetime64("2025-01-01")
    order_dates = start_date + rng.integers(0, 365, size=row_count).astype("timedelta64[D]")

    return pd.DataFrame(
        {
            "order_id": [f"ORD{index:07d}" for index in range(1, row_count + 1)],
            "order_date": order_dates.astype(str),
            "customer_id": [f"CUS{value:05d}" for value in rng.integers(1, 2501, row_count)],
            "product_id": [product[0] for product in products],
            "product_name": [product[1] for product in products],
            "category": [product[2] for product in products],
            "quantity": quantities,
            "unit_price": prices,
            "discount_pct": discounts,
            "payment_method": rng.choice(contract["domains"]["payment_method"], row_count),
            "delivery_status": rng.choice(
                contract["domains"]["delivery_status"],
                row_count,
                p=[0.70, 0.14, 0.11, 0.05],
            ),
            "country": rng.choice(
                contract["domains"]["country"], row_count, p=[0.72, 0.10, 0.10, 0.08]
            ),
            "total_amount": total_amounts,
        }
    )


def inject_controlled_anomalies(valid: pd.DataFrame) -> pd.DataFrame:
    """Adiciona 55 linhas ruins em 11 grupos de cinco registros."""
    anomalies: list[pd.Series] = [valid.iloc[index].copy() for index in range(5)]
    mutations: tuple[tuple[str, object], ...] = (
        ("order_id", None),
        ("customer_id", None),
        ("order_date", "not-a-date"),
        ("quantity", -2),
        ("quantity", 500),
        ("unit_price", "free"),
        ("discount_pct", 0.80),
        ("delivery_status", "Lost"),
        ("category", "Unknown"),
        ("total_amount", "mismatch"),
    )

    source_index = 20
    anomaly_id = 1
    for column, value in mutations:
        for _ in range(5):
            row = valid.iloc[source_index].copy()
            row["order_id"] = f"BAD{anomaly_id:07d}"
            if column == "total_amount":
                row[column] = float(row[column]) + 999.0
            else:
                row[column] = value
            anomalies.append(row)
            source_index += 1
            anomaly_id += 1

    return pd.concat([valid, pd.DataFrame(anomalies)], ignore_index=True)


def generate_dataset(row_count: int, seed: int, contract: dict) -> pd.DataFrame:
    valid = generate_valid_orders(row_count=row_count, seed=seed, contract=contract)
    return inject_controlled_anomalies(valid)


def write_dataset(dataframe: pd.DataFrame, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(output_path, index=False)
    return output_path


def main(row_count: int | None = None, seed: int | None = None) -> Path:
    settings.ensure_directories()
    configure_logging(settings.log_file)
    contract = load_contract(settings.contract_file)
    selected_rows = row_count or settings.source_row_count
    selected_seed = settings.source_seed if seed is None else seed
    dataframe = generate_dataset(selected_rows, selected_seed, contract)
    output = write_dataset(dataframe, settings.raw_file)
    LOGGER.info("Fonte gerada em %s com %s registros", output, len(dataframe))
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Gera pedidos sinteticos com anomalias controladas."
    )
    parser.add_argument("--rows", type=int, default=None)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()
    main(args.rows, args.seed)
