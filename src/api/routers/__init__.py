"""API routers."""

from .books import router as books_router
from .quotes import router as quotes_router
from .oscars import router as oscars_router

__all__ = ["books_router", "quotes_router", "oscars_router"]
