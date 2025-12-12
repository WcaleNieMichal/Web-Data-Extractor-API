"""Pydantic schemas for API responses."""

from .books import BookSchema
from .quotes import QuoteSchema
from .oscars import OscarFilmSchema

__all__ = ["BookSchema", "QuoteSchema", "OscarFilmSchema"]
