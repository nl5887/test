"""Custom exceptions for the application."""

import logging

logger = logging.getLogger(__name__)


class ApplicationError(Exception):
    """Base exception for all application errors."""
    
    def __init__(self, message: str, error_code: str = None):
        """Initialize application error."""
        self.message = message
        self.error_code = error_code or "UNKNOWN"
        logger.error(f"[{self.error_code}] {message}")
        super().__init__(message)


class ValidationError(ApplicationError):
    """Raised when validation fails."""
    
    def __init__(self, message: str):
        """Initialize validation error."""
        super().__init__(message, error_code="VALIDATION_ERROR")


class ConfigurationError(ApplicationError):
    """Raised when configuration is invalid."""
    
    def __init__(self, message: str):
        """Initialize configuration error."""
        super().__init__(message, error_code="CONFIG_ERROR")


class ProcessingError(ApplicationError):
    """Raised when data processing fails."""
    
    def __init__(self, message: str):
        """Initialize processing error."""
        super().__init__(message, error_code="PROCESSING_ERROR")


class CalculationError(ApplicationError):
    """Raised when calculation fails."""
    
    def __init__(self, message: str):
        """Initialize calculation error."""
        super().__init__(message, error_code="CALCULATION_ERROR")

