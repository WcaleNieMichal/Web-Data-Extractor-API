import json
from pathlib import Path
from typing import Any

import pandas as pd
from loguru import logger

from config.settings import PROCESSED_DATA_DIR


def export_to_json(data: list[dict[str, Any]], filename: str) -> Path:
    """Export data to JSON file."""
    filepath = PROCESSED_DATA_DIR / f"{filename}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    logger.info(f"Exported {len(data)} items to {filepath}")
    return filepath


def export_to_csv(data: list[dict[str, Any]], filename: str) -> Path:
    """Export data to CSV file."""
    filepath = PROCESSED_DATA_DIR / f"{filename}.csv"
    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False, encoding="utf-8")
    logger.info(f"Exported {len(data)} items to {filepath}")
    return filepath
