# Web Scrapers API

REST API for fetching data from various websites. Project follows REST API conventions.

## Available Scrapers

- **Books** - books from [books.toscrape.com](https://books.toscrape.com)
- **Quotes** - quotes from [quotes.toscrape.com](https://quotes.toscrape.com)
- **Oscars** - Oscar-winning films from [scrapethissite.com](https://www.scrapethissite.com/pages/ajax-javascript/)

## Project Structure

```
├── config/             # Application configuration
├── data/
│   ├── raw/            # Raw scraped data
│   └── processed/      # Processed data
├── logs/               # Application logs
├── src/
│   ├── api/            # FastAPI REST API
│   │   ├── main.py     # Main application
│   │   ├── routers/    # Endpoints (books, quotes, oscars)
│   │   └── schemas/    # Pydantic schemas
│   ├── models/         # Data models (Pydantic)
│   ├── pipelines/      # Data processing pipelines
│   ├── scrapers/       # Scrapers
│   └── utils/          # Utility functions
├── tests/              # Unit tests
└── zadania/            # Tasks to implement
```

## Installation

```bash
# Clone and setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

## Running

### Development (local)

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

## Swagger UI (Client Demo)

After starting the API, open in browser:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

Swagger UI has built-in **"Try it out"** feature - click the button, fill in parameters and test the API directly in browser.

## API Endpoints

### Books `/api/books`

```bash
# All books (JSON)
curl http://localhost:8000/api/books

# Books from mystery category (2 pages)
curl "http://localhost:8000/api/books?category=mystery&pages=2"

# Download CSV
curl -o books.csv "http://localhost:8000/api/books?format=csv&pages=1"

# Download Excel
curl -o books.xlsx "http://localhost:8000/api/books?format=excel&pages=1"
```

**Parameters:**
- `category` - category (e.g. mystery, horror, travel)
- `pages` - number of pages (1-50, empty = all)
- `format` - json (default), csv, excel

### Quotes `/api/quotes`

```bash
# All quotes (JSON)
curl http://localhost:8000/api/quotes

# Quotes with tag love (2 pages)
curl "http://localhost:8000/api/quotes?tag=love&pages=2"

# Download CSV
curl -o quotes.csv "http://localhost:8000/api/quotes?format=csv"
```

**Parameters:**
- `tag` - tag to filter (e.g. love, life, inspirational)
- `pages` - number of pages (1-50, empty = all)
- `format` - json (default), csv, excel

### Oscars `/api/oscars`

```bash
# All Oscar-winning films (JSON)
curl http://localhost:8000/api/oscars

# Films from 2015
curl "http://localhost:8000/api/oscars?year=2015"

# Download Excel
curl -o oscars.xlsx "http://localhost:8000/api/oscars?format=excel"
```

**Parameters:**
- `year` - ceremony year (2010-2015)
- `format` - json (default), csv, excel

### Health Check `/health`

```bash
curl http://localhost:8000/health
# {"status": "healthy", "version": "1.0.0"}
```

## Data Formats

| Format | Content-Type | Description |
|--------|--------------|-------------|
| JSON | `application/json` | Default format, JSON data |
| CSV | `text/csv` | Downloadable CSV file |
| Excel | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` | Downloadable XLSX file |

## REST API Standards

API follows REST conventions:

- **Resource naming** - plural nouns (`/books`, `/quotes`, `/oscars`)
- **HTTP methods** - GET for fetching data
- **Response codes:**
  - `200 OK` - success
  - `400 Bad Request` - invalid parameters
  - `422 Unprocessable Entity` - validation error
  - `500 Internal Server Error` - server error
- **Filters** - query params (`?category=mystery&pages=2`)

---

## Project Guidelines

### 1. Test-Driven Development (TDD)

We follow the **Red-Green-Refactor** cycle:

```
1. RED     → Write a failing test
2. GREEN   → Write minimal code to pass the test
3. REFACTOR → Improve code while keeping tests green
```

**Workflow:**

```bash
# 1. Write test in tests/
# 2. Run test - must FAIL
pytest tests/test_my_feature.py -v

# 3. Write implementation in src/
# 4. Run test - must PASS
pytest tests/test_my_feature.py -v

# 5. Refactor if needed
# 6. Run all tests
pytest
```

### 2. Google-style Docstrings

Every function and class must have a Google-style docstring:

```python
def fetch_data(url: str, timeout: int = 30) -> dict:
    """Fetches data from the given URL.

    Performs a GET request and returns parsed JSON data.
    Retries 3 times on connection error.

    Args:
        url: URL to fetch data from.
        timeout: Maximum wait time in seconds.

    Returns:
        Dictionary with JSON data from response.

    Raises:
        RequestError: When connection fails after 3 retries.
        ValueError: When response is not valid JSON.

    Example:
        >>> data = fetch_data("https://api.example.com/users")
        >>> print(data["users"])
    """
```

**Class template:**

```python
class ProductScraper(BaseScraper):
    """Scraper for fetching product data.

    Handles pagination and product detail extraction
    from store categories.

    Attributes:
        base_url: Base URL of the store.
        max_pages: Maximum number of pages to scan.

    Example:
        >>> scraper = ProductScraper(max_pages=10)
        >>> products = scraper.run()
    """
```

### 3. Code Quality

#### Naming Conventions

```python
# Variables and functions: snake_case
user_name = "John"
def get_user_data():
    pass

# Classes: PascalCase
class UserScraper:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
BASE_URL = "https://example.com"

# Private methods: _prefix
def _parse_response(self):
    pass
```

#### File Structure

```python
"""Module for product scraping."""

# 1. Standard library imports
import json
from pathlib import Path

# 2. Third-party imports
import requests
from bs4 import BeautifulSoup

# 3. Local imports
from config.settings import BASE_URL
from src.models import Product


# 4. Constants
DEFAULT_TIMEOUT = 30


# 5. Classes and functions
class Scraper:
    pass
```

#### Guidelines

- **Maximum line length:** 88 characters
- **One function = one task**
- **Maximum 3 levels of nesting**
- **Avoid magic numbers** - use constants
- **Type hints** for arguments and return values

```python
# Bad
def process(d, n):
    for i in range(n):
        if d[i] > 100:
            d[i] = 100
    return d

# Good
def clamp_values(data: list[int], max_value: int = 100) -> list[int]:
    """Clamps values in list to maximum value."""
    return [min(value, max_value) for value in data]
```

### 4. Testing

#### Required code coverage: minimum 80%

```bash
# Check coverage
pytest --cov=src --cov-report=term-missing --cov-fail-under=80
```

**Code without 80% test coverage CANNOT be committed.**

#### Test Structure

```python
"""Tests for product_scraper module."""

import pytest
from src.scrapers.product_scraper import ProductScraper


class TestProductScraper:
    """Tests for ProductScraper class."""

    def test_parse_extracts_title(self):
        """Test that parse extracts product title."""
        # Arrange
        html = "<div class='product'><h1>Test Product</h1></div>"
        scraper = ProductScraper()

        # Act
        result = scraper.parse(html)

        # Assert
        assert result["title"] == "Test Product"

    def test_parse_handles_missing_title(self):
        """Test that parse handles missing title."""
        html = "<div class='product'></div>"
        scraper = ProductScraper()

        result = scraper.parse(html)

        assert result["title"] is None
```

#### Test Naming

```
test_<what_we_test>_<scenario>_<expected_result>

test_parse_with_valid_html_returns_product_dict
test_fetch_when_timeout_raises_exception
test_run_with_empty_urls_returns_empty_list
```

#### Running Tests

```bash
# All tests
pytest

# Specific file
pytest tests/test_scraper.py

# Specific test
pytest tests/test_scraper.py::TestProductScraper::test_parse_extracts_title

# With coverage
pytest --cov=src --cov-report=html

# Verbose
pytest -v
```

### 5. Git Workflow

```bash
# Before commit
pytest                    # Tests must pass
ruff check src/ tests/    # Linting (optional)

# Commit message format
git commit -m "feat: add product scraper"
git commit -m "fix: fix price parsing"
git commit -m "test: add tests for ProductScraper"
git commit -m "refactor: extract _parse_price method"
```

---

## Commands

| Command | Description |
|---------|-------------|
| `pytest` | Run tests |
| `pytest -v` | Run tests with details |
| `pytest --cov=src --cov-fail-under=80` | Tests with coverage (min 80%) |
| `uvicorn src.api.main:app --reload` | Run API (dev) |
| `docker compose up` | Run in Docker (dev) |
| `docker compose -f docker-compose.prod.yml up -d` | Run in Docker (prod) |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Debug mode | `False` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `REQUEST_TIMEOUT` | Request timeout (s) | `30` |
| `REQUEST_DELAY` | Delay between requests (s) | `1.0` |
| `MAX_RETRIES` | Number of retries | `3` |
