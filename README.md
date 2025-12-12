# Web Scrapers API

REST API do pobierania danych z różnych stron internetowych. Projekt zgodny z konwencjami REST API.

## Dostępne scrapery

- **Books** - książki z [books.toscrape.com](https://books.toscrape.com)
- **Quotes** - cytaty z [quotes.toscrape.com](https://quotes.toscrape.com)
- **Oscars** - filmy oscarowe z [scrapethissite.com](https://www.scrapethissite.com/pages/ajax-javascript/)

## Struktura projektu

```
├── config/             # Konfiguracja aplikacji
├── data/
│   ├── raw/            # Surowe dane ze scrapingu
│   └── processed/      # Przetworzone dane
├── logs/               # Logi aplikacji
├── src/
│   ├── api/            # FastAPI REST API
│   │   ├── main.py     # Główna aplikacja
│   │   ├── routers/    # Endpointy (books, quotes, oscars)
│   │   └── schemas/    # Pydantic schemas
│   ├── models/         # Modele danych (Pydantic)
│   ├── pipelines/      # Pipeline'y przetwarzania
│   ├── scrapers/       # Scrapery
│   └── utils/          # Narzędzia pomocnicze
├── tests/              # Testy jednostkowe
└── zadania/            # Zadania do realizacji
```

## Instalacja

```bash
# Klonowanie i setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

## Uruchomienie

### Development (lokalne)

```bash
uvicorn src.api.main:app --reload
```

### Docker Development

```bash
docker compose up --build
```

### Docker Production

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

## Swagger UI (Demo dla klientów)

Po uruchomieniu API, otwórz w przeglądarce:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

Swagger UI posiada wbudowaną funkcję **"Try it out"** - kliknij przycisk, wypełnij parametry i przetestuj API bezpośrednio w przeglądarce.

## Endpointy API

### Books `/api/books`

```bash
# Wszystkie książki (JSON)
curl http://localhost:8000/api/books

# Książki z kategorii mystery (2 strony)
curl "http://localhost:8000/api/books?category=mystery&pages=2"

# Pobranie CSV
curl -o books.csv "http://localhost:8000/api/books?format=csv&pages=1"

# Pobranie Excel
curl -o books.xlsx "http://localhost:8000/api/books?format=excel&pages=1"
```

**Parametry:**
- `category` - kategoria (np. mystery, horror, travel)
- `pages` - liczba stron (1-50, puste = wszystkie)
- `format` - json (domyślny), csv, excel

### Quotes `/api/quotes`

```bash
# Wszystkie cytaty (JSON)
curl http://localhost:8000/api/quotes

# Cytaty z tagiem love (2 strony)
curl "http://localhost:8000/api/quotes?tag=love&pages=2"

# Pobranie CSV
curl -o quotes.csv "http://localhost:8000/api/quotes?format=csv"
```

**Parametry:**
- `tag` - tag do filtrowania (np. love, life, inspirational)
- `pages` - liczba stron (1-50, puste = wszystkie)
- `format` - json (domyślny), csv, excel

### Oscars `/api/oscars`

```bash
# Wszystkie filmy oscarowe (JSON)
curl http://localhost:8000/api/oscars

# Filmy z 2015 roku
curl "http://localhost:8000/api/oscars?year=2015"

# Pobranie Excel
curl -o oscars.xlsx "http://localhost:8000/api/oscars?format=excel"
```

**Parametry:**
- `year` - rok ceremonii (2010-2015)
- `format` - json (domyślny), csv, excel

### Health Check `/health`

```bash
curl http://localhost:8000/health
# {"status": "healthy", "version": "1.0.0"}
```

## Formaty danych

| Format | Content-Type | Opis |
|--------|--------------|------|
| JSON | `application/json` | Domyślny format, dane w JSON |
| CSV | `text/csv` | Plik CSV do pobrania |
| Excel | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` | Plik XLSX do pobrania |

## REST API Standards

API jest zgodne z konwencjami REST:

- **Nazewnictwo zasobów** - rzeczowniki w liczbie mnogiej (`/books`, `/quotes`, `/oscars`)
- **Metody HTTP** - GET dla pobierania danych
- **Kody odpowiedzi:**
  - `200 OK` - sukces
  - `400 Bad Request` - błędne parametry
  - `422 Unprocessable Entity` - błąd walidacji
  - `500 Internal Server Error` - błąd serwera
- **Filtry** - query params (`?category=mystery&pages=2`)

---

## Zasady pracy w projekcie

### 1. Test-Driven Development (TDD)

Stosujemy cykl **Red-Green-Refactor**:

```
1. RED     → Napisz test, który nie przechodzi
2. GREEN   → Napisz minimalny kod, aby test przeszedł
3. REFACTOR → Popraw kod zachowując testy na zielono
```

**Workflow:**

```bash
# 1. Napisz test w tests/
# 2. Uruchom test - musi FAILOWAĆ
pytest tests/test_my_feature.py -v

# 3. Napisz implementację w src/
# 4. Uruchom test - musi PRZECHODZIĆ
pytest tests/test_my_feature.py -v

# 5. Refaktoruj jeśli potrzeba
# 6. Uruchom wszystkie testy
pytest
```

### 2. Docstringi w stylu Google

Każda funkcja i klasa musi mieć docstring w formacie Google:

```python
def fetch_data(url: str, timeout: int = 30) -> dict:
    """Pobiera dane z podanego URL.

    Wykonuje request GET i zwraca sparsowane dane JSON.
    W przypadku błędu połączenia, ponawia próbę 3 razy.

    Args:
        url: Adres URL do pobrania danych.
        timeout: Maksymalny czas oczekiwania w sekundach.

    Returns:
        Słownik z danymi JSON z odpowiedzi.

    Raises:
        RequestError: Gdy nie udało się połączyć po 3 próbach.
        ValueError: Gdy odpowiedź nie jest prawidłowym JSON.

    Example:
        >>> data = fetch_data("https://api.example.com/users")
        >>> print(data["users"])
    """
```

**Szablon dla klas:**

```python
class ProductScraper(BaseScraper):
    """Scraper do pobierania danych produktów.

    Obsługuje paginację i ekstrakcję szczegółów produktów
    z kategorii sklepu.

    Attributes:
        base_url: Bazowy URL sklepu.
        max_pages: Maksymalna liczba stron do przeskanowania.

    Example:
        >>> scraper = ProductScraper(max_pages=10)
        >>> products = scraper.run()
    """
```

### 3. Czystość kodu

#### Nazewnictwo

```python
# Zmienne i funkcje: snake_case
user_name = "John"
def get_user_data():
    pass

# Klasy: PascalCase
class UserScraper:
    pass

# Stałe: UPPER_SNAKE_CASE
MAX_RETRIES = 3
BASE_URL = "https://example.com"

# Prywatne metody: _prefix
def _parse_response(self):
    pass
```

#### Struktura pliku

```python
"""Moduł do scrapowania produktów."""

# 1. Importy standardowe
import json
from pathlib import Path

# 2. Importy zewnętrzne
import requests
from bs4 import BeautifulSoup

# 3. Importy lokalne
from config.settings import BASE_URL
from src.models import Product


# 4. Stałe
DEFAULT_TIMEOUT = 30


# 5. Klasy i funkcje
class Scraper:
    pass
```

#### Zasady

- **Maksymalna długość linii:** 88 znaków
- **Jedna funkcja = jedno zadanie**
- **Maksymalnie 3 poziomy zagnieżdżenia**
- **Unikaj magic numbers** - używaj stałych
- **Type hints** dla argumentów i zwracanych wartości

```python
# Źle
def process(d, n):
    for i in range(n):
        if d[i] > 100:
            d[i] = 100
    return d

# Dobrze
def clamp_values(data: list[int], max_value: int = 100) -> list[int]:
    """Ogranicza wartości w liście do maksymalnej wartości."""
    return [min(value, max_value) for value in data]
```

### 4. Testy

#### Wymagane pokrycie kodu: minimum 80%

```bash
# Sprawdź coverage
pytest --cov=src --cov-report=term-missing --cov-fail-under=80
```

**Kod bez 80% pokrycia testami NIE może być ucommitowany.**

#### Struktura testów

```python
"""Testy dla modułu product_scraper."""

import pytest
from src.scrapers.product_scraper import ProductScraper


class TestProductScraper:
    """Testy klasy ProductScraper."""

    def test_parse_extracts_title(self):
        """Test czy parse wyciąga tytuł produktu."""
        # Arrange
        html = "<div class='product'><h1>Test Product</h1></div>"
        scraper = ProductScraper()

        # Act
        result = scraper.parse(html)

        # Assert
        assert result["title"] == "Test Product"

    def test_parse_handles_missing_title(self):
        """Test czy parse obsługuje brak tytułu."""
        html = "<div class='product'></div>"
        scraper = ProductScraper()

        result = scraper.parse(html)

        assert result["title"] is None
```

#### Nazewnictwo testów

```
test_<co_testujemy>_<scenariusz>_<oczekiwany_rezultat>

test_parse_with_valid_html_returns_product_dict
test_fetch_when_timeout_raises_exception
test_run_with_empty_urls_returns_empty_list
```

#### Uruchamianie testów

```bash
# Wszystkie testy
pytest

# Konkretny plik
pytest tests/test_scraper.py

# Konkretny test
pytest tests/test_scraper.py::TestProductScraper::test_parse_extracts_title

# Z coverage
pytest --cov=src --cov-report=html

# Verbose
pytest -v
```

### 5. Git workflow

```bash
# Przed commitem
pytest                    # Testy muszą przechodzić
ruff check src/ tests/    # Linting (opcjonalnie)

# Commit message format
git commit -m "feat: dodaj scraper produktów"
git commit -m "fix: napraw parsowanie cen"
git commit -m "test: dodaj testy dla ProductScraper"
git commit -m "refactor: wydziel metodę _parse_price"
```

---

## Komendy

| Komenda | Opis |
|---------|------|
| `pytest` | Uruchom testy |
| `pytest -v` | Testy z detalami |
| `pytest --cov=src --cov-fail-under=80` | Testy z coverage (min 80%) |
| `uvicorn src.api.main:app --reload` | Uruchom API (dev) |
| `docker compose up` | Uruchom w Docker (dev) |
| `docker compose -f docker-compose.prod.yml up -d` | Uruchom w Docker (prod) |

## Zmienne środowiskowe

| Zmienna | Opis | Domyślnie |
|---------|------|-----------|
| `DEBUG` | Tryb debug | `False` |
| `LOG_LEVEL` | Poziom logowania | `INFO` |
| `REQUEST_TIMEOUT` | Timeout requestów (s) | `30` |
| `REQUEST_DELAY` | Opóźnienie między requestami (s) | `1.0` |
| `MAX_RETRIES` | Liczba ponowień | `3` |
