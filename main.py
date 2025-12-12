"""CLI dla BooksScraper.

Przykłady użycia:
    python main.py                    # Strona główna
    python main.py mystery_3          # Kategoria Mystery
    python main.py travel_2 --pages 3 # Travel, 3 strony
    python main.py --format json      # Wyjście jako JSON
"""

import argparse
import csv
import io
import json
from typing import Literal

from src.scrapers.books_scraper import BooksScraper
from src.utils import setup_logger


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parsuje argumenty linii poleceń.

    Args:
        args: Lista argumentów. None = sys.argv.

    Returns:
        Namespace z argumentami.
    """
    parser = argparse.ArgumentParser(
        description="Scraper książek z books.toscrape.com",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady:
  python main.py                    # Wszystkie książki (strona główna)
  python main.py mystery_3          # Kategoria Mystery
  python main.py travel_2 --pages 3 # Travel, 3 strony
  python main.py --format json      # Wyjście jako JSON
  python main.py --format csv       # Wyjście jako CSV

Dostępne kategorie:
  books_1 (wszystkie), travel_2, mystery_3, science-fiction_16,
  fantasy_19, horror_31, i więcej...
        """,
    )

    parser.add_argument(
        "category",
        nargs="?",
        default=None,
        help="Slug kategorii (np. mystery_3). Domyślnie: wszystkie książki.",
    )

    parser.add_argument(
        "--pages",
        type=int,
        default=None,
        help="Liczba stron do pobrania (domyślnie: wszystkie)",
    )

    parser.add_argument(
        "--format",
        choices=["json", "csv", "excel"],
        default="json",
        help="Format wyjścia (domyślnie: json)",
    )

    return parser.parse_args(args)


def format_output(
    books: list[dict],
    output_format: Literal["json", "csv", "excel"],
) -> str:
    """Formatuje listę książek do wybranego formatu.

    Args:
        books: Lista słowników z danymi książek.
        output_format: Format wyjścia - "json", "csv" lub "excel".

    Returns:
        Sformatowany string (json/csv) lub ścieżka do pliku (excel).
    """
    if not books:
        return "[]" if output_format == "json" else ""

    if output_format == "json":
        return json.dumps(books, ensure_ascii=False, indent=2)

    if output_format == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=books[0].keys())
        writer.writeheader()
        writer.writerows(books)
        return output.getvalue()

    if output_format == "excel":
        import pandas as pd
        from pathlib import Path

        df = pd.DataFrame(books)
        filepath = Path("data/processed/books.xlsx")
        filepath.parent.mkdir(parents=True, exist_ok=True)
        df.to_excel(filepath, index=False)
        return f"Zapisano {len(books)} książek do: {filepath}"

    return json.dumps(books, ensure_ascii=False, indent=2)


def run_cli(
    category: str | None,
    pages: int | None,
    output_format: Literal["json", "csv", "excel"],
) -> str:
    """Uruchamia scraper i zwraca sformatowane wyjście.

    Args:
        category: Slug kategorii lub None dla strony głównej.
        pages: Liczba stron do pobrania.
        output_format: Format wyjścia.

    Returns:
        Sformatowany string z wynikami.
    """
    scraper = BooksScraper(category=category, pages=pages)
    books = scraper.get(output_format="dict")

    return format_output(books, output_format)


def main():
    """Główna funkcja CLI."""
    setup_logger()

    args = parse_args()
    result = run_cli(
        category=args.category,
        pages=args.pages,
        output_format=args.format,
    )

    print(result)


if __name__ == "__main__":
    main()
