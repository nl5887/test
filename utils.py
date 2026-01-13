"""Utility functions for the application."""

import logging
from typing import List, Dict, Any, Optional

__version__ = "1.0.0"
__all__ = ["DataProcessor", "ErrorHandler", "transform_data", "validate_config", "merge_configs"]
logger = logging.getLogger(__name__)


class DataProcessor:
    """Process and transform data."""
    
    def __init__(self, name: str = "default"):
        """Initialize processor with name."""
        self.name = name
        self.cache = {}
    
    def process(self, items: List[Any]) -> Dict[str, Any]:
        """Process a list of items."""
        if not items:
            logger.warning("Empty items list provided")
            return {"status": "empty", "count": 0}
        
        logger.info(f"Processing {len(items)} items")
        return {
            "status": "success",
            "count": len(items),
            "items": items
        }
    
    def cache_result(self, key: str, value: Any) -> None:
        """Cache a result."""
        self.cache[key] = value
        logger.debug(f"Cached {key}")
    
    def get_cached(self, key: str) -> Optional[Any]:
        """Get cached result."""
        return self.cache.get(key)


class ErrorHandler:
    """Handle various error scenarios."""
    
    def __init__(self, verbose: bool = False):
        """Initialize error handler."""
        self.verbose = verbose
        self.errors = []
    
    def handle_error(self, error: Exception) -> str:
        """Handle an error and return message."""
        self.errors.append(error)
        msg = f"Error: {str(error)}"
        if self.verbose:
            logger.exception("Exception caught")
        return msg
    
    def get_error_count(self) -> int:
        """Get count of errors."""
        return len(self.errors)
    
    def clear_errors(self) -> None:
        """Clear error list."""
        self.errors.clear()


def transform_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform data dictionary."""
    return {k: str(v).upper() for k, v in data.items()}


def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration dictionary."""
    required_keys = {"version", "name", "enabled"}
    return required_keys.issubset(config.keys())


def merge_configs(*configs: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple configuration dictionaries."""
    result = {}
    for config in configs:
        result.update(config)
    return result