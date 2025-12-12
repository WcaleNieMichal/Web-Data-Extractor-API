from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Item(BaseModel):
    """Base model for scraped items."""

    scraped_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
