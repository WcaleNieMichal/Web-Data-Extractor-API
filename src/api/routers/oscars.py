"""Router for /api/oscars endpoint."""

from enum import Enum
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from src.api.schemas import OscarFilmSchema
from src.scrapers.oscars_scraper import OscarsScraper

router = APIRouter(prefix="/api/oscars", tags=["oscars"])


class OutputFormat(str, Enum):
    """Available output formats."""

    json = "json"
    csv = "csv"
    excel = "excel"


@router.get(
    "",
    response_model=list[OscarFilmSchema],
    summary="Get Oscar-winning films",
    description="Fetches Oscar-winning film data from scrapethissite.com API. "
    "Available years: 2010-2015.",
    responses={
        200: {
            "description": "List of Oscar-winning films",
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
                    "example": "(downloadable Excel file)"
                },
            },
        },
        400: {"description": "Invalid parameters (e.g. year outside 2010-2015 range)"},
        500: {"description": "Server or scraper error"},
    },
)
async def get_oscars(
    year: Annotated[
        int | None,
        Query(
            description="Oscar ceremony year (2010-2015). Empty = all years.",
            ge=2010,
            le=2015,
            examples=[2015, 2014, 2010],
        ),
    ] = None,
    format: Annotated[
        OutputFormat,
        Query(description="Response format: json, csv or excel"),
    ] = OutputFormat.json,
) -> Response | list[dict]:
    """Fetches Oscar-winning films from scrapethissite.com.

    Args:
        year: Ceremony year (2010-2015, optional).
        format: Output format - json, csv or excel.

    Returns:
        List of Oscar-winning films in selected format.

    Raises:
        HTTPException: 400 for invalid parameters, 500 for scraper errors.
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

        # JSON - parse string to list
        import json

        return json.loads(result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraper error: {e}") from e
