"""CLI dla scraperów.

Przykłady użycia:
    python main.py                    # Tryb interaktywny
    python main.py mystery            # Kategoria Mystery (books)
    python main.py travel --pages 3   # Travel, 3 strony
    python main.py --format csv       # Wyjście jako CSV
"""

import argparse
from pathlib import Path
from typing import Literal

from src.scrapers.books_scraper import BooksScraper
from src.scrapers.quotes_scraper import QuotesScraper
from src.scrapers.oscars_scraper import OscarsScraper
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


def interactive_mode_full() -> dict:
    """Tryb interaktywny z wyborem scrapera.

    Returns:
        Dict z parametrami scrapera.
    """
    print("\n=== Scraper - Tryb interaktywny ===\n")

    # Wybór scrapera
    print("Wybierz scraper:")
    print("  1. BooksScraper (books.toscrape.com)")
    print("  2. QuotesScraper (quotes.toscrape.com)")
    print("  3. OscarsScraper (scrapethissite.com)")
    scraper_input = input("\nWybierz [1/2/3]: ").strip()

    scraper_map = {"1": "books", "2": "quotes", "3": "oscars"}
    scraper_type = scraper_map.get(scraper_input, "books")

    print()
    filter_value = None
    pages = None

    if scraper_type == "books":
        # Kategoria
        print("Dostępne kategorie:")
        print("  [Enter] - wszystkie książki")
        categories = list(BooksScraper.CATEGORIES.keys())
        for i in range(0, len(categories), 4):
            row = categories[i:i+4]
            print("  " + ", ".join(row))
        filter_input = input("\nKategoria: ").strip()
        filter_value = filter_input if filter_input else None

        # Liczba stron
        print("\nLiczba stron do pobrania:")
        print("  [Enter] - wszystkie strony")
        pages_input = input("Liczba stron: ").strip()
        pages = int(pages_input) if pages_input.isdigit() else None

    elif scraper_type == "quotes":
        # Tag
        print("Filtr po tagu:")
        print("  [Enter] - wszystkie cytaty")
        print("  Przykłady: love, life, inspirational, humor, ...")
        filter_input = input("\nTag: ").strip()
        filter_value = filter_input if filter_input else None

        # Liczba stron
        print("\nLiczba stron do pobrania:")
        print("  [Enter] - wszystkie strony")
        pages_input = input("Liczba stron: ").strip()
        pages = int(pages_input) if pages_input.isdigit() else None

    else:  # oscars
        # Rok
        print("Dostępne lata: 2010, 2011, 2012, 2013, 2014, 2015")
        print("  [Enter] - wszystkie lata")
        year_input = input("\nRok: ").strip()
        filter_value = int(year_input) if year_input.isdigit() else None

    # Format
    print("\nFormat wyjścia:")
    print("  1. json (domyślnie)")
    print("  2. csv")
    print("  3. excel")
    format_input = input("Wybierz [1/2/3]: ").strip()
    format_map = {"1": "json", "2": "csv", "3": "excel"}
    output_format = format_map.get(format_input, "json")

    print()
    return {
        "scraper_type": scraper_type,
        "filter": filter_value,
        "pages": pages,
        "output_format": output_format,
    }


def has_cli_args() -> bool:
    """Sprawdza czy podano argumenty CLI (poza nazwą skryptu)."""
    import sys
    return len(sys.argv) > 1


def run_scraper(params: dict) -> str:
    """Uruchamia wybrany scraper i zapisuje wynik.

    Args:
        params: Słownik z parametrami scrapera.

    Returns:
        Komunikat o zapisaniu pliku.
    """
    output_format = params["output_format"]
    pages = params["pages"]
    scraper_type = params["scraper_type"]

    if scraper_type == "books":
        scraper = BooksScraper(
            category=params["filter"],
            pages=pages,
            output_format=output_format,
        )
        filename = "books"
        item_name = "książek"
    elif scraper_type == "quotes":
        scraper = QuotesScraper(
            tag=params["filter"],
            pages=pages,
            output_format=output_format,
        )
        filename = "quotes"
        item_name = "cytatów"
    else:  # oscars
        scraper = OscarsScraper(
            year=params["filter"],
            output_format=output_format,
        )
        filename = "oscars"
        item_name = "filmów"

    data = scraper.get()

    # Zapisz do pliku
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    ext_map = {"json": "json", "csv": "csv", "excel": "xlsx"}
    ext = ext_map[output_format]
    filepath = output_dir / f"{filename}.{ext}"

    if output_format == "excel":
        filepath.write_bytes(data)
    else:
        filepath.write_text(data, encoding="utf-8")

    # Policz elementy
    if output_format == "json":
        import json
        count = len(json.loads(data))
    elif output_format == "csv":
        count = len(data.strip().split("\n")) - 1 if data.strip() else 0
    else:
        count = "?"

    return f"Zapisano {count} {item_name} do: {filepath}"


def main():
    """Główna funkcja CLI."""
    setup_logger()

    if has_cli_args():
        # Stary tryb - tylko BooksScraper
        args = parse_args()
        result = run_cli(
            category=args.category,
            pages=args.pages,
            output_format=args.format,
        )
    else:
        # Nowy tryb interaktywny z wyborem scrapera
        params = interactive_mode_full()
        result = run_scraper(params)

    print(result)


if __name__ == "__main__":
    main()
