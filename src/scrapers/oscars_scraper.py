"""Scraper dla strony scrapethissite.com - filmy oscarowe."""

import csv
import io
import json
from typing import Literal

import requests
from loguru import logger

from config.settings import DEFAULT_HEADERS, REQUEST_TIMEOUT


class OscarsScraper:
    """Scraper do pobierania danych o filmach oscarowych.

    Pobiera dane z API AJAX strony scrapethissite.com.

    Attributes:
        year: Rok ceremonii (2010-2015). None = wszystkie lata.
        output_format: Format wyjścia - "json", "csv" lub "excel".

    Example:
        >>> scraper = OscarsScraper(year=2015)
        >>> json_str = scraper.get()  # domyślnie JSON

        >>> scraper = OscarsScraper(output_format="csv")
        >>> csv_str = scraper.get()  # wszystkie lata

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
        """Inicjalizuje scraper.

        Args:
            year: Rok ceremonii (2010-2015). None = wszystkie lata.
            output_format: Format wyjścia - "json", "csv" lub "excel".
                          Domyślnie "json".

        Raises:
            ValueError: Gdy rok jest poza zakresem 2010-2015.
        """
        if year is not None:
            self._validate_year(year)
        self.year = year
        self.output_format = output_format

    def _validate_year(self, year: int) -> None:
        """Waliduje rok.

        Args:
            year: Rok do walidacji.

        Raises:
            ValueError: Gdy rok jest poza zakresem.
        """
        if year not in self.AVAILABLE_YEARS:
            available = ", ".join(str(y) for y in self.AVAILABLE_YEARS)
            raise ValueError(
                f"Niepoprawny rok: {year}. "
                f"Dostępne: {available}"
            )

    def build_url(self, year: int) -> str:
        """Buduje URL dla danego roku.

        Args:
            year: Rok ceremonii.

        Returns:
            Pełny URL do API.
        """
        return f"{self.BASE_URL}?ajax=true&year={year}"

    def fetch(self, year: int) -> list[dict]:
        """Pobiera dane z API dla danego roku.

        Args:
            year: Rok ceremonii.

        Returns:
            Lista słowników z danymi filmów.

        Raises:
            requests.RequestException: Gdy nie udało się pobrać danych.
        """
        url = self.build_url(year)
        logger.debug(f"Fetching: {url}")

        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        return response.json()

    def _clean_film(self, film: dict) -> dict:
        """Czyści i normalizuje dane filmu.

        Args:
            film: Surowe dane filmu z API.

        Returns:
            Oczyszczony słownik z danymi filmu.
        """
        return {
            "title": film.get("title", "").strip(),
            "year": film.get("year"),
            "awards": film.get("awards", 0),
            "nominations": film.get("nominations", 0),
            "best_picture": film.get("best_picture", False),
        }

    def _to_csv(self, films: list[dict]) -> str:
        """Konwertuje listę filmów do formatu CSV.

        Args:
            films: Lista słowników z danymi filmów.

        Returns:
            String CSV.
        """
        if not films:
            return ""

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=films[0].keys())
        writer.writeheader()
        writer.writerows(films)

        return output.getvalue()

    def _to_excel(self, films: list[dict]) -> bytes:
        """Konwertuje listę filmów do formatu Excel (bytes).

        Args:
            films: Lista słowników z danymi filmów.

        Returns:
            Plik XLSX jako bytes.
        """
        import pandas as pd

        df = pd.DataFrame(films)
        output = io.BytesIO()
        df.to_excel(output, index=False)
        return output.getvalue()

    def get(self) -> str | bytes:
        """Pobiera filmy i zwraca w formacie ustawionym w konstruktorze.

        Returns:
            JSON string, CSV string lub Excel bytes.

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
