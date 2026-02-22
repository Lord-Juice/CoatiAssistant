from datetime import datetime, timedelta
from langchain.tools import tool
from typing import List, Dict, Any
from pathlib import Path
from urllib.parse import unquote

# Debug: zeigt dir beim Start exakt, welche Datei importiert wurde
print(f"[calendar_tools] loaded from: {Path(__file__).resolve()}")

def _iso_in(hours: int) -> str:
    return (datetime.now() + timedelta(hours=hours)).isoformat(timespec="minutes")

# Mock Calendar Events
CALENDAR_EVENTS: List[Dict[str, Any]] = [
    {
        "title": "Beispieltermin",
        "start": _iso_in(2),
        "end": _iso_in(3),
        "location": "Home Office",
    }
]

@tool
def calendar_list_events(from_iso: str, to_iso: str) -> str:
    """List calendar events between from_iso and to_iso (inclusive). ISO format: YYYY-MM-DDTHH:MM."""
    try:
        start = datetime.fromisoformat(unquote(from_iso))
        end = datetime.fromisoformat(unquote(to_iso))
    except ValueError:
        return "ERROR: Invalid ISO datetime. Example: 2026-02-12T09:00"

    hits = []
    for ev in CALENDAR_EVENTS:
        ev_start = datetime.fromisoformat(ev["start"])
        if start <= ev_start <= end:
            hits.append(ev)

    if not hits:
        return "No events found"
    
    lines = []
    for ev in hits:
        lines.append(f'- {ev["title"]} | {ev["start"]} → {ev["end"]} | {ev.get("location", "")}')
    return "\n".join(lines)

@tool
def calendar_create_event(title: str, start_iso: str, end_iso: str, location: str = "") -> str:
    """Create a calendar event. Provice start_iso and end_iso in ISO format: YYYY-MM-DDTHH:MM."""
    try:
        datetime.fromisoformat(start_iso)
        datetime.fromisoformat(end_iso)
    except ValueError:
        return "ERROR: Invalid ISO datetime. Example: 2026-02-12T09:00"
    
    CALENDAR_EVENTS.append(
        {"title": title, "start": start_iso, "end": end_iso, "location": location}
    )
    return f"Created event: {title} ({start_iso} → {end_iso}) @ {location}"
