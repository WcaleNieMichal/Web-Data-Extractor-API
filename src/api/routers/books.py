"""Router for /api/books endpoint."""

from enum import Enum
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from src.api.schemas import BookSchema
from src.scrapers.books_scraper import BooksScraper

router = APIRouter(prefix="/api/books", tags=["books"])


class OutputFormat(str, Enum):
    """Available output formats."""

    json = "json"
    csv = "csv"
    excel = "excel"


@router.get(
    "",
    response_model=list[BookSchema],
    summary="Get books",
    description="Fetches books from books.toscrape.com. "
    "You can filter by category and limit number of pages.",
    responses={
        200: {
            "description": "List of books",
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
                    "example": "(downloadable Excel file)"
                },
            },
        },
        400: {"description": "Invalid parameters (e.g. unknown category)"},
        500: {"description": "Server or scraper error"},
    },
)
async def get_books(
    category: Annotated[
        str | None,
        Query(
            description="Book category (e.g. mystery, horror, travel). "
            "Empty = all books.",
            examples=["mystery", "horror", "travel", "science-fiction"],
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
    """Fetches books from books.toscrape.com.

    Args:
        category: Book category (optional).
        pages: Number of pages to fetch (optional).
        format: Output format - json, csv or excel.

    Returns:
        List of books in selected format.

    Raises:
        HTTPException: 400 for invalid parameters, 500 for scraper errors.
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

        # JSON - parse string to list
        import json

        return json.loads(result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraper error: {e}") from e
