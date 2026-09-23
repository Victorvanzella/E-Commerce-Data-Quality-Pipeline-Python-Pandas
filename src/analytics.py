from __future__ import annotations

from pathlib import Path

import pandas as pd


def build_analytics(clean: pd.DataFrame) -> dict[str, pd.DataFrame]:
    recognized = clean.loc[clean["delivery_status"] != "Cancelled"].copy()

    revenue_by_category = (
        recognized.groupby("category", as_index=False)
        .agg(
            orders=("order_id", "nunique"),
            units_sold=("quantity", "sum"),
            recognized_revenue=("total_amount", "sum"),
        )
        .sort_values("recognized_revenue", ascending=False)
    )
    revenue_by_category["recognized_revenue"] = revenue_by_category["recognized_revenue"].round(2)

    revenue_by_product = (
        recognized.groupby(["product_id", "product_name", "category"], as_index=False)
        .agg(
            orders=("order_id", "nunique"),
            units_sold=("quantity", "sum"),
            recognized_revenue=("total_amount", "sum"),
        )
        .sort_values("recognized_revenue", ascending=False)
    )
    revenue_by_product["recognized_revenue"] = revenue_by_product["recognized_revenue"].round(2)

    daily_sales = (
        recognized.assign(order_date=recognized["order_date"].dt.strftime("%Y-%m-%d"))
        .groupby("order_date", as_index=False)
        .agg(
            orders=("order_id", "nunique"),
            units_sold=("quantity", "sum"),
            recognized_revenue=("total_amount", "sum"),
        )
        .sort_values("order_date")
    )
    daily_sales["recognized_revenue"] = daily_sales["recognized_revenue"].round(2)

    delivery_status = (
        clean.groupby("delivery_status", as_index=False)
        .agg(orders=("order_id", "nunique"), gross_order_value=("total_amount", "sum"))
        .sort_values("orders", ascending=False)
    )
    delivery_status["gross_order_value"] = delivery_status["gross_order_value"].round(2)

    customer_summary = (
        recognized.groupby(["customer_id", "country"], as_index=False)
        .agg(
            orders=("order_id", "nunique"),
            units_purchased=("quantity", "sum"),
            recognized_revenue=("total_amount", "sum"),
        )
        .sort_values(["recognized_revenue", "orders"], ascending=False)
    )
    customer_summary["recognized_revenue"] = customer_summary["recognized_revenue"].round(2)

    return {
        "revenue_by_category": revenue_by_category,
        "revenue_by_product": revenue_by_product,
        "daily_sales": daily_sales,
        "delivery_status": delivery_status,
        "customer_summary": customer_summary,
    }


def write_analytics(reports: dict[str, pd.DataFrame], output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for name, dataframe in reports.items():
        path = output_dir / f"{name}.csv"
        dataframe.to_csv(path, index=False)
        paths.append(path)
    return paths
