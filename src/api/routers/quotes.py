"""Router for /api/quotes endpoint."""

from enum import Enum
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from src.api.schemas import QuoteSchema
from src.scrapers.quotes_scraper import QuotesScraper

router = APIRouter(prefix="/api/quotes", tags=["quotes"])


class OutputFormat(str, Enum):
    """Available output formats."""

    json = "json"
    csv = "csv"
    excel = "excel"


@router.get(
    "",
    response_model=list[QuoteSchema],
    summary="Get quotes",
    description="Fetches quotes from quotes.toscrape.com. "
    "You can filter by tag and limit number of pages.",
    responses={
        200: {
            "description": "List of quotes",
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
                    "example": "(downloadable Excel file)"
                },
            },
        },
        500: {"description": "Server or scraper error"},
    },
)
async def get_quotes(
    tag: Annotated[
        str | None,
        Query(
            description="Tag to filter by (e.g. love, life, inspirational). "
            "Empty = all quotes.",
            examples=["love", "life", "inspirational", "humor"],
        ),
    ] = None,
    pages: Annotated[
        int | None,
        Query(
            description="Number of pages to fetch. Empty = all pages.",
            ge=1,
            le=50,
            examples=[1, 2, 5],
        ),
    ] = None,
    format: Annotated[
        OutputFormat,
        Query(description="Response format: json, csv or excel"),
    ] = OutputFormat.json,
) -> Response | list[dict]:
    """Fetches quotes from quotes.toscrape.com.

    Args:
        tag: Tag to filter by (optional).
        pages: Number of pages to fetch (optional).
        format: Output format - json, csv or excel.

    Returns:
        List of quotes in selected format.

    Raises:
        HTTPException: 500 for scraper errors.
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

        # JSON - parse string to list
        import json

        return json.loads(result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraper error: {e}") from e
