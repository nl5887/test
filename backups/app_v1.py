import json
from utils import validate_input, process_data


class Calculator:
    """A simple calculator class for basic operations."""
    
    def __init__(self, name: str):
        """Initialize calculator with a name."""
        self.name = name
        self.history = []
    
    def add(self, a: int, b: int) -> int:
        """Add two numbers and store in history."""
        result = a + b
        self.history.append(f"add({a}, {b}) = {result}")
        return result
    
    def multiply(self, a: int, b: int) -> int:
        """Multiply two numbers."""
        result = a * b
        self.history.append(f"multiply({a}, {b}) = {result}")
        return result
    
    def get_history(self):
        """Return operation history."""
        return self.history


def fib_sequence(n: int) -> int:
    """Calculate fibonacci number at position n."""
    if n <= 1:
        return n
    return fib_sequence(n - 1) + fib_sequence(n - 2)


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