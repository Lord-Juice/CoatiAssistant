from __future__ import annotations
from langchain.tools import tool

from typing import Any, Dict, Optional

from .store import MemoryStore, read_fact_with_history

STORE = MemoryStore("../../../data/memory.json")


# ---- Tool: remember ----
@tool
def remember(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Expected payload examples:
    {
      "entity": "wallet",
      "entity_type": "item",
      "slot": "location.current",
      "value": "kitchen shelf",
      "source_utterance": "Remember for me that I put my wallet on the kitchen shelf",
      "confidence": 0.9
    }
    """
    return STORE.upsert_fact(
        entity_raw=payload["entity"],
        entity_type=payload.get("entity_type", "unknown"),
        slot=payload.get("slot", "note.current"),
        value=payload.get("value"),
        source_utterance=payload.get("source_utterance", ""),
        confidence=float(payload.get("confidence", 1.0)),
        source=payload.get("source", "user"),
    )


# ---- Tool: recall ----
@tool
def recall(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Retrieves a stored memory fact for an entity.

    Expected payload:
    {
      "entity": "wallet",
      "slot": "location.current"
    }

    Returns the current value and optionally location candidates for the entity.
    """
    entity = payload["entity"]
    slot = payload.get("slot", "note.current")

    # wenn du die neue Methode eingebaut hast:
    value, history, meta = read_fact_with_history(entity_raw=entity, slot=slot)

    if meta["status"] == "ok":
        if slot == "location.current":
            candidates = _location_candidates(value, history, limit=3)
            return {
                "status": "ok",
                "key": meta["key"],
                "value": value,
                "candidates": candidates,
            }
        return {"status": "ok", "key": meta["key"], "value": value}


# ---- Tool: memory_index ----
@tool
def memory_index(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """
    Returns a structured index of all stored memory entities.

    Use this tool when:
    - You are unsure which entity key exists.
    - You need to check whether an entity is already stored.
    - You want to inspect available slots for an entity.
    - You must avoid guessing memory keys.

    The response contains:
    - key: the canonical memory key (e.g. "entity:wallet")
    - entity: canonical entity name
    - aliases: alternative names for the entity
    - slots: list of stored slots (e.g. "location.current")

    Important:
    Never invent memory keys. Always call this tool first if the entity
    or slot is uncertain.
    """
    return {"status": "ok", "index": STORE.memory_index()}


def _location_candidates(current, history, limit=3):
    seen = set()
    out = []

    # history ist chronologisch -> wir gehen rückwärts (neueste zuerst)
    for h in reversed(history or []):
        v = h.get("value")
        if not v:
            continue
        # keine Wiederholung des aktuellen Ortes und keine Duplikate
        if v == current:
            continue
        if v in seen:
            continue
        seen.add(v)
        out.append(v)
        if len(out) >= limit:
            break

    return out