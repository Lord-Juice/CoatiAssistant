import json
from pathlib import Path
from typing import Dict

from langchain.tools import tool

# agent_core/ ist: app/.. (also parent von app)
BASE_DIR = Path(__file__).resolve().parents[2]  # .../services/agent_core
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

MEMORY_FILE = DATA_DIR / "memory.json"


def load_memory() -> Dict[str, str]:
    if not MEMORY_FILE.exists():
        return {}
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Defensive: nur dict akzeptieren
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_memory(memory: Dict[str, str]) -> None:
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=4, ensure_ascii=False)


# Globaler Store (geladen beim Import)
MEMORY_STORE: Dict[str, str] = load_memory()


@tool
def remember(key: str, value: str) -> str:
    """Store a key-value memory entry persistently (written to JSON)."""
    MEMORY_STORE[key] = value
    save_memory(MEMORY_STORE)
    return f"Stored memory: {key}"


@tool
def recall(key: str) -> str:
    """Retrieve a stored memory entry by key."""
    return MEMORY_STORE.get(key, "No memory found.")


@tool
def clear_memory() -> str:
    """Delete all stored memory entries."""
    MEMORY_STORE.clear()
    save_memory(MEMORY_STORE)
    return "All memory cleared."