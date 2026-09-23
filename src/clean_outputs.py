from __future__ import annotations

from src.config import settings


def clean_generated_outputs() -> list[str]:
    generated = [
        settings.raw_file,
        settings.processed_file,
        settings.quarantine_file,
        settings.quality_report_file,
        settings.metrics_file,
        settings.log_file,
        *(
            settings.reports_dir / name
            for name in (
                "revenue_by_category.csv",
                "revenue_by_product.csv",
                "daily_sales.csv",
                "delivery_status.csv",
                "customer_summary.csv",
            )
        ),
    ]
    removed: list[str] = []
    for path in generated:
        if path.exists() and path.is_file():
            path.unlink()
            removed.append(str(path.relative_to(settings.project_root)))
    return removed


def main() -> None:
    removed = clean_generated_outputs()
    print(f"Limpeza concluida: {len(removed)} arquivos gerados removidos.")


if __name__ == "__main__":
    main()
