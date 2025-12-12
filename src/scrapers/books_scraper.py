"""Scraper for books.toscrape.com website."""

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
    """Scraper for fetching book data from books.toscrape.com.

    Fetches books from selected category or homepage.

    Attributes:
        category: Category slug (e.g. "travel_2"). Defaults to "books_1".
        pages: Number of pages to fetch.
        output_format: Output format - "json", "csv" or "excel".

    Example:
        >>> scraper = BooksScraper(category="mystery", pages=2)
        >>> json_str = scraper.get()  # default JSON

        >>> scraper = BooksScraper(category="horror", output_format="csv")
        >>> csv_str = scraper.get()

        >>> scraper = BooksScraper(output_format="excel")
        >>> excel_bytes = scraper.get()  # bytes for saving
    """

    BASE_URL = "https://books.toscrape.com/catalogue/category/books/{category}"

    CATEGORIES = {
        "all": "books_1",
        "travel": "travel_2",
        "mystery": "mystery_3",
        "historical fiction": "historical-fiction_4",
        "sequential art": "sequential-art_5",
        "classics": "classics_6",
        "philosophy": "philosophy_7",
        "romance": "romance_8",
        "womens fiction": "womens-fiction_9",
        "fiction": "fiction_10",
        "childrens": "childrens_11",
        "religion": "religion_12",
        "nonfiction": "nonfiction_13",
        "music": "music_14",
        "science fiction": "science-fiction_16",
        "sports and games": "sports-and-games_17",
        "fantasy": "fantasy_19",
        "new adult": "new-adult_20",
        "young adult": "young-adult_21",
        "science": "science_22",
        "poetry": "poetry_23",
        "paranormal": "paranormal_24",
        "art": "art_25",
        "psychology": "psychology_26",
        "autobiography": "autobiography_27",
        "parenting": "parenting_28",
        "adult fiction": "adult-fiction_29",
        "humor": "humor_30",
        "horror": "horror_31",
        "history": "history_32",
        "food and drink": "food-and-drink_33",
        "christian fiction": "christian-fiction_34",
        "business": "business_35",
        "biography": "biography_36",
        "thriller": "thriller_37",
        "contemporary": "contemporary_38",
        "spirituality": "spirituality_39",
        "academic": "academic_40",
        "self help": "self-help_41",
        "historical": "historical_42",
        "christian": "christian_43",
        "suspense": "suspense_44",
        "short stories": "short-stories_45",
        "novels": "novels_46",
        "health": "health_47",
        "politics": "politics_48",
        "cultural": "cultural_49",
        "erotica": "erotica_50",
        "crime": "crime_51",
    }

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
        """Initializes scraper.

        Args:
            category: Category name (e.g. "mystery", "horror") or slug.
                      None = all books (books_1).
            pages: Number of pages to fetch. None = all pages.
            output_format: Output format - "json", "csv" or "excel".
                          Defaults to "json".
        """
        self.category = self._resolve_category(category)
        self.pages = pages  # None = auto (all pages)
        self.output_format = output_format

    def _resolve_category(self, category: str | None) -> str:
        """Converts category name to slug.

        Args:
            category: Category name or slug.

        Returns:
            Category slug (e.g. "mystery_3").

        Raises:
            ValueError: When category doesn't exist.
        """
        if not category:
            return "books_1"

        key = category.lower().strip()

        # Category name (e.g. "mystery")
        if key in self.CATEGORIES:
            return self.CATEGORIES[key]

        # Category slug (e.g. "mystery_3")
        if key in self.CATEGORIES.values():
            return key

        # Unknown category
        available = ", ".join(sorted(self.CATEGORIES.keys())[:10])
        raise ValueError(
            f"Unknown category: '{category}'. "
            f"Available: {available}, ..."
        )

    def build_url(self, page: int = 1) -> str:
        """Builds URL for given category page.

        Args:
            page: Page number.

        Returns:
            Full URL to page.
        """
        base = self.BASE_URL.format(category=self.category)
        if page == 1:
            return f"{base}/index.html"
        return f"{base}/page-{page}.html"

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
        """Parses HTML and extracts book data.

        Args:
            html: HTML string to parse.

        Returns:
            List of dictionaries with book data.
        """
        soup = BeautifulSoup(html, "lxml")
        books = []

        for article in soup.select("article.product_pod"):
            book = self._parse_book(article)
            books.append(book)

        return books

    def _parse_book(self, article: BeautifulSoup) -> dict:
        """Parses single article element with book.

        Args:
            article: BeautifulSoup element with book data.

        Returns:
            Dictionary with book data.
        """
        # Title
        title_elem = article.select_one("h3 a")
        title = title_elem.get("title") if title_elem else None

        # URL
        url = title_elem.get("href") if title_elem else None

        # Price
        price_elem = article.select_one(".price_color")
        price = price_elem.get_text(strip=True) if price_elem else None
        price_float = self._parse_price(price)

        # Rating
        rating_elem = article.select_one(".star-rating")
        rating = self._parse_rating(rating_elem)

        # Availability
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
        """Parses price from string to float.

        Args:
            price: Price as string (e.g. "£51.77").

        Returns:
            Price as float or None.
        """
        if not price:
            return None

        match = re.search(r"[\d.]+", price)
        if match:
            return float(match.group())
        return None

    def _parse_rating(self, rating_elem) -> int | None:
        """Parses rating from HTML element.

        Args:
            rating_elem: BeautifulSoup element with star-rating class.

        Returns:
            Rating as int (1-5) or None.
        """
        if not rating_elem:
            return None

        classes = rating_elem.get("class", [])
        for cls in classes:
            if cls in self.RATING_MAP:
                return self.RATING_MAP[cls]
        return None

    def _parse_availability(self, availability_elem) -> bool:
        """Parses availability from HTML element.

        Args:
            availability_elem: Element with availability info.

        Returns:
            True if in stock, False otherwise.
        """
        if not availability_elem:
            return False

        text = availability_elem.get_text(strip=True).lower()
        return "in stock" in text

    def _to_csv(self, books: list[dict]) -> str:
        """Converts book list to CSV format.

        Args:
            books: List of dictionaries with book data.

        Returns:
            CSV string.
        """
        if not books:
            return ""

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=books[0].keys())
        writer.writeheader()
        writer.writerows(books)

        return output.getvalue()

    def _to_excel(self, books: list[dict]) -> bytes:
        """Converts book list to Excel format (bytes).

        Args:
            books: List of dictionaries with book data.

        Returns:
            XLSX file as bytes.
        """
        import pandas as pd

        df = pd.DataFrame(books)
        output = io.BytesIO()
        df.to_excel(output, index=False)
        return output.getvalue()

    def get(self, html: str | None = None) -> str | bytes:
        """Fetches books and returns in format set in constructor.

        Args:
            html: Optional HTML to parse (instead of fetching).

        Returns:
            JSON string, CSV string or Excel bytes.

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
            max_pages = self.pages if self.pages else 100  # Safety limit

            while page <= max_pages:
                try:
                    page_html = self.fetch(page)
                    books = self.parse(page_html)

                    if not books:
                        break  # No books = end of pagination

                    all_books.extend(books)
                    logger.info(f"Page {page}: {len(books)} books")

                    # If pages=None (auto), continue
                    # If pages set, check limit
                    if self.pages and page >= self.pages:
                        break

                    page += 1

                except requests.RequestException as e:
                    logger.debug(f"Page {page} not found: {e}")
                    break  # 404 = end of pagination

        logger.info(f"Total books: {len(all_books)}")

        if self.output_format == "csv":
            return self._to_csv(all_books)
        elif self.output_format == "excel":
            return self._to_excel(all_books)

        return json.dumps(all_books, ensure_ascii=False, indent=2)
