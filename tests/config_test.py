"""Configuration module."""

DEBUG = True
LOG_LEVEL = "INFO"
MAX_RETRIES = 3
TIMEOUT = 30

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