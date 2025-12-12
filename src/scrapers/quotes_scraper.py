"""Scraper for quotes.toscrape.com website."""

import csv
import io
import json
from typing import Literal

import requests
from bs4 import BeautifulSoup
from loguru import logger

from config.settings import DEFAULT_HEADERS, REQUEST_TIMEOUT


class QuotesScraper:
    """Scraper for fetching quotes from quotes.toscrape.com.

    Fetches quotes from homepage or filtered by tag.

    Attributes:
        tag: Tag to filter by (e.g. "love", "life"). None = all quotes.
        pages: Number of pages to fetch.
        output_format: Output format - "json", "csv" or "excel".

    Example:
        >>> scraper = QuotesScraper(tag="love", pages=2)
        >>> json_str = scraper.get()  # default JSON

        >>> scraper = QuotesScraper(output_format="csv")
        >>> csv_str = scraper.get()

        >>> scraper = QuotesScraper(tag="life", output_format="excel")
        >>> excel_bytes = scraper.get()  # bytes for saving
    """

    BASE_URL = "https://quotes.toscrape.com"

    def __init__(
        self,
        tag: str | None = None,
        pages: int | None = None,
        output_format: Literal["json", "csv", "excel"] = "json",
    ):
        """Initializes scraper.

        Args:
            tag: Tag to filter by (e.g. "love", "inspirational").
                 None = all quotes.
            pages: Number of pages to fetch. None = all pages.
            output_format: Output format - "json", "csv" or "excel".
                          Defaults to "json".
        """
        self.tag = tag.lower().strip() if tag else None
        self.pages = pages
        self.output_format = output_format

    def build_url(self, page: int = 1) -> str:
        """Builds URL for given page.

        Args:
            page: Page number.

        Returns:
            Full URL to page.
        """
        if self.tag:
            return f"{self.BASE_URL}/tag/{self.tag}/page/{page}/"
        return f"{self.BASE_URL}/page/{page}/"

    def fetch(self, page: int = 1) -> str:
        """Fetches page HTML.

        Args:
            page: Page number to fetch.

        Returns:
            Page HTML as string.

        Raises:
            requests.RequestException: When page fetch fails.
        """
        url = self.build_url(page)
        logger.debug(f"Fetching: {url}")

        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        response.encoding = "utf-8"

        return response.text

    def parse(self, html: str) -> list[dict]:
        """Parses HTML and extracts quote data.

        Args:
            html: HTML string to parse.

        Returns:
            List of dictionaries with quote data.
        """
        soup = BeautifulSoup(html, "lxml")
        quotes = []

        for quote_div in soup.select("div.quote"):
            quote = self._parse_quote(quote_div)
            quotes.append(quote)

        return quotes

    def _parse_quote(self, quote_div: BeautifulSoup) -> dict:
        """Parses single div element with quote.

        Args:
            quote_div: BeautifulSoup element with quote data.

        Returns:
            Dictionary with quote data.
        """
        # Quote text
        text_elem = quote_div.select_one("span.text")
        text = text_elem.get_text(strip=True) if text_elem else None
        # Remove quotation marks
        if text:
            text = text.strip("\u201c\u201d\"'")

        # Author
        author_elem = quote_div.select_one("small.author")
        author = author_elem.get_text(strip=True) if author_elem else None

        # Author URL
        author_link = quote_div.select_one("a[href^='/author/']")
        author_url = author_link.get("href") if author_link else None

        # Tags
        tag_elems = quote_div.select("div.tags a.tag")
        tags = [tag.get_text(strip=True) for tag in tag_elems]

        return {
            "text": text,
            "author": author,
            "author_url": author_url,
            "tags": tags,
        }

    def _has_next_page(self, html: str) -> bool:
        """Checks if there is a next page.

        Args:
            html: Page HTML.

        Returns:
            True if there is a next page.
        """
        soup = BeautifulSoup(html, "lxml")
        next_btn = soup.select_one("li.next a")
        return next_btn is not None

    def _to_csv(self, quotes: list[dict]) -> str:
        """Converts quote list to CSV format.

        Args:
            quotes: List of dictionaries with quote data.

        Returns:
            CSV string.
        """
        if not quotes:
            return ""

        output = io.StringIO()
        # Convert tags list to string
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
        """Converts quote list to Excel format (bytes).

        Args:
            quotes: List of dictionaries with quote data.

        Returns:
            XLSX file as bytes.
        """
        import pandas as pd

        # Convert tags list to string
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
        """Fetches quotes and returns in format set in constructor.

        Args:
            html: Optional HTML to parse (instead of fetching).

        Returns:
            JSON string, CSV string or Excel bytes.

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
