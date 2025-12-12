"""Scraper dla strony books.toscrape.com."""

import csv
import io
import json
import re
from typing import Literal

import requests
from bs4 import BeautifulSoup
from loguru import logger

from config.settings import DEFAULT_HEADERS, REQUEST_TIMEOUT


class BooksScraper:
    """Scraper do pobierania danych książek z books.toscrape.com.

    Pobiera książki z wybranej kategorii lub strony głównej.

    Attributes:
        category: Slug kategorii (np. "travel_2"). Domyślnie "books_1".
        pages: Liczba stron do pobrania.
        output_format: Format wyjścia - "json", "csv" lub "excel".

    Example:
        >>> scraper = BooksScraper(category="mystery_3", pages=2)
        >>> json_str = scraper.get()  # domyślnie JSON

        >>> scraper = BooksScraper(output_format="csv")
        >>> csv_str = scraper.get()

        >>> scraper = BooksScraper(output_format="excel")
        >>> excel_bytes = scraper.get()  # bytes do zapisu
    """

    BASE_URL = "https://books.toscrape.com/catalogue/category/{category}/page-{page}.html"

    RATING_MAP = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    def __init__(
        self,
        category: str | None = None,
        pages: int | None = None,
        output_format: Literal["json", "csv", "excel"] = "json",
    ):
        """Inicjalizuje scraper.

        Args:
            category: Slug kategorii (np. "travel_2", "mystery_3").
                      None = strona główna (books_1).
            pages: Liczba stron do pobrania. None = wszystkie strony.
            output_format: Format wyjścia - "json", "csv" lub "excel".
                          Domyślnie "json".
        """
        self.category = category if category else "books_1"
        self.pages = pages  # None = auto (wszystkie strony)
        self.output_format = output_format

    def build_url(self, page: int = 1) -> str:
        """Buduje URL dla danej strony kategorii.

        Args:
            page: Numer strony.

        Returns:
            Pełny URL do strony.
        """
        return self.BASE_URL.format(category=self.category, page=page)

    def fetch(self, page: int = 1) -> str:
        """Pobiera HTML strony.

        Args:
            page: Numer strony do pobrania.

        Returns:
            HTML strony jako string.

        Raises:
            requests.RequestException: Gdy nie udało się pobrać strony.
        """
        url = self.build_url(page)
        logger.debug(f"Fetching: {url}")

        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        response.encoding = "utf-8"

        return response.text

    def parse(self, html: str) -> list[dict]:
        """Parsuje HTML i wyciąga dane książek.

        Args:
            html: String z HTML do sparsowania.

        Returns:
            Lista słowników z danymi książek.
        """
        soup = BeautifulSoup(html, "lxml")
        books = []

        for article in soup.select("article.product_pod"):
            book = self._parse_book(article)
            books.append(book)

        return books

    def _parse_book(self, article: BeautifulSoup) -> dict:
        """Parsuje pojedynczy element article z książką.

        Args:
            article: Element BeautifulSoup z danymi książki.

        Returns:
            Słownik z danymi książki.
        """
        # Tytuł
        title_elem = article.select_one("h3 a")
        title = title_elem.get("title") if title_elem else None

        # URL
        url = title_elem.get("href") if title_elem else None

        # Cena
        price_elem = article.select_one(".price_color")
        price = price_elem.get_text(strip=True) if price_elem else None
        price_float = self._parse_price(price)

        # Rating
        rating_elem = article.select_one(".star-rating")
        rating = self._parse_rating(rating_elem)

        # Dostępność
        availability_elem = article.select_one(".availability")
        in_stock = self._parse_availability(availability_elem)

        return {
            "title": title,
            "price": price,
            "price_float": price_float,
            "rating": rating,
            "in_stock": in_stock,
            "url": url,
        }

    def _parse_price(self, price: str | None) -> float | None:
        """Parsuje cenę z stringa na float.

        Args:
            price: Cena jako string (np. "£51.77").

        Returns:
            Cena jako float lub None.
        """
        if not price:
            return None

        match = re.search(r"[\d.]+", price)
        if match:
            return float(match.group())
        return None

    def _parse_rating(self, rating_elem) -> int | None:
        """Parsuje rating z elementu HTML.

        Args:
            rating_elem: Element BeautifulSoup z klasą star-rating.

        Returns:
            Rating jako int (1-5) lub None.
        """
        if not rating_elem:
            return None

        classes = rating_elem.get("class", [])
        for cls in classes:
            if cls in self.RATING_MAP:
                return self.RATING_MAP[cls]
        return None

    def _parse_availability(self, availability_elem) -> bool:
        """Parsuje dostępność z elementu HTML.

        Args:
            availability_elem: Element z informacją o dostępności.

        Returns:
            True jeśli w magazynie, False w przeciwnym razie.
        """
        if not availability_elem:
            return False

        text = availability_elem.get_text(strip=True).lower()
        return "in stock" in text

    def _to_csv(self, books: list[dict]) -> str:
        """Konwertuje listę książek do formatu CSV.

        Args:
            books: Lista słowników z danymi książek.

        Returns:
            String CSV.
        """
        if not books:
            return ""

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=books[0].keys())
        writer.writeheader()
        writer.writerows(books)

        return output.getvalue()

    def _to_excel(self, books: list[dict]) -> bytes:
        """Konwertuje listę książek do formatu Excel (bytes).

        Args:
            books: Lista słowników z danymi książek.

        Returns:
            Plik XLSX jako bytes.
        """
        import pandas as pd

        df = pd.DataFrame(books)
        output = io.BytesIO()
        df.to_excel(output, index=False)
        return output.getvalue()

    def get(self, html: str | None = None) -> str | bytes:
        """Pobiera książki i zwraca w formacie ustawionym w konstruktorze.

        Args:
            html: Opcjonalny HTML do sparsowania (zamiast pobierania).

        Returns:
            JSON string, CSV string lub Excel bytes.

        Example:
            >>> scraper = BooksScraper(category="travel_2", pages=3)
            >>> json_str = scraper.get()

            >>> scraper = BooksScraper(output_format="excel")
            >>> excel_bytes = scraper.get()
        """
        all_books = []

        if html:
            all_books = self.parse(html)
        else:
            page = 1
            max_pages = self.pages if self.pages else 100  # Limit bezpieczeństwa

            while page <= max_pages:
                try:
                    page_html = self.fetch(page)
                    books = self.parse(page_html)

                    if not books:
                        break  # Brak książek = koniec paginacji

                    all_books.extend(books)
                    logger.info(f"Page {page}: {len(books)} books")

                    # Jeśli pages=None (auto), kontynuuj
                    # Jeśli pages ustawione, sprawdź limit
                    if self.pages and page >= self.pages:
                        break

                    page += 1

                except requests.RequestException as e:
                    logger.debug(f"Page {page} not found: {e}")
                    break  # 404 = koniec paginacji

        logger.info(f"Total books: {len(all_books)}")

        if self.output_format == "csv":
            return self._to_csv(all_books)
        elif self.output_format == "excel":
            return self._to_excel(all_books)

        return json.dumps(all_books, ensure_ascii=False, indent=2)
