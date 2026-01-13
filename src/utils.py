"""Utility functions for the application."""

import logging
from functools import wraps
from typing import List, Dict, Any, Optional

__version__ = "1.0.0"
__author__ = "Logan Test Suite"
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
        
        if not isinstance(items, list):
            raise TypeError(f"Expected list, got {type(items).__name__}")
        
        logger.info(f"Processing {len(items)} items")
        return {
            "status": "success",
            "count": len(items),
            "items": items
        }
    
    
    def get_cached(self, key: str) -> Optional[Any]:
        """Get cached result."""
        return self.cache.get(key)




def transform_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform data dictionary."""
    return {k: str(v).upper() for k, v in data.items()}


def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration dictionary."""
    if not isinstance(config, dict):
        logger.error(f"Config must be dict, got {type(config).__name__}")
        return False
    
    required_keys = {"version", "name", "enabled"}
    is_valid = required_keys.issubset(config.keys())
    
    if not is_valid:
        missing = required_keys - set(config.keys())
        logger.warning(f"Missing required config keys: {missing}")
    
    return is_valid


def merge_configs(*configs: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple configuration dictionaries."""
    if not configs:
        logger.warning("No configurations provided to merge")
    result = {}
    for config in configs:
        if not isinstance(config, dict):
            logger.warning(f"Skipping non-dict config: {type(config).__name__}")
            continue
        result.update(config)
    logger.info(f"Merged {len(configs)} configurations")
    return result