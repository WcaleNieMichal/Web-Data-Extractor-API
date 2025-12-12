"""Scraper dla strony quotes.toscrape.com."""

import csv
import io
import json
from typing import Literal

import requests
from bs4 import BeautifulSoup
from loguru import logger

from config.settings import DEFAULT_HEADERS, REQUEST_TIMEOUT


class QuotesScraper:
    """Scraper do pobierania cytatów z quotes.toscrape.com.

    Pobiera cytaty ze strony głównej lub filtrowane po tagu.

    Attributes:
        tag: Tag do filtrowania (np. "love", "life"). None = wszystkie.
        pages: Liczba stron do pobrania.
        output_format: Format wyjścia - "json", "csv" lub "excel".

    Example:
        >>> scraper = QuotesScraper(tag="love", pages=2)
        >>> json_str = scraper.get()  # domyślnie JSON

        >>> scraper = QuotesScraper(output_format="csv")
        >>> csv_str = scraper.get()

        >>> scraper = QuotesScraper(tag="life", output_format="excel")
        >>> excel_bytes = scraper.get()  # bytes do zapisu
    """

    BASE_URL = "https://quotes.toscrape.com"

    def __init__(
        self,
        tag: str | None = None,
        pages: int | None = None,
        output_format: Literal["json", "csv", "excel"] = "json",
    ):
        """Inicjalizuje scraper.

        Args:
            tag: Tag do filtrowania (np. "love", "inspirational").
                 None = wszystkie cytaty.
            pages: Liczba stron do pobrania. None = wszystkie strony.
            output_format: Format wyjścia - "json", "csv" lub "excel".
                          Domyślnie "json".
        """
        self.tag = tag.lower().strip() if tag else None
        self.pages = pages
        self.output_format = output_format

    def build_url(self, page: int = 1) -> str:
        """Buduje URL dla danej strony.

        Args:
            page: Numer strony.

        Returns:
            Pełny URL do strony.
        """
        if self.tag:
            return f"{self.BASE_URL}/tag/{self.tag}/page/{page}/"
        return f"{self.BASE_URL}/page/{page}/"

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
        """Parsuje HTML i wyciąga dane cytatów.

        Args:
            html: String z HTML do sparsowania.

        Returns:
            Lista słowników z danymi cytatów.
        """
        soup = BeautifulSoup(html, "lxml")
        quotes = []

        for quote_div in soup.select("div.quote"):
            quote = self._parse_quote(quote_div)
            quotes.append(quote)

        return quotes

    def _parse_quote(self, quote_div: BeautifulSoup) -> dict:
        """Parsuje pojedynczy element div z cytatem.

        Args:
            quote_div: Element BeautifulSoup z danymi cytatu.

        Returns:
            Słownik z danymi cytatu.
        """
        # Tekst cytatu
        text_elem = quote_div.select_one("span.text")
        text = text_elem.get_text(strip=True) if text_elem else None
        # Usuń cudzysłowy
        if text:
            text = text.strip("\u201c\u201d\"'")

        # Autor
        author_elem = quote_div.select_one("small.author")
        author = author_elem.get_text(strip=True) if author_elem else None

        # URL autora
        author_link = quote_div.select_one("a[href^='/author/']")
        author_url = author_link.get("href") if author_link else None

        # Tagi
        tag_elems = quote_div.select("div.tags a.tag")
        tags = [tag.get_text(strip=True) for tag in tag_elems]

        return {
            "text": text,
            "author": author,
            "author_url": author_url,
            "tags": tags,
        }

    def _has_next_page(self, html: str) -> bool:
        """Sprawdza czy jest następna strona.

        Args:
            html: HTML strony.

        Returns:
            True jeśli jest następna strona.
        """
        soup = BeautifulSoup(html, "lxml")
        next_btn = soup.select_one("li.next a")
        return next_btn is not None

    def _to_csv(self, quotes: list[dict]) -> str:
        """Konwertuje listę cytatów do formatu CSV.

        Args:
            quotes: Lista słowników z danymi cytatów.

        Returns:
            String CSV.
        """
        if not quotes:
            return ""

        output = io.StringIO()
        # Zamień listę tagów na string
        flat_quotes = []
        for q in quotes:
            flat_q = q.copy()
            flat_q["tags"] = ", ".join(q["tags"])
            flat_quotes.append(flat_q)

        writer = csv.DictWriter(output, fieldnames=flat_quotes[0].keys())
        writer.writeheader()
        writer.writerows(flat_quotes)

        return output.getvalue()

    def _to_excel(self, quotes: list[dict]) -> bytes:
        """Konwertuje listę cytatów do formatu Excel (bytes).

        Args:
            quotes: Lista słowników z danymi cytatów.

        Returns:
            Plik XLSX jako bytes.
        """
        import pandas as pd

        # Zamień listę tagów na string
        flat_quotes = []
        for q in quotes:
            flat_q = q.copy()
            flat_q["tags"] = ", ".join(q["tags"])
            flat_quotes.append(flat_q)

        df = pd.DataFrame(flat_quotes)
        output = io.BytesIO()
        df.to_excel(output, index=False)
        return output.getvalue()

    def get(self, html: str | None = None) -> str | bytes:
        """Pobiera cytaty i zwraca w formacie ustawionym w konstruktorze.

        Args:
            html: Opcjonalny HTML do sparsowania (zamiast pobierania).

        Returns:
            JSON string, CSV string lub Excel bytes.

        Example:
            >>> scraper = QuotesScraper(tag="love", pages=2)
            >>> json_str = scraper.get()

            >>> scraper = QuotesScraper(output_format="excel")
            >>> excel_bytes = scraper.get()
        """
        all_quotes = []

        if html:
            all_quotes = self.parse(html)
        else:
            page = 1
            max_pages = self.pages if self.pages else 100

            while page <= max_pages:
                try:
                    page_html = self.fetch(page)
                    quotes = self.parse(page_html)

                    if not quotes:
                        break

                    all_quotes.extend(quotes)
                    logger.info(f"Page {page}: {len(quotes)} quotes")

                    if self.pages and page >= self.pages:
                        break

                    if not self._has_next_page(page_html):
                        break

                    page += 1

                except requests.RequestException as e:
                    logger.debug(f"Page {page} not found: {e}")
                    break

        logger.info(f"Total quotes: {len(all_quotes)}")

        if self.output_format == "csv":
            return self._to_csv(all_quotes)
        elif self.output_format == "excel":
            return self._to_excel(all_quotes)

        return json.dumps(all_quotes, ensure_ascii=False, indent=2)
