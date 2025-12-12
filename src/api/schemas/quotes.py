"""Pydantic schemas for Quotes API."""

from pydantic import BaseModel, Field


class QuoteSchema(BaseModel):
    """Schema for a quote item."""

    text: str = Field(..., description="Quote text")
    author: str = Field(..., description="Quote author")
    author_url: str = Field(..., description="Relative URL to author page")
    tags: list[str] = Field(..., description="List of tags")

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
