"""CLI dla BooksScraper.

Przykłady użycia:
    python main.py                    # Tryb interaktywny
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
  python main.py                    # Tryb interaktywny
  python main.py mystery            # Kategoria Mystery
  python main.py travel --pages 3   # Travel, 3 strony
  python main.py --format csv       # Wyjście jako CSV
  python main.py --format excel     # Wyjście jako Excel

Dostępne kategorie:
  mystery, horror, thriller, crime, fantasy, romance, fiction,
  science fiction, history, biography, i więcej...
        """,
    )

    parser.add_argument(
        "category",
        nargs="?",
        default=None,
        help="Nazwa kategorii (np. mystery, horror). Domyślnie: wszystkie.",
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


def interactive_mode() -> tuple[str | None, int | None, str]:
    """Tryb interaktywny - pyta użytkownika o parametry.

    Returns:
        Tuple (category, pages, output_format).
    """
    print("\n=== BooksScraper - Tryb interaktywny ===\n")

    # Kategoria
    print("Dostępne kategorie:")
    print("  [Enter] - wszystkie książki")
    categories = list(BooksScraper.CATEGORIES.keys())
    # Wyświetl w kolumnach
    for i in range(0, len(categories), 4):
        row = categories[i:i+4]
        print("  " + ", ".join(row))
    category_input = input("\nKategoria: ").strip()
    category = category_input if category_input else None

    # Liczba stron
    print("\nLiczba stron do pobrania:")
    print("  [Enter] - wszystkie strony")
    pages_input = input("Liczba stron: ").strip()
    pages = int(pages_input) if pages_input.isdigit() else None

    # Format
    print("\nFormat wyjścia:")
    print("  1. json (domyślnie)")
    print("  2. csv")
    print("  3. excel")
    format_input = input("Wybierz [1/2/3]: ").strip()
    format_map = {"1": "json", "2": "csv", "3": "excel"}
    output_format = format_map.get(format_input, "json")

    print()
    return category, pages, output_format


def has_cli_args() -> bool:
    """Sprawdza czy podano argumenty CLI (poza nazwą skryptu)."""
    import sys
    return len(sys.argv) > 1


def main():
    """Główna funkcja CLI."""
    setup_logger()

    if has_cli_args():
        args = parse_args()
        category = args.category
        pages = args.pages
        output_format = args.format
    else:
        category, pages, output_format = interactive_mode()

    result = run_cli(
        category=category,
        pages=pages,
        output_format=output_format,
    )

    print(result)


if __name__ == "__main__":
    main()
