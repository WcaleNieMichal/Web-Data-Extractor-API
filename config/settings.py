"""Konfiguracja aplikacji z obsługą środowisk.

Obsługiwane środowiska: dev, test, prod
Ustaw zmienną ENV aby wybrać środowisko.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Określ środowisko
ENV = os.getenv("ENV", "dev")

# Załaduj odpowiedni plik .env
env_file = Path(__file__).resolve().parent.parent / f".env.{ENV}"
if env_file.exists():
    load_dotenv(env_file)
else:
    load_dotenv()  # Fallback do .env

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
LOGS_DIR = BASE_DIR / "logs"

# App settings
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/scraper.db")

# Scraping settings
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", 1.0))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", 5))

# Headers
DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

# Proxy
PROXY_URL = os.getenv("PROXY_URL")

# Environment-specific settings
IS_DEV = ENV == "dev"
IS_TEST = ENV == "test"
IS_PROD = ENV == "prod"
