"""Główna aplikacja FastAPI dla Web Scrapers API."""

from fastapi import FastAPI

from src.api.routers import books_router, oscars_router, quotes_router

# Metadane tagów - linki do stron źródłowych
tags_metadata = [
    {
        "name": "books",
        "description": "Książki z **books.toscrape.com**",
        "externalDocs": {
            "description": "Strona źródłowa",
            "url": "https://books.toscrape.com",
        },
    },
    {
        "name": "quotes",
        "description": "Cytaty z **quotes.toscrape.com**",
        "externalDocs": {
            "description": "Strona źródłowa",
            "url": "https://quotes.toscrape.com",
        },
    },
    {
        "name": "oscars",
        "description": "Filmy oscarowe z **scrapethissite.com**",
        "externalDocs": {
            "description": "Strona źródłowa",
            "url": "https://www.scrapethissite.com/pages/ajax-javascript/",
        },
    },
    {
        "name": "system",
        "description": "Endpointy systemowe (health check)",
    },
]

app = FastAPI(
    title="Web Scrapers API",
    description="""
API do pobierania danych z różnych stron internetowych.

## Dostępne scrapery

* **Books** - książki z [books.toscrape.com](https://books.toscrape.com)
* **Quotes** - cytaty z [quotes.toscrape.com](https://quotes.toscrape.com)
* **Oscars** - filmy oscarowe z [scrapethissite.com](https://www.scrapethissite.com)

## Formaty danych

Każdy endpoint obsługuje trzy formaty wyjścia:
- **JSON** (domyślny) - zwraca dane w formacie JSON
- **CSV** - pobieranie pliku CSV
- **Excel** - pobieranie pliku XLSX

## Użycie

Kliknij **"Try it out"** przy każdym endpoincie, aby przetestować API bezpośrednio w przeglądarce.
    """,
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Rejestracja routerów
app.include_router(books_router)
app.include_router(quotes_router)
app.include_router(oscars_router)


@app.get("/health", tags=["system"], summary="Health check")
async def health_check() -> dict:
    """Sprawdza czy API działa poprawnie.

    Returns:
        Status i wersja API.
    """
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/", include_in_schema=False)
async def root() -> dict:
    """Przekierowanie do dokumentacji."""
    return {
        "message": "Web Scrapers API",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }
