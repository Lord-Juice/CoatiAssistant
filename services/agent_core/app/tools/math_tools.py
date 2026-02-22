import random
import uuid
from langchain.tools import tool

@tool
def calculate(expression: str) -> str:
    """Safely evaluate a simple math expression (e.g., '2+2*5')."""
    try:
        result = eval(expression, {"__builtins__": {}})
        return str(result)
    except Exception:
        return "ERROR: Invalid expression"

@tool
def random_number(min_value: int, max_value: int) -> str:
    """Return a random integer between min_value and max_value."""
    return str(random.randint(min_value, max_value))

@tool
def generate_uuid() -> str:
    """Generate a random UUID string."""
    return str(uuid.uuid4())