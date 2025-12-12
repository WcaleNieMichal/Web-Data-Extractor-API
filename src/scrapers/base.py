from abc import ABC, abstractmethod
from typing import Any, Generator

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger

from config.settings import (
    DEFAULT_HEADERS,
    REQUEST_TIMEOUT,
    REQUEST_DELAY,
    MAX_RETRIES,
    PROXY_URL,
)


class BaseScraper(ABC):
    """Base class for all scrapers."""

    def __init__(self, use_random_ua: bool = True):
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self.use_random_ua = use_random_ua
        self.ua = UserAgent() if use_random_ua else None

        if PROXY_URL:
            self.session.proxies = {"http": PROXY_URL, "https": PROXY_URL}

    def _get_headers(self) -> dict:
        headers = DEFAULT_HEADERS.copy()
        if self.use_random_ua and self.ua:
            headers["User-Agent"] = self.ua.random
        return headers

    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def fetch(self, url: str) -> BeautifulSoup:
        """Fetch URL and return BeautifulSoup object."""
        logger.debug(f"Fetching: {url}")
        response = self.session.get(
            url,
            headers=self._get_headers(),
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return BeautifulSoup(response.text, "lxml")

    @abstractmethod
    def parse(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        """Parse the page and extract data."""
        pass

    @abstractmethod
    def get_urls(self) -> Generator[str, None, None]:
        """Generate URLs to scrape."""
        pass

    def run(self) -> list[dict[str, Any]]:
        """Run the scraper."""
        all_data = []
        for url in self.get_urls():
            try:
                soup = self.fetch(url)
                data = self.parse(soup)
                all_data.extend(data)
                logger.info(f"Scraped {len(data)} items from {url}")
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
        return all_data

    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
