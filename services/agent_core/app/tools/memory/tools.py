from __future__ import annotations
from langchain.tools import tool

from typing import Any, Dict, Optional

from .store import MemoryStore

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
    Expected payload:
    { "entity": "wallet", "slot": "location.current" }
    """
    value, meta = STORE.read_fact(entity_raw=payload["entity"], slot=payload.get("slot", "note.current"))
    if meta["status"] == "ok":
        return {"status": "ok", "key": meta["key"], "value": value}

    # unified "You didn't tell me before" behavior
    if meta.get("reason") == "slot_not_found":
        return {
            "status": "not_found",
            "key": meta.get("key"),
            "message": "Diese Information hast du mir zuvor nicht gesagt.",
        }

    return {
        "status": "not_found",
        "message": "Dazu habe ich noch keine gespeicherte Erinnerung.",
    }


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