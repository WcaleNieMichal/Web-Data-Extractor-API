from typing import Any, Callable

from loguru import logger


class DataPipeline:
    """Pipeline for processing scraped data."""

    def __init__(self):
        self.processors: list[Callable] = []

    def add_processor(self, processor: Callable) -> "DataPipeline":
        """Add a processor function to the pipeline."""
        self.processors.append(processor)
        return self

    def process(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Run all processors on the data."""
        result = data
        for processor in self.processors:
            logger.debug(f"Running processor: {processor.__name__}")
            result = processor(result)
        return result
