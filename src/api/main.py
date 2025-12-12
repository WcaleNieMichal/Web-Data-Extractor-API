"""Main FastAPI application for Web Scrapers API."""

from fastapi import FastAPI

from src.api.routers import books_router, oscars_router, quotes_router

# Tag metadata - links to source websites
tags_metadata = [
    {
        "name": "books",
        "description": "Books from **books.toscrape.com**",
        "externalDocs": {
            "description": "Source website",
            "url": "https://books.toscrape.com",
        },
    },
    {
        "name": "quotes",
        "description": "Quotes from **quotes.toscrape.com**",
        "externalDocs": {
            "description": "Source website",
            "url": "https://quotes.toscrape.com",
        },
    },
    {
        "name": "oscars",
        "description": "Oscar-winning films from **scrapethissite.com**",
        "externalDocs": {
            "description": "Source website",
            "url": "https://www.scrapethissite.com/pages/ajax-javascript/",
        },
    },
    {
        "name": "system",
        "description": "System endpoints (health check)",
    },
]

app = FastAPI(
    title="Web Scrapers API",
    description="""
API for fetching data from various websites.

## Available Scrapers

* **Books** - books from [books.toscrape.com](https://books.toscrape.com)
* **Quotes** - quotes from [quotes.toscrape.com](https://quotes.toscrape.com)
* **Oscars** - Oscar-winning films from [scrapethissite.com](https://www.scrapethissite.com)

## Data Formats

Each endpoint supports three output formats:
- **JSON** (default) - returns data in JSON format
- **CSV** - downloadable CSV file
- **Excel** - downloadable XLSX file

## Usage

Click **"Try it out"** on any endpoint to test the API directly in browser.
    """,
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Register routers
app.include_router(books_router)
app.include_router(quotes_router)
app.include_router(oscars_router)


@app.get("/health", tags=["system"], summary="Health check")
async def health_check() -> dict:
    """Checks if API is running correctly.

    Returns:
        API status and version.
    """
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/", include_in_schema=False)
async def root() -> dict:
    """Redirect to documentation."""
    return {
        "message": "Web Scrapers API",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }
