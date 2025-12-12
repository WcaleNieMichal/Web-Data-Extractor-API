"""Router dla endpointu /api/oscars."""

from enum import Enum
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from src.api.schemas import OscarFilmSchema
from src.scrapers.oscars_scraper import OscarsScraper

router = APIRouter(prefix="/api/oscars", tags=["oscars"])


class OutputFormat(str, Enum):
    """Dostępne formaty wyjścia."""

    json = "json"
    csv = "csv"
    excel = "excel"


@router.get(
    "",
    response_model=list[OscarFilmSchema],
    summary="Pobierz filmy oscarowe",
    description="Pobiera dane o filmach oscarowych z API scrapethissite.com. "
    "Dostępne lata: 2010-2015.",
    responses={
        200: {
            "description": "Lista filmów oscarowych",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "title": "Spotlight",
                            "year": 2015,
                            "awards": 2,
                            "nominations": 6,
                            "best_picture": True,
                        }
                    ]
                },
                "text/csv": {"example": "title,year,awards,nominations,best_picture\n..."},
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {
                    "example": "(plik Excel do pobrania)"
                },
            },
        },
        400: {"description": "Błędne parametry (np. rok poza zakresem 2010-2015)"},
        500: {"description": "Błąd serwera lub scrapera"},
    },
)
async def get_oscars(
    year: Annotated[
        int | None,
        Query(
            description="Rok ceremonii Oscar (2010-2015). Puste = wszystkie lata.",
            ge=2010,
            le=2015,
            examples=[2015, 2014, 2010],
        ),
    ] = None,
    format: Annotated[
        OutputFormat,
        Query(description="Format odpowiedzi: json, csv lub excel"),
    ] = OutputFormat.json,
) -> Response | list[dict]:
    """Pobiera filmy oscarowe z scrapethissite.com.

    Args:
        year: Rok ceremonii (2010-2015, opcjonalne).
        format: Format wyjścia - json, csv lub excel.

    Returns:
        Lista filmów oscarowych w wybranym formacie.

    Raises:
        HTTPException: 400 dla błędnych parametrów, 500 dla błędów scrapera.
    """
    try:
        scraper = OscarsScraper(
            year=year,
            output_format=format.value,
        )
        result = scraper.get()

        if format == OutputFormat.csv:
            return Response(
                content=result,
                media_type="text/csv; charset=utf-8",
                headers={"Content-Disposition": "attachment; filename=oscars.csv"},
            )

        if format == OutputFormat.excel:
            return Response(
                content=result,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": "attachment; filename=oscars.xlsx"},
            )

        # JSON - parsuj string na listę
        import json

        return json.loads(result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd scrapera: {e}") from e
