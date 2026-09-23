from __future__ import annotations

import pandas as pd
import pandera as pa
from pandera import Check, Column, DataFrameSchema


def build_clean_schema(contract: dict) -> DataFrameSchema:
    domains = contract["domains"]
    thresholds = contract["thresholds"]
    return DataFrameSchema(
        {
            "order_id": Column(str, nullable=False, unique=True),
            "order_date": Column(pa.DateTime, nullable=False),
            "customer_id": Column(str, nullable=False),
            "product_id": Column(str, nullable=False),
            "product_name": Column(str, nullable=False),
            "category": Column(str, Check.isin(domains["category"]), nullable=False),
            "quantity": Column(
                int,
                [
                    Check.ge(thresholds["quantity_min"]),
                    Check.le(thresholds["quantity_max"]),
                ],
                nullable=False,
            ),
            "unit_price": Column(
                float,
                Check.gt(thresholds["unit_price_min_exclusive"]),
                nullable=False,
            ),
            "discount_pct": Column(
                float,
                [
                    Check.ge(thresholds["discount_min"]),
                    Check.le(thresholds["discount_max"]),
                ],
                nullable=False,
            ),
            "payment_method": Column(str, Check.isin(domains["payment_method"]), nullable=False),
            "delivery_status": Column(str, Check.isin(domains["delivery_status"]), nullable=False),
            "country": Column(str, Check.isin(domains["country"]), nullable=False),
            "total_amount": Column(float, Check.gt(0), nullable=False),
        },
        strict=True,
        coerce=False,
        ordered=True,
        name="sales_orders_clean",
    )


def validate_clean_schema(dataframe: pd.DataFrame, contract: dict) -> pd.DataFrame:
    return build_clean_schema(contract).validate(dataframe, lazy=True)
