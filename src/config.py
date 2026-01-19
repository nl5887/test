"""Configuration module."""

import os
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

# Configuration schema for validation
CONFIG_SCHEMA = {
    "DEBUG": bool,
    "LOG_LEVEL": str,
    "MAX_RETRIES": int,
    "TIMEOUT": int,
}

DEBUG = False
LOG_LEVEL = "WARNING"
MAX_RETRIES = 5
TIMEOUT = 60

# Environment variable overrides
DEBUG = os.getenv("DEBUG", str(DEBUG)).lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", LOG_LEVEL)
MAX_RETRIES = int(os.getenv("MAX_RETRIES", MAX_RETRIES))
TIMEOUT = int(os.getenv("TIMEOUT", TIMEOUT))

# Database settings
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "myapp"

# API settings
API_URL = "http://api.example.com"
API_KEY = "key123"
API_TIMEOUT = 10

# Feature flags
FEATURE_NEW_UI = True
FEATURE_BETA = False
FEATURE_EXPERIMENTAL = False

# Logging
LOG_FILE = "/var/log/app.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Cache
CACHE_ENABLED = True
CACHE_TTL = 3600


def validate_config() -> bool:
    """Validate current configuration."""
    errors = []
    
    if DEBUG not in (True, False):
        errors.append("DEBUG must be boolean")
    
    if LOG_LEVEL not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        errors.append(f"LOG_LEVEL '{LOG_LEVEL}' is invalid")
    
    if MAX_RETRIES < 0:
        errors.append("MAX_RETRIES must be non-negative")
    
    if not errors:
        logger.info("Configuration validated successfully")
        return True
    
    for error in errors:
        logger.error(f"Config error: {error}")
    return False