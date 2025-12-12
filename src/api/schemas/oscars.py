"""Pydantic schemas for Oscars API."""

from pydantic import BaseModel, Field


class OscarFilmSchema(BaseModel):
    """Schema for an Oscar-winning film."""

    title: str = Field(..., description="Film title")
    year: int = Field(..., description="Oscar ceremony year")
    awards: int = Field(..., ge=0, description="Number of awards won")
    nominations: int = Field(..., ge=0, description="Number of nominations")
    best_picture: bool = Field(..., description="Whether won Best Picture")

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Spotlight",
                "year": 2015,
                "awards": 2,
                "nominations": 6,
                "best_picture": True
            }
        }
    }
