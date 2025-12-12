"""Pydantic schemas for Quotes API."""

from pydantic import BaseModel, Field


class QuoteSchema(BaseModel):
    """Schema for a quote item."""

    text: str = Field(..., description="Treść cytatu")
    author: str = Field(..., description="Autor cytatu")
    author_url: str = Field(..., description="Relatywny URL do strony autora")
    tags: list[str] = Field(..., description="Lista tagów")

    model_config = {
        "json_schema_extra": {
            "example": {
                "text": "The world as we have created it is a process of our thinking.",
                "author": "Albert Einstein",
                "author_url": "/author/Albert-Einstein",
                "tags": ["change", "deep-thoughts", "thinking", "world"]
            }
        }
    }
