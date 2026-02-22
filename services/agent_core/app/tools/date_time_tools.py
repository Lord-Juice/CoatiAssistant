from datetime import datetime, timedelta
from langchain.tools import tool

@tool
def get_current_datetime() -> str:
    """Return the current local date and time in ISO format."""
    return datetime.now().isoformat(timespec="minutes")

@tool
def get_current_weekday() -> str:
    """Return the current weekday name."""
    return datetime.now().strftime("%A")

@tool
def add_days_to_now(days: int) -> str:
    """Return ISO datetime for now + given number of days."""
    future = datetime.now() + timedelta(days=days)
    return future.isoformat(timespec="minutes")


@tool
def get_today_range() -> dict:
    """Return today's start and end as ISO datetimes: {'from_iso': ..., 'to_iso': ...}."""
    now = datetime.now()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = now.replace(hour=23, minute=59, second=0, microsecond=0)
    return {
        "from_iso": start.isoformat(timespec="minutes"),
        "to_iso": end.isoformat(timespec="minutes"),
    }

@tool
def get_tomorrow_range() -> dict:
    """Return tomorrow's start and end as ISO datetimes: {'from_iso': ..., 'to_iso': ...}."""
    now = datetime.now() + timedelta(days=1)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = now.replace(hour=23, minute=59, second=0, microsecond=0)
    return {
        "from_iso": start.isoformat(timespec="minutes"),
        "to_iso": end.isoformat(timespec="minutes"),
    }