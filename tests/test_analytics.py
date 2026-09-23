from __future__ import annotations

from src.analytics import build_analytics
from src.generate_data import generate_dataset
from src.transform import split_valid_and_quarantine


def test_analytics_builds_five_business_views(contract: dict) -> None:
    clean, _, _ = split_valid_and_quarantine(generate_dataset(100, 42, contract), contract)

    reports = build_analytics(clean)

    assert set(reports) == {
        "revenue_by_category",
        "revenue_by_product",
        "daily_sales",
        "delivery_status",
        "customer_summary",
    }
    assert reports["revenue_by_category"]["recognized_revenue"].sum() > 0
    assert reports["delivery_status"]["orders"].sum() == 100


def test_cancelled_orders_are_excluded_from_recognized_revenue(contract: dict) -> None:
    clean, _, _ = split_valid_and_quarantine(generate_dataset(100, 42, contract), contract)
    reports = build_analytics(clean)
    expected = clean.loc[clean["delivery_status"] != "Cancelled", "total_amount"].sum()

    actual = reports["revenue_by_category"]["recognized_revenue"].sum()

    assert round(actual, 2) == round(expected, 2)
