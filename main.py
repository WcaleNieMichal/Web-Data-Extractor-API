"""CLI dla BooksScraper.

Przykłady użycia:
    python main.py                    # Strona główna, JSON
    python main.py mystery_3          # Kategoria Mystery
    python main.py travel_2 --pages 3 # Travel, 3 strony
    python main.py --format csv       # Wyjście jako CSV
"""

import argparse
from pathlib import Path
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
  python main.py --format excel     # Wyjście jako Excel

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


def run_cli(
    category: str | None,
    pages: int | None,
    output_format: Literal["json", "csv", "excel"],
) -> str:
    """Uruchamia scraper i zapisuje wynik do pliku.

    Args:
        category: Slug kategorii lub None dla strony głównej.
        pages: Liczba stron do pobrania.
        output_format: Format wyjścia.

    Returns:
        Komunikat o zapisaniu pliku.
    """
    scraper = BooksScraper(
        category=category,
        pages=pages,
        output_format=output_format,
    )

    data = scraper.get()

    # Zapisz do pliku
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    ext_map = {"json": "json", "csv": "csv", "excel": "xlsx"}
    ext = ext_map[output_format]
    filepath = output_dir / f"books.{ext}"

    if output_format == "excel":
        filepath.write_bytes(data)
    else:
        filepath.write_text(data, encoding="utf-8")

    # Policz książki (parsuj JSON dla liczby)
    if output_format == "json":
        import json
        count = len(json.loads(data))
    elif output_format == "csv":
        count = len(data.strip().split("\n")) - 1 if data.strip() else 0
    else:
        count = "?"

    return f"Zapisano {count} książek do: {filepath}"


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
