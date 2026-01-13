import json
from utils import validate_input, process_data
import logging
from exceptions import ValidationError, CalculationError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Calculator:
    """A simple calculator class for basic operations."""
    
    def __init__(self, name: str):
        """Initialize calculator with a name."""
        if not name or not isinstance(name, str):
            raise ValidationError("Calculator name must be a non-empty string")
        logger.info(f"Initializing Calculator: {name}")
        self.name = name
        self.history = []
    
    def add(self, a: int, b: int) -> int:
        """Add two numbers and store in history."""
        result = a + b
        self.history.append(f"add({a}, {b}) = {result}")
        logger.debug(f"Added: {a} + {b} = {result}")
        return result
    
    def multiply(self, a: int, b: int) -> int:
        """Multiply two numbers."""
        result = a * b
        self.history.append(f"multiply({a}, {b}) = {result}")
        logger.debug(f"Multiplied: {a} * {b} = {result}")
        return result
    
    def get_history(self):
        """Return operation history."""
        if not self.history:
            logger.warning(f"Calculator {self.name}: History is empty")
        return list(self.history)


def calculate_fibonacci(n: int) -> int:
    """Calculate fibonacci number at position n."""
    if n <= 1:
        return n
    return calculate_fibonacci(n - 1) + calculate_fibonacci(n - 2)


def process_data(data: list) -> dict:
    """Process a list of data and return statistics."""
    if not data:
        return {"error": "empty data"}
    
    total = sum(data)
    avg = total / len(data)
    max_val = max(data)
    min_val = min(data)
    
    return {
        "total": total,
        "average": avg,
        "max": max_val,
        "min": min_val
    }


def validate_input(value: int) -> bool:
    """Validate input is a positive integer."""
    if not isinstance(value, int):
        return False
    return value > 0