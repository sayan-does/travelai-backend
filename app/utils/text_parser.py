import re
from datetime import datetime


def extract_time(text: str) -> str:
    """Extract time from text using regex."""
    time_pattern = r'\b(?:1[0-2]|0?[1-9])(?::[0-5][0-9])?\s*(?:AM|PM|am|pm)\b'
    match = re.search(time_pattern, text)
    return match.group(0) if match else "09:00 AM"


def extract_cost(text: str) -> float:
    """Extract cost from text using regex."""
    cost_pattern = r'\$\s*(\d+(?:\.\d{2})?)'
    match = re.search(cost_pattern, text)
    return float(match.group(1)) if match else 0.0
