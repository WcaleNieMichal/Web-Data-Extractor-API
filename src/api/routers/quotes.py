"""Router dla endpointu /api/quotes."""

from enum import Enum
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from src.api.schemas import QuoteSchema
from src.scrapers.quotes_scraper import QuotesScraper

router = APIRouter(prefix="/api/quotes", tags=["quotes"])


class OutputFormat(str, Enum):
    """Dostępne formaty wyjścia."""

    json = "json"
    csv = "csv"
    excel = "excel"


@router.get(
    "",
    response_model=list[QuoteSchema],
    summary="Pobierz cytaty",
    description="Pobiera cytaty z quotes.toscrape.com. "
    "Możesz filtrować po tagu i ograniczyć liczbę stron.",
    responses={
        200: {
            "description": "Lista cytatów",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "text": "The world as we have created it is a process of our thinking.",
                            "author": "Albert Einstein",
                            "author_url": "/author/Albert-Einstein",
                            "tags": ["change", "deep-thoughts", "thinking", "world"],
                        }
                    ]
                },
                "text/csv": {"example": "text,author,author_url,tags\n..."},
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {
                    "example": "(plik Excel do pobrania)"
                },
            },
        },
        500: {"description": "Błąd serwera lub scrapera"},
    },
)
async def get_quotes(
    tag: Annotated[
        str | None,
        Query(
            description="Tag do filtrowania (np. love, life, inspirational). "
            "Puste = wszystkie cytaty.",
            examples=["love", "life", "inspirational", "humor"],
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
    """Pobiera cytaty z quotes.toscrape.com.

    Args:
        tag: Tag do filtrowania (opcjonalne).
        pages: Liczba stron do pobrania (opcjonalne).
        format: Format wyjścia - json, csv lub excel.

    Returns:
        Lista cytatów w wybranym formacie.

    Raises:
        HTTPException: 500 dla błędów scrapera.
    """
    try:
        scraper = QuotesScraper(
            tag=tag,
            pages=pages,
            output_format=format.value,
        )
        result = scraper.get()

        if format == OutputFormat.csv:
            return Response(
                content=result,
                media_type="text/csv; charset=utf-8",
                headers={"Content-Disposition": "attachment; filename=quotes.csv"},
            )

        if format == OutputFormat.excel:
            return Response(
                content=result,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": "attachment; filename=quotes.xlsx"},
            )

        # JSON - parsuj string na listę
        import json

        return json.loads(result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd scrapera: {e}") from e
