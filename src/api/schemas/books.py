"""Pydantic schemas for Books API."""

from pydantic import BaseModel, Field


class BookSchema(BaseModel):
    """Schema for a book item."""

    title: str = Field(..., description="Book title")
    price: str = Field(..., description="Price with currency symbol (e.g. £51.77)")
    price_float: float = Field(..., description="Price as number")
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5 stars")
    in_stock: bool = Field(..., description="Whether available in stock")
    url: str = Field(..., description="Relative URL to book page")

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
