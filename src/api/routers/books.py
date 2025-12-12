"""Router dla endpointu /api/books."""

from enum import Enum
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from src.api.schemas import BookSchema
from src.scrapers.books_scraper import BooksScraper

router = APIRouter(prefix="/api/books", tags=["books"])


class OutputFormat(str, Enum):
    """Dostępne formaty wyjścia."""

    json = "json"
    csv = "csv"
    excel = "excel"


@router.get(
    "",
    response_model=list[BookSchema],
    summary="Pobierz książki",
    description="Pobiera książki z books.toscrape.com. "
    "Możesz filtrować po kategorii i ograniczyć liczbę stron.",
    responses={
        200: {
            "description": "Lista książek",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "title": "A Light in the Attic",
                            "price": "£51.77",
                            "price_float": 51.77,
                            "rating": 3,
                            "in_stock": True,
                            "url": "a-light-in-the-attic_1000/index.html",
                        }
                    ]
                },
                "text/csv": {"example": "title,price,price_float,rating,in_stock,url\n..."},
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {
                    "example": "(plik Excel do pobrania)"
                },
            },
        },
        400: {"description": "Błędne parametry (np. nieznana kategoria)"},
        500: {"description": "Błąd serwera lub scrapera"},
    },
)
async def get_books(
    category: Annotated[
        str | None,
        Query(
            description="Kategoria książek (np. mystery, horror, travel). "
            "Puste = wszystkie książki.",
            examples=["mystery", "horror", "travel", "science-fiction"],
        ),
    ] = None,
    pages: Annotated[
        int | None,
        Query(
            description="Liczba stron do pobrania. Puste = wszystkie strony.",
            ge=1,
            le=50,
            examples=[1, 2, 5],
        ),
    ] = None,
    format: Annotated[
        OutputFormat,
        Query(description="Format odpowiedzi: json, csv lub excel"),
    ] = OutputFormat.json,
) -> Response | list[dict]:
    """Pobiera książki z books.toscrape.com.

    Args:
        category: Kategoria książek (opcjonalne).
        pages: Liczba stron do pobrania (opcjonalne).
        format: Format wyjścia - json, csv lub excel.

    Returns:
        Lista książek w wybranym formacie.

    Raises:
        HTTPException: 400 dla błędnych parametrów, 500 dla błędów scrapera.
    """
    try:
        scraper = BooksScraper(
            category=category,
            pages=pages,
            output_format=format.value,
        )
        result = scraper.get()

        if format == OutputFormat.csv:
            return Response(
                content=result,
                media_type="text/csv; charset=utf-8",
                headers={"Content-Disposition": "attachment; filename=books.csv"},
            )

        if format == OutputFormat.excel:
            return Response(
                content=result,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": "attachment; filename=books.xlsx"},
            )

        # JSON - parsuj string na listę
        import json

        return json.loads(result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd scrapera: {e}") from e
