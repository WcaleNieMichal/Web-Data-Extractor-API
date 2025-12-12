"""Pydantic schemas for Books API."""

from pydantic import BaseModel, Field


class BookSchema(BaseModel):
    """Schema for a book item."""

    title: str = Field(..., description="Tytuł książki")
    price: str = Field(..., description="Cena z symbolem waluty (np. £51.77)")
    price_float: float = Field(..., description="Cena jako liczba")
    rating: int = Field(..., ge=1, le=5, description="Ocena 1-5 gwiazdek")
    in_stock: bool = Field(..., description="Czy dostępna w magazynie")
    url: str = Field(..., description="Relatywny URL do strony książki")

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A Light in the Attic",
                "price": "£51.77",
                "price_float": 51.77,
                "rating": 3,
                "in_stock": True,
                "url": "a-light-in-the-attic_1000/index.html"
            }
        }
    }
