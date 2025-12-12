"""Pydantic schemas for Oscars API."""

from pydantic import BaseModel, Field


class OscarFilmSchema(BaseModel):
    """Schema for an Oscar-winning film."""

    title: str = Field(..., description="Tytuł filmu")
    year: int = Field(..., description="Rok ceremonii Oscar")
    awards: int = Field(..., ge=0, description="Liczba zdobytych Oscarów")
    nominations: int = Field(..., ge=0, description="Liczba nominacji")
    best_picture: bool = Field(..., description="Czy zdobył Oscara za najlepszy film")

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
