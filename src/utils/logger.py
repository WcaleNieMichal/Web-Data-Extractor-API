import sys
from loguru import logger

from config.settings import LOG_LEVEL, LOGS_DIR


def setup_logger():
    """Configure loguru logger."""
    logger.remove()

    # Console handler
    logger.add(
        sys.stderr,
        level=LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>",
    )

    # File handler
    logger.add(
        LOGS_DIR / "scraper_{time:YYYY-MM-DD}.log",
        level="DEBUG",
        rotation="1 day",
        retention="7 days",
        compression="gz",
    )

    return logger
