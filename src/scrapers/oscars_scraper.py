"""Scraper for scrapethissite.com - Oscar-winning films."""

import csv
import io
import json
from typing import Literal

import requests
from loguru import logger

from config.settings import DEFAULT_HEADERS, REQUEST_TIMEOUT


class OscarsScraper:
    """Scraper for fetching Oscar-winning film data.

    Fetches data from AJAX API at scrapethissite.com.

    Attributes:
        year: Ceremony year (2010-2015). None = all years.
        output_format: Output format - "json", "csv" or "excel".

    Example:
        >>> scraper = OscarsScraper(year=2015)
        >>> json_str = scraper.get()  # default JSON

        >>> scraper = OscarsScraper(output_format="csv")
        >>> csv_str = scraper.get()  # all years

        >>> scraper = OscarsScraper(year=2014, output_format="excel")
        >>> excel_bytes = scraper.get()
    """

    BASE_URL = "https://www.scrapethissite.com/pages/ajax-javascript/"
    AVAILABLE_YEARS = [2010, 2011, 2012, 2013, 2014, 2015]

    def __init__(
        self,
        year: int | None = None,
        output_format: Literal["json", "csv", "excel"] = "json",
    ):
        """Initializes scraper.

        Args:
            year: Ceremony year (2010-2015). None = all years.
            output_format: Output format - "json", "csv" or "excel".
                          Defaults to "json".

        Raises:
            ValueError: When year is outside 2010-2015 range.
        """
        if year is not None:
            self._validate_year(year)
        self.year = year
        self.output_format = output_format

    def _validate_year(self, year: int) -> None:
        """Validates year.

        Args:
            year: Year to validate.

        Raises:
            ValueError: When year is outside range.
        """
        if year not in self.AVAILABLE_YEARS:
            available = ", ".join(str(y) for y in self.AVAILABLE_YEARS)
            raise ValueError(
                f"Invalid year: {year}. "
                f"Available: {available}"
            )

    def build_url(self, year: int) -> str:
        """Builds URL for given year.

        Args:
            year: Ceremony year.

        Returns:
            Full URL to API.
        """
        return f"{self.BASE_URL}?ajax=true&year={year}"

    def fetch(self, year: int) -> list[dict]:
        """Fetches data from API for given year.

        Args:
            year: Ceremony year.

        Returns:
            List of dictionaries with film data.

        Raises:
            requests.RequestException: When data fetch fails.
        """
        url = self.build_url(year)
        logger.debug(f"Fetching: {url}")

        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        return response.json()

    def _clean_film(self, film: dict) -> dict:
        """Cleans and normalizes film data.

        Args:
            film: Raw film data from API.

        Returns:
            Cleaned dictionary with film data.
        """
        return {
            "title": film.get("title", "").strip(),
            "year": film.get("year"),
            "awards": film.get("awards", 0),
            "nominations": film.get("nominations", 0),
            "best_picture": film.get("best_picture", False),
        }

    def _to_csv(self, films: list[dict]) -> str:
        """Converts film list to CSV format.

        Args:
            films: List of dictionaries with film data.

        Returns:
            CSV string.
        """
        if not films:
            return ""

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=films[0].keys(), delimiter=";")
        writer.writeheader()
        writer.writerows(films)

        return output.getvalue()

    def _to_excel(self, films: list[dict]) -> bytes:
        """Converts film list to Excel format (bytes).

        Args:
            films: List of dictionaries with film data.

        Returns:
            XLSX file as bytes.
        """
        import pandas as pd

        df = pd.DataFrame(films)
        output = io.BytesIO()
        df.to_excel(output, index=False)
        return output.getvalue()

    def get(self) -> str | bytes:
        """Fetches films and returns in format set in constructor.

        Returns:
            JSON string, CSV string or Excel bytes.

        Example:
            >>> scraper = OscarsScraper(year=2015)
            >>> json_str = scraper.get()

            >>> scraper = OscarsScraper(output_format="excel")
            >>> excel_bytes = scraper.get()
        """
        all_films = []

        years_to_fetch = [self.year] if self.year else self.AVAILABLE_YEARS

        for year in years_to_fetch:
            try:
                films = self.fetch(year)
                cleaned_films = [self._clean_film(f) for f in films]
                all_films.extend(cleaned_films)
                logger.info(f"Year {year}: {len(cleaned_films)} films")
            except requests.RequestException as e:
                logger.error(f"Failed to fetch year {year}: {e}")

        logger.info(f"Total films: {len(all_films)}")

        if self.output_format == "csv":
            return self._to_csv(all_films)
        elif self.output_format == "excel":
            return self._to_excel(all_films)

        return json.dumps(all_films, ensure_ascii=False, indent=2)
